import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import score_v4_test as S
out = []
for s in ["vanilla", "trustrag", "poisonguard_v4", "poisonguard_v5", "closedbook"]:
    for ds, _ in S.DS:
        ids = S.test_ids(ds)
        for p in S.RATES:
            d = S.rows(s, ds, p)
            for q in ids:
                r = d.get(q)
                if not r: continue
                sa, ss = S.strict(r)
                a = r.get("arbitration") or {}
                pc = r.get("poison_consensus") or {}
                cf = r.get("context_filter") or {}
                out.append(dict(sys=s, ds=ds, p=p, qid=q, acc=bool(r["acc"]), asr=bool(r["asr"]), sacc=sa, sasr=ss,
                    sec=r.get("sec"), adv_topk=r.get("n_adv_in_topk"),
                    adv_gen=r.get("n_adv_reaching_generator", r.get("n_adv_after_stage1")),
                    n_kept=(r.get("n_after_stage1") if s == "trustrag" else (len(a.get("per_passage") or []) if a else None)),
                    pc_dropped=len(pc.get("dropped") or []), cf_dropped=len(cf.get("dropped") or []),
                    decision=a.get("decision"), parametric=a.get("parametric"), risk=r.get("risk"),
                    step_sec=r.get("step_sec"), blocked=r.get("blocked"), abstained=r.get("abstained"),
                    anslen=len(r.get("answer") or "")))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_per_question.json"), "w"))
print(len(out))
