"""
step_06b_poison_consensus.py  -  STEP 6b: Poison-Consensus Risk (corpus-poisoning channel)
==========================================================================================

WHY THIS STEP EXISTS
--------------------
Steps 3/6 detect *instructions* (prompt injection). Knowledge-corruption attacks
such as PoisonedRAG (Zou et al., 2024) plant *facts*, not instructions: the
poisoned passages are fluent, on-topic and contain nothing an injection
classifier can flag, so Step 6 passes them and Step 10 then certifies the
poisoned answer as "grounded". This step adds a dedicated corpus-poisoning risk
channel that feeds the same adaptive risk score as every other stage.

PER-PASSAGE SIGNALS (no LLM calls; all thresholds fixed a priori)
-----------------------------------------------------------------
  q_i  query-echo       LCS(query tokens, passage prefix) / |query tokens|.
                        Retrieval-optimised poison is written to maximise
                        sim(query, passage) (PoisonedRAG Eq. S = query ⊕ I), so
                        it restates the question verbatim. Clean encyclopaedic
                        passages do not open by repeating the user's question.
  c_i  coordination     max_j  σ((cos_ij-0.85)/0.02) · σ((ROUGE-L_ij-0.25)/0.03)
                        Multiple poisons for one target are sampled from the same
                        generator and are near-paraphrases: semantically AND
                        lexically close. (0.85 cosine / 0.25 ROUGE-L are the
                        thresholds TrustRAG reports in its Appendix B.2; we reuse
                        them rather than tuning on the test set.)
  r_i = 1 - (1 - 0.9·σ((q_i-0.75)/0.05)) (1 - 0.9·c_i)          (noisy-OR)

AGGREGATION INTO THE PIPELINE RISK (the adaptive cascade)
---------------------------------------------------------
  r_poison = max_i r_i
  effective_risk <- 1 - (1 - input_risk)(1 - w_p · r_poison),   w_p = 0.8
so Step 7 (rerank floor) and Step 10 (grounding threshold) tighten exactly as
they do for injection risk. Passages with r_i >= θ are removed (θ = 0.5).
Coordinated passages are also recorded as ONE source group so Step 9d can
count them as a single independent witness (sybil-resistant voting).
If every passage is removed the context is left empty: Step 9d then answers
from internal knowledge or abstains (TrustRAG returns [] in the same case).
"""
from __future__ import annotations

import math
import re

import numpy as np

from pipeline_common import PipelineState

ECHO_CENTER, ECHO_SCALE = 0.75, 0.05
COS_T, COS_SCALE = 0.85, 0.02
ROUGE_T, ROUGE_SCALE = 0.25, 0.03
W_ECHO, W_COORD = 0.9, 0.9
W_POISON = 0.8
DROP_THETA = 0.5

_TOK = re.compile(r"[a-z0-9]+")
_SCORER = None


def _sig(x: float) -> float:
    if x < -60:
        return 0.0
    if x > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def _toks(s: str) -> list[str]:
    return _TOK.findall((s or "").lower())


def _lcs(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def query_echo(query: str, passage: str) -> float:
    q = _toks(query)
    if not q:
        return 0.0
    prefix = _toks(passage)[: len(q) + 5]
    return _lcs(q, prefix) / len(q)


def _rouge_l(a: str, b: str) -> float:
    global _SCORER
    if _SCORER is None:
        try:
            from rouge_score import rouge_scorer
            _SCORER = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
        except ImportError:
            _SCORER = False
    if _SCORER:
        return _SCORER.score(a, b)["rougeL"].fmeasure
    ta, tb = _toks(a), _toks(b)
    l = _lcs(ta, tb)
    if not l:
        return 0.0
    p, r = l / len(tb), l / len(ta)
    return 2 * p * r / (p + r)


def _embed_all(texts: list[str]) -> np.ndarray:
    from step_04_query_embedding import _get_model
    return np.asarray(_get_model().encode(texts, normalize_embeddings=True))


def score_passages(query: str, passages: list[str]) -> dict:
    n = len(passages)
    echo = [query_echo(query, p) for p in passages]
    coord = [0.0] * n
    pair = {}
    if n >= 2:
        E = _embed_all(passages)
        cos = E @ E.T
        for i in range(n):
            for j in range(i + 1, n):
                v = _sig((float(cos[i, j]) - COS_T) / COS_SCALE) * \
                    _sig((_rouge_l(passages[i], passages[j]) - ROUGE_T) / ROUGE_SCALE)
                pair[(i, j)] = v
                coord[i] = max(coord[i], v)
                coord[j] = max(coord[j], v)
    risk = [1 - (1 - W_ECHO * _sig((e - ECHO_CENTER) / ECHO_SCALE)) * (1 - W_COORD * c)
            for e, c in zip(echo, coord)]
    # coordinated groups = connected components of pairs with v >= 0.5
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for (i, j), v in pair.items():
        if v >= 0.5:
            parent[find(i)] = find(j)
    groups = [find(i) for i in range(n)]
    return {"echo": echo, "coord": coord, "risk": risk, "group": groups}


def run(state: PipelineState, theta: float = DROP_THETA) -> PipelineState:
    if state.blocked or not state.context:
        return state
    passages = list(state.context)
    s = score_passages(state.prompt, passages)
    r_poison = max(s["risk"]) if s["risk"] else 0.0
    keep_idx = [i for i, r in enumerate(s["risk"]) if r < theta]
    state.context = [passages[i] for i in keep_idx]
    # Per-passage trust (1 - r_i) and source group travel with the passages so
    # Step 9d can weight / de-duplicate votes after Step 7 reorders them.
    trust = state.meta.setdefault("passage_trust", {})
    group = state.meta.setdefault("passage_group", {})
    for i in keep_idx:
        trust[passages[i]] = round(1.0 - s["risk"][i], 4)
        group[passages[i]] = int(s["group"][i])
    prev = state.input_risk()
    fused = 1 - (1 - prev) * (1 - W_POISON * r_poison)
    state.scores["poison_risk"] = round(r_poison, 4)
    if fused > prev:
        state.scores["effective_risk"] = round(fused, 4)
    state.meta["poison_consensus"] = {
        "echo": [round(x, 3) for x in s["echo"]],
        "coord": [round(x, 3) for x in s["coord"]],
        "risk": [round(x, 3) for x in s["risk"]],
        "group": s["group"],
        "dropped": [i for i in range(len(passages)) if i not in keep_idx],
        "r_poison": round(r_poison, 4),
        "effective_risk_after": round(max(prev, fused), 4),
    }
    state.log("step_06b_poison_consensus", n_in=len(passages), n_kept=len(keep_idx),
              r_poison=round(r_poison, 4))
    return state
