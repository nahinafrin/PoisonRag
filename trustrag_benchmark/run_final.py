"""Benchmark adapter for the final system (poisonguard_rag package) on the
TrustRAG / PoisonedRAG protocol. Retrieval is the protocol's top-k list, so every
system sees identical passages.

  python run_final.py --ds nq --poison 5 1 0 --variant with_q
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import traceback

from bench_common import append, done_ids, judge, load_cases, log, result_path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from poisonguard_rag import pipeline      # noqa: E402



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ds", default="nq")
    ap.add_argument("--poison", type=int, nargs="+", default=[5])
    ap.add_argument("--variant", default="with_q", choices=["with_q", "without_q", "pia", "adaptive", "mimic"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0, help="skip the first N target questions (dev/test split)")
    ap.add_argument("--system", default="poisonguard", choices=["poisonguard", "poisonguard_v32", "poisonguard_v4", "poisonguard_v5"],
                    help="poisonguard = v3.1 (isolated arbitration); poisonguard_v32 = + joint-reading fallback")
    a = ap.parse_args()
    SYSTEM = a.system
    joint = SYSTEM == "poisonguard_v32"
    best = SYSTEM in ("poisonguard_v4", "poisonguard_v5")
    v5 = SYSTEM == "poisonguard_v5"
    for p in (a.poison if a.variant != "pia" else [1]):
        cases = load_cases(a.ds, p, a.variant, a.limit, offset=a.offset)
        path = result_path(SYSTEM, a.ds, p, a.variant)
        done = done_ids(path)
        log(f"{SYSTEM} {a.ds} p={p} {a.variant}: {len(cases)} cases, {len(done)} done")
        for c in cases:
            if c.qid in done:
                continue
            t0, err, rec = time.time(), None, {}
            try:
                st = pipeline.run(c.question, passages=c.contexts, joint_fallback=joint, best_effort=best, v5=v5)
                rec = pipeline.record(st)
                answer = st.final_response
            except Exception:
                err, answer = traceback.format_exc(), ""
            acc, asr = judge(answer, c.correct, c.incorrect)
            adv = {t for t, x in zip(c.contexts, c.is_adv) if x}
            row = {"qid": c.qid, "question": c.question, "correct": c.correct, "incorrect": c.incorrect,
                   "n_poison": p, "variant": a.variant, "n_adv_in_topk": sum(c.is_adv),
                   "n_adv_reaching_generator": sum(1 for t in rec.get("passages_used", []) if t in adv),
                   "answer": answer, "acc": acc, "asr": asr, "blocked": rec.get("blocked"),
                   "block_stage": rec.get("block_stage"), "abstained": rec.get("abstained"),
                   "arbitration": rec.get("arbitration"), "poison_consensus": rec.get("poison_consensus"),
                   "context_filter": rec.get("context_filter"), "risk": rec.get("risk"),
                   "risk_trace": rec.get("risk_trace"), "step_sec": rec.get("timings"),
                   "error": err, "sec": round(time.time() - t0, 2)}
            append(path, row)
        log("done", path)


if __name__ == "__main__":
    main()
