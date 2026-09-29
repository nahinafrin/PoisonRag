"""Aggregate results/*.jsonl into ACC/ASR tables (TrustRAG metric definitions)
and put the paper's published Llama-3.1-8B numbers next to them."""
import glob, json, math, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
rows = collections.defaultdict(list)
for f in glob.glob(os.path.join(HERE, os.environ.get("BENCH_RESULTS", "results"), "*.jsonl")):
    sys_, ds, p, var = os.path.basename(f)[:-6].split("__")
    for line in open(f, encoding="utf-8"):
        try:
            rows[(sys_, ds, int(p[1:]), var)].append(json.loads(line))
        except Exception:
            pass

# TrustRAG paper, Llama-3.1-8B, Contriever, top-5 (Table 7 NQ / Table 9 HotpotQA / Table 8 MS-MARCO)
PAPER = {
    ("nq", 5): {"Vanilla RAG": (2, 98), "TrustRAG": (83, 2)},
    ("nq", 4): {"Vanilla RAG": (2, 98), "TrustRAG": (85, 1)},
    ("nq", 3): {"Vanilla RAG": (3, 97), "TrustRAG": (84, 1)},
    ("nq", 2): {"Vanilla RAG": (4, 93), "TrustRAG": (83, 1)},
    ("nq", 1): {"Vanilla RAG": (26, 73), "TrustRAG": (82, 9)},
    ("nq", 0): {"Vanilla RAG": (71, None), "TrustRAG": (82, None)},
    ("hotpotqa", 5): {"Vanilla RAG": (1, 99), "TrustRAG": (67, 4)},
    ("hotpotqa", 3): {"Vanilla RAG": (6, 94), "TrustRAG": (70, 7)},
    ("hotpotqa", 1): {"Vanilla RAG": (27, 81), "TrustRAG": (66, 18)},
    ("hotpotqa", 0): {"Vanilla RAG": (71, None), "TrustRAG": (74, None)},
    ("msmarco", 5): {"Vanilla RAG": (3, 97), "TrustRAG": (87, 5)},
    ("msmarco", 3): {"Vanilla RAG": (5, 94), "TrustRAG": (85, 7)},
    ("msmarco", 1): {"Vanilla RAG": (28, 70), "TrustRAG": (83, 11)},
    ("msmarco", 0): {"Vanilla RAG": (79, None), "TrustRAG": (85, None)},
}
NAMES = {"vanilla": "Vanilla RAG", "trustrag": "TrustRAG (reproduced)",
         "ours_v1": "Ours v1 (thesis pipeline as locked)", "ours_v2": "Ours v2 (+6b poison risk, +9d arbitration)",
         "ours_v21": "Ours v2.1 (v2 + reasoned internal knowledge in 9d)",
         "poisonguard": "**PoisonGuard-RAG (final)**"}
ORDER = ["vanilla", "trustrag", "poisonguard", "ours_v1", "ours_v2", "ours_v21"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


summary = []
for (s, ds, p, var), rs in sorted(rows.items()):
    n = len(rs)
    acc = sum(r["acc"] for r in rs)
    asr = sum(r["asr"] for r in rs)
    rec = {"system": s, "ds": ds, "poison": p, "rate": f"{p*20}%", "variant": var, "n": n,
           "ACC": round(100 * acc / n, 1), "ASR": round(100 * asr / n, 1),
           "ACC_ci": [round(x, 1) for x in wilson(acc, n)], "ASR_ci": [round(x, 1) for x in wilson(asr, n)],
           "refused_or_abstained": sum(1 for r in rs if r.get("blocked") or r.get("abstained")),
           "errors": sum(1 for r in rs if r.get("error")),
           "mean_sec": round(sum(r.get("sec", 0) for r in rs) / n, 2),
           "adv_in_topk": round(sum(r.get("n_adv_in_topk", 0) for r in rs) / n, 2)}
    if "n_adv_reaching_generator" in rs[0]:
        rec["adv_reaching_generator"] = round(sum(r["n_adv_reaching_generator"] for r in rs) / n, 2)
    if "n_adv_after_stage1" in rs[0]:
        rec["adv_reaching_generator"] = round(sum(r["n_adv_after_stage1"] for r in rs) / n, 2)
    summary.append(rec)
json.dump(summary, open(os.path.join(HERE, "summary.json"), "w"), indent=1)

lines = ["# TrustRAG head-to-head (PoisonedRAG protocol, Contriever top-5, backbone llama3.1:8b)", ""]
for ds in ["nq", "hotpotqa", "msmarco"]:
    for var in ["with_q", "without_q", "pia"]:
        sub = [r for r in summary if r["ds"] == ds and r["variant"] == var]
        if not sub:
            continue
        ps = sorted({r["poison"] for r in sub}, reverse=True)
        lines.append(f"## {ds.upper()} — poisoned passages { {'with_q':'= question + adv text (TrustRAG code)','without_q':'without question prefix','pia':'PIA prompt-injection attack (1 of 5 passages)'}[var] }")
        lines.append("")
        lines.append("| System | " + " | ".join(f"Poison {p*20}% ACC↑/ASR↓" for p in ps) + " |")
        lines.append("|---|" + "---|" * len(ps))
        for s in ORDER:
            cells = []
            for p in ps:
                r = next((x for x in sub if x["system"] == s and x["poison"] == p), None)
                if r is None:
                    cells.append("–")
                elif p == 0:
                    cells.append(f"{r['ACC']:.0f} / – (n={r['n']})")
                else:
                    cells.append(f"{r['ACC']:.0f} / {r['ASR']:.0f} (n={r['n']})")
            if any(c != "–" for c in cells):
                lines.append(f"| {NAMES[s]} | " + " | ".join(cells) + " |")
        if var == "with_q":
            for pname in ["Vanilla RAG", "TrustRAG"]:
                cells = []
                for p in ps:
                    v = PAPER.get((ds, p), {}).get(pname)
                    cells.append("–" if v is None else (f"{v[0]} / –" if v[1] is None else f"{v[0]} / {v[1]}"))
                lines.append(f"| *{pname} — paper (Llama-3.1-8B)* | " + " | ".join(cells) + " |")
        lines.append("")
open(os.path.join(HERE, "RESULTS_trustrag_comparison.md"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
