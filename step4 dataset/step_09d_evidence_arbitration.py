"""
step_09d_evidence_arbitration.py  -  STEP 9d: Trust-Weighted Evidence Arbitration
=================================================================================

Replaces the Step 9 generator on the knowledge-corruption path. It combines three
ideas already present in this pipeline (isolate-then-aggregate, parametric
knowledge-conflict, adaptive risk) into one decision rule:

  1. Internal knowledge   p   : closed-book short answer (or UNKNOWN).
  2. Isolated evidence    a_i : one short answer per surviving passage, generated
                                in isolation (Step 9A prompt) so no passage can
                                steer the reading of another.
  3. Trust-weighted, sybil-resistant vote. Answers are clustered by normalised
     containment. A passage votes with weight t_i = 1 - r_i (Step 6b poison risk);
     passages Step 6b marked as one coordinated group count as ONE witness
     (weight = max t_i in the group). Internal knowledge votes with weight 1.
  4. Corroboration rule (the security invariant):
       accept cluster B  iff  B holds >= 2 independent witnesses
                              (internal knowledge counts as one)
       else if internal knowledge is known  -> answer from internal knowledge
            (an uncorroborated external claim that contradicts the model's own
             knowledge is exactly the single-poison case)
       else if exactly one external witness -> accept it but mark the answer
            as uncorroborated (disagreement 0.5 => Step 10 raises its threshold)
       else abstain.
  5. The winning answer is written in a short sentence; the evidence Step 10
     grounds against is the surviving passages PLUS the internal-knowledge
     statement when it was a witness for the answer (grounding feedback loop).

Cost: 1 + |passages| short generations (<= 6 with k=5), all on one backbone.
"""
from __future__ import annotations

import re

from pipeline_common import PipelineState
from step_09a_isolate_aggregate import _PER_PASSAGE_PROMPT, _is_abstention, _normalize

_PARAMETRIC_PROMPT = (
    "Answer the question from your own knowledge. Reply with ONE short phrase or "
    "single value - no explanation. If you do not know, reply exactly \"UNKNOWN\".\n\n"
    "QUESTION: {question}\n\nShort answer:")

# v2.1 "reasoned" internal knowledge: let the model state what it knows first
# (TrustRAG's internal-knowledge prompt, verbatim), then extract the short answer
# from that statement. The terse closed-book prompt above under-uses the model's
# knowledge (abstains / drops details) when Step 6b has removed every passage.
_KNOWLEDGE_PROMPT = (
    "Generate a concise text that provides accurate and relevant information to answer the given "
    "question [{question}?] If the information is unclear or uncertain, explicitly state 'I don't know' "
    "to avoid any hallucinations. Please less than 50 words!")
_EXTRACT_PROMPT = (
    "Using ONLY the text below, answer the question with ONE short phrase or single value, keeping "
    "all details the text gives (full dates, units, full names). If the text does not answer it or "
    "says it does not know, reply exactly \"UNKNOWN\".\n\nTEXT:\n{knowledge}\n\n"
    "QUESTION: {question}\n\nShort answer:")

_BACKBONE = "llama3.1:8b"


class OllamaArbiter:
    def __init__(self, model: str = _BACKBONE, base_url: str = "http://localhost:11434",
                 parametric_mode: str = "terse"):
        from langchain_ollama import ChatOllama
        self._llm = ChatOllama(model=model, base_url=base_url, temperature=0.0, seed=0,
                               num_predict=48, num_ctx=4096)
        self._long = ChatOllama(model=model, base_url=base_url, temperature=0.0, seed=0,
                                num_predict=160, num_ctx=4096)
        self.parametric_mode = parametric_mode      # "terse" (v2) | "reasoned" (v2.1)
        self.last_knowledge = ""

    def ask(self, prompt: str) -> str:
        out = self._llm.invoke(prompt)
        return (getattr(out, "content", str(out)) or "").strip().split("\n")[0].strip()

    def parametric(self, question: str) -> str:
        if self.parametric_mode != "reasoned":
            self.last_knowledge = ""
            return self.ask(_PARAMETRIC_PROMPT.format(question=question))
        out = self._long.invoke(_KNOWLEDGE_PROMPT.format(question=question))
        self.last_knowledge = (getattr(out, "content", str(out)) or "").strip()
        if not self.last_knowledge or "don't know" in self.last_knowledge.lower():
            return "UNKNOWN"
        return self.ask(_EXTRACT_PROMPT.format(knowledge=self.last_knowledge, question=question))

    def per_passage(self, question: str, passage: str) -> str:
        return self.ask(_PER_PASSAGE_PROMPT.format(passage=passage, question=question))


def _clean(ans: str) -> str:
    a = re.sub(r"^\s*(short answer|answer)\s*:\s*", "", ans or "", flags=re.I).strip().strip('"').strip()
    return a.rstrip(".").strip()


def _unknown(ans: str) -> bool:
    return (not ans) or "unknown" in ans.lower() or _is_abstention(ans)


def _same(a: str, b: str) -> bool:
    na, nb = _normalize(a), _normalize(b)
    if not na or not nb:
        return False
    ta, tb = set(na.split()), set(nb.split())
    if na == nb or ta <= tb or tb <= ta:
        return True
    inter = len(ta & tb)
    if not inter:
        return False
    p, r = inter / len(tb), inter / len(ta)
    return 2 * p * r / (p + r) >= 0.6


