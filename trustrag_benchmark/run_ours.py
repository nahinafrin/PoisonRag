"""Run the thesis pipeline (Steps 1-13, run_full_pipeline.process) on the
TrustRAG / PoisonedRAG protocol.

Only retrieval is swapped: Step 5 returns the protocol's top-k list (clean
Contriever top-k merged with the poisoned passages by Contriever score) instead
of the rag-mini-wikipedia FAISS index, so every system sees identical passages.
If the closed-loop controller broadens retrieval (k -> 2k), it gets the next
passages from the same ranked pool (clean top-10 + poison).

Systems:
  ours_v1   the pipeline exactly as locked (fused 3-model ensemble, controller on)
  ours_v2   + Step 6b poison-consensus risk channel
            + Step 9d trust-weighted evidence arbitration (backbone llama3.1:8b)
"""
from __future__ import annotations

import argparse
import os
import sys
import time

from bench_common import append, done_ids, judge, load_cases, log, result_path

PIPE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "step4 dataset"))
sys.path.insert(0, PIPE_DIR)
os.chdir(PIPE_DIR)          # step modules read config files relative to this dir

# --- Ollama placement (runtime only, no change to any model or prompt) -------- #
# On an 8 GB GPU llama3.1:8b and llama-guard3:1b cannot both stay resident, so
# every guard call evicted the 8B generator (5-10 s reload each, 3x per query).
# Pin the 1B guard to CPU and give every other model the same context window so
# Ollama never reloads. Decisions are unchanged (same weights, temperature 0).
import langchain_ollama as _lo            # noqa: E402

_BaseChatOllama = _lo.ChatOllama


def _ChatOllama(*a, **k):
    model = str(k.get("model", a[0] if a else ""))
    k.setdefault("keep_alive", "60m")    # this machine's Ollama unloads after every call otherwise
    k.setdefault("client_kwargs", {"timeout": 240})   # never hang forever on one call
    if model.startswith("llama-guard"):
        k.setdefault("num_gpu", 0)
    else:
        k.setdefault("num_ctx", 4096)
    return _BaseChatOllama(*a, **k)


_lo.ChatOllama = _ChatOllama

import run_full_pipeline as rfp          # noqa: E402

_CUR = {"pool": []}


def _step5(state, k: int = 5, dim: int = 512):
    if state.blocked:
        return state
    state.context = [t for t, _ in _CUR["pool"][:k]]
    state.meta["retrieval_scores"] = []
    state.log("step_05_vector_search", retrieved=len(state.context), source="trustrag_protocol")
    return state


_TIMES: dict = {}


def _timed(name, fn):
    def w(*a, **k):
        t = time.time()
        try:
            return fn(*a, **k)
        finally:
            _TIMES[name] = round(_TIMES.get(name, 0.0) + time.time() - t, 2)
    return w


for _n in ["s1", "s2", "s3c", "s6", "s6b", "s7", "s8", "s9", "s9d", "s10", "s11", "s12", "s13"]:
    _m = getattr(rfp, _n)
    _m.run = _timed(_n, _m.run)

rfp.ensure_index = lambda *a, **k: None
rfp.s4.run = lambda state, **kw: state        # query embedding only feeds the old FAISS index
rfp.s5.run = _step5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", choices=["ours_v1", "ours_v2", "ours_v21"], required=True)
    ap.add_argument("--ds", default="nq")
    ap.add_argument("--poison", type=int, nargs="+", default=[5])
    ap.add_argument("--variant", default="with_q", choices=["with_q", "without_q"])
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    arbiter = (rfp.s9d.OllamaArbiter(parametric_mode="reasoned") if args.system == "ours_v21"
               else rfp.s9d.OllamaArbiter() if args.system == "ours_v2" else None)
    for p in args.poison:
        cases = load_cases(args.ds, p, args.variant, args.limit)
        path = result_path(args.system, args.ds, p, args.variant)
        done = done_ids(path)
        log(f"{args.system} {args.ds} p={p} {args.variant}: {len(cases)} cases, {len(done)} done")
        for c in cases:
            if c.qid in done:
                continue
            t0 = time.time()
            _TIMES.clear()
            # the protocol's exact top-5 first, then the rest of the pool for k>5 retries
            rest = [x for x in c.pool if x[0] not in set(c.contexts)]
            _CUR["pool"] = list(zip(c.contexts, c.is_adv)) + rest
            adv_set = {t for t, a in _CUR["pool"] if a}
            err = None
            try:
                if args.system == "ours_v1":
                    st = rfp.process(c.question, k=5, top_n=3, use_semantic_intent=False)
                else:
                    st = rfp.process(c.question, k=5, top_n=5, use_semantic_intent=False,
                                     poison_consensus=True, generator="arbitrated", arbiter=arbiter)
                rec = rfp._record(st, c.qid, c.correct)
                answer = st.meta.get("final_response", "")
            except Exception as e:           # fail-closed row, still counted
                import traceback
                err = traceback.format_exc()
                rec, answer = {}, ""
            acc, asr = judge(answer, c.correct, c.incorrect)
            ranked = (rec.get("retrieval") or {}).get("ranked_chunks") or []
            row = {"qid": c.qid, "question": c.question, "correct": c.correct, "incorrect": c.incorrect,
                   "n_poison": p, "variant": args.variant, "n_adv_in_topk": sum(c.is_adv),
                   "n_adv_reaching_generator": sum(1 for t in ranked if t in adv_set),
                   "n_ranked": len(ranked),
                   "answer": answer, "acc": acc, "asr": asr,
                   "blocked": rec.get("blocked"), "block_stage": rec.get("block_stage"),
                   "abstained": rec.get("abstained"),
                   "gen_answer": (rec.get("generation") or {}).get("answer"),
                   "poison_consensus": rec.get("poison_consensus"),
                   "arbitration": rec.get("arbitration"),
                   "controller_action": (rec.get("controller") or {}).get("final_action"),
                   "grounding": rec.get("grounding"),
                   "gate": rec.get("gate"),
                   "error": err, "sec": round(time.time() - t0, 2), "step_sec": dict(_TIMES)}
            append(path, row)
        log("done", path)


if __name__ == "__main__":
    main()