def arbitrate(parametric: str, per_passage: list[tuple[str, float, int]]) -> dict:
    """per_passage: [(answer, trust, group_id)]. Returns the decision record."""
    clusters: list[dict] = []

    def add(ans, weight, source, group):
        for c in clusters:
            if _same(ans, c["rep"]):
                c["members"].append((source, weight, group, ans))
                return
        clusters.append({"rep": ans, "members": [(source, weight, group, ans)]})

    p_known = not _unknown(parametric)
    if p_known:
        add(parametric, 1.0, "internal", "internal")
    for i, (a, t, g) in enumerate(per_passage):
        if not _unknown(a):
            add(a, t, f"passage{i}", f"g{g}")

    for c in clusters:
        best_per_group: dict = {}
        for src, w, g, _ in c["members"]:
            best_per_group[g] = max(best_per_group.get(g, 0.0), w)
        c["witnesses"] = len(best_per_group)
        c["weight"] = round(sum(best_per_group.values()), 4)
        c["has_internal"] = "internal" in best_per_group
        c["n_external"] = sum(1 for g in best_per_group if g != "internal")
        # prefer an external phrasing (grounds better) when one agrees
        ext = [m for m in c["members"] if m[0] != "internal"]
        c["answer"] = ext[0][3] if ext else c["rep"]
    clusters.sort(key=lambda c: (c["witnesses"], c["weight"]), reverse=True)
    total = sum(c["weight"] for c in clusters) or 1.0

    if clusters and clusters[0]["witnesses"] >= 2:
        best = clusters[0]
        return {"decision": "corroborated", "answer": best["answer"], "cluster": best,
                "disagreement": round(1 - best["weight"] / total, 4), "clusters": clusters,
                "uses_internal": best["has_internal"]}
    if p_known:
        best = next(c for c in clusters if c["has_internal"])
        conflict = any(not c["has_internal"] for c in clusters)
        return {"decision": "internal_over_uncorroborated" if conflict else "internal_only",
                "answer": best["answer"], "cluster": best,
                "disagreement": 0.5 if conflict else 0.0, "clusters": clusters,
                "uses_internal": True}
    ext = [c for c in clusters if c["n_external"] >= 1]
    if len(ext) == 1:
        return {"decision": "single_external_uncorroborated", "answer": ext[0]["answer"],
                "cluster": ext[0], "disagreement": 0.5, "clusters": clusters, "uses_internal": False}
    if len(ext) > 1:
        best = max(ext, key=lambda c: c["weight"])
        return {"decision": "external_plurality_uncorroborated", "answer": best["answer"],
                "cluster": best, "disagreement": round(1 - best["weight"] / total, 4),
                "clusters": clusters, "uses_internal": False}
    return {"decision": "abstain", "answer": None, "cluster": None, "disagreement": 0.0,
            "clusters": clusters, "uses_internal": False}


def run(state: PipelineState, arbiter: OllamaArbiter | None = None) -> PipelineState:
    if state.blocked:
        return state
    arbiter = arbiter or OllamaArbiter()
    question = state.prompt
    passages = list(state.ranked_context or [])
    trust = state.meta.get("passage_trust", {})
    group = state.meta.get("passage_group", {})

    parametric = _clean(arbiter.parametric(question))
    knowledge = getattr(arbiter, "last_knowledge", "") or ""
    per = []
    for i, p in enumerate(passages):
        try:
            a = _clean(arbiter.per_passage(question, p))
        except Exception as e:
            a = f"INSUFFICIENT (error: {type(e).__name__})"
        per.append((a, float(trust.get(p, 1.0)), int(group.get(p, 1000 + i))))

    d = arbitrate(parametric, per)
    state.meta["arbitration"] = {
        "parametric": parametric,
        "internal_knowledge": knowledge,
        "per_passage": [a for a, _, _ in per],
        "trust": [t for _, t, _ in per],
        "group": [g for _, _, g in per],
        "decision": d["decision"],
        "clusters": [{k: c[k] for k in ("rep", "witnesses", "weight", "has_internal")}
                     for c in d["clusters"]],
    }
    state.scores["disagreement"] = d["disagreement"]
    state.scores["ensemble_disagreement"] = d["disagreement"]
    if d["answer"] is None:
        state.meta["answer"] = ""
        state.meta["abstention_message"] = (
            "The available sources do not provide a trustworthy answer to this question.")
        state.abstain("step_09d_evidence_arbitration", "no trustworthy witness")
        return state
    answer = d["answer"]
    state.output = answer
    state.meta["answer"] = answer
    if d["uses_internal"]:
        # grounding feedback loop: internal knowledge is a declared evidence source
        state.meta["grounding_evidence_extra"] = [f"{question} {parametric}"] + ([knowledge] if knowledge else [])
        if knowledge and d["decision"] in ("internal_only", "internal_over_uncorroborated"):
            # answer + the witness statement it rests on (TrustRAG likewise answers in prose)
            answer = f"{answer}. {knowledge}"
    state.log("step_09d_evidence_arbitration", decision=d["decision"], answer=answer,
              parametric=parametric, n_passages=len(passages))
    return state
