"""Build a TrustRAG-Table-2-style comparison (ACC / ASR per poison rate, per dataset)
from results/*.jsonl, with the paper's published Llama-3.1-8B rows for reference.

Outputs: RESULTS_TABLE2.md, RESULTS_TABLE2.csv, RESULTS_TABLE2.tex
Main table = PoisonedRAG passages WITHOUT the question prefix (paper Sec. 5.4: "all the
experiments are based on this setting"); a second table gives the with-question variant
and the PIA prompt-injection attack.
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results")
RATES = [5, 4, 3, 2, 1, 0]
DS = [("nq", "NQ"), ("msmarco", "MS-MARCO"), ("hotpotqa", "HotpotQA")]
SYS = [("vanilla", "Vanilla RAG (reproduced)"), ("trustrag", "TrustRAG stage 1&2 (reproduced, official code)"),
       ("poisonguard", "PoisonGuard-RAG (ours)")]
PAPER = {  # TrustRAG arXiv:2501.00879 Table 2, Llama-3.1-8B: (ACC, ASR) for 100,80,60,40,20 ; clean ACC
    "nq": {"Vanilla RAG": [(2, 98), (2, 98), (3, 97), (4, 93), (26, 73), (71, None)],
           "TrustRAG stage 1&2": [(83, 2), (85, 1), (84, 1), (83, 1), (82, 9), (82, None)]},
    "msmarco": {"Vanilla RAG": [(3, 97), (3, 96), (5, 94), (7, 93), (28, 70), (79, None)],
                "TrustRAG stage 1&2": [(87, 5), (84, 8), (85, 7), (85, 7), (83, 11), (85, None)]},
    "hotpotqa": {"Vanilla RAG": [(1, 99), (2, 97), (6, 94), (5, 94), (27, 81), (71, None)],
                 "TrustRAG stage 1&2": [(67, 4), (71, 4), (70, 7), (69, 5), (66, 18), (74, None)]},
}


def load(sys_, ds, p, var):
    f = os.path.join(R, f"{sys_}__{ds}__p{p}__{var}.jsonl")
    if not os.path.exists(f) and p == 0:        # clean run is identical in both variants
        f = os.path.join(R, f"{sys_}__{ds}__p0__{'with_q' if var == 'without_q' else 'without_q'}.jsonl")
    if not os.path.exists(f):
        return None
    rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    return rows or None


def cell(rows, p):
    if rows is None:
        return None
    n = len(rows)
    acc = 100 * sum(r["acc"] for r in rows) / n
    asr = 100 * sum(r["asr"] for r in rows) / n
    return {"acc": acc, "asr": None if p == 0 else asr, "n": n,
            "refuse": 100 * sum(1 for r in rows if r.get("blocked") or r.get("abstained")) / n,
            "sec": sum(r.get("sec", 0) for r in rows) / n}


def fmt(c, best_acc=False, best_asr=False, partial=True):
    if c is None:
        return "–"
    a = f"{c['acc']:.1f}"
    a = f"**{a}**" if best_acc else a
    if c["asr"] is None:
        s = a
    else:
        b = f"{c['asr']:.1f}"
        s = f"{a}/{'**' + b + '**' if best_asr else b}"
    return s + (f" (n={c['n']})" if partial and c["n"] < 100 else "")


def table(var, rates, title):
    out = [f"### {title}", "", "| Dataset | Defense | " + " | ".join(
        f"Poison-({p*20}%) {'ACC↑/ASR↓' if p else 'ACC↑'}" for p in rates) + " |",
        "|---|---|" + "---|" * len(rates)]
    csvrows = []
    for ds, dname in DS:
        cells = {s: [cell(load(s, ds, p, var), p) for p in rates] for s, _ in SYS}
        if not any(c for s in cells for c in cells[s]):
            continue
        first = True
        if var == "without_q":
            for pname, vals in PAPER[ds].items():
                row = []
                for p in rates:
                    v = vals[RATES.index(p)]
                    row.append(f"{v[0]:.1f}" if v[1] is None else f"{v[0]:.1f}/{v[1]:.1f}")
                out.append(f"| {dname if first else ''} | *{pname} — paper* | " + " | ".join(row) + " |")
                first = False
        for i, p in enumerate(rates):
            pass
        for s, sname in SYS:
            row = []
            for i, p in enumerate(rates):
                c = cells[s][i]
                others = [cells[o][i] for o, _ in SYS if o != "vanilla" and cells[o][i]]
                ba = c is not None and s != "vanilla" and len(others) > 1 and c["acc"] >= max(o["acc"] for o in others)
                bs = (c is not None and p and s != "vanilla" and len(others) > 1
                      and c["asr"] <= min(o["asr"] for o in others))
                row.append(fmt(c, ba, bs))
                if c:
                    csvrows.append([var, dname, sname, p * 20, round(c["acc"], 1),
                                    "" if c["asr"] is None else round(c["asr"], 1), c["n"],
                                    round(c["refuse"], 1), round(c["sec"], 1)])
            out.append(f"| {dname if first else ''} | {sname} | " + " | ".join(row) + " |")
            first = False
    return out, csvrows


md = ["# PoisonGuard-RAG vs TrustRAG — TrustRAG Table 2 protocol", "",
      "Backbone Llama-3.1-8B (Ollama `llama3.1:8b`, temp 0.01) for every reproduced row; Contriever top-5; "
      "100 PoisonedRAG target questions per dataset; poison rate = poisoned passages / 5 injected before retrieval; "
      "metrics exactly as TrustRAG `main_trustrag.py` (substring ACC; ASR = attacker answer present and correct answer absent). "
      "Bold = best of the reproduced defenses (same model, same passages). Paper rows are copied from TrustRAG Table 2 for reference; "
      "they were produced with LMDeploy on H100s, so compare ours against the *reproduced* TrustRAG row.", ""]
t1, c1 = table("without_q", RATES, "Table A — PoisonedRAG, poisoned passages without the question prefix (TrustRAG Table 2 setting)")
t2, c2 = table("with_q", [5, 1, 0], "Table B — PoisonedRAG with question prefix (TrustRAG code default, `LM_targeted`)")
t3, c3 = table("pia", [1], "Table C — PIA prompt-injection attack (1 of 5 passages is an injected instruction)")
md += t1 + [""] + t2 + [""] + t3 + [""]

# refusal / cost summary
md += ["### Benign refusal and cost (all runs)", "", "| Defense | runs | refused or abstained | mean s/query |", "|---|---|---|---|"]
for s, sname in SYS:
    allr = []
    for f in os.listdir(R):
        if f.startswith(s + "__"):
            allr += [json.loads(l) for l in open(os.path.join(R, f), encoding="utf-8") if l.strip()]
    if allr:
        md.append(f"| {sname} | {len(allr)} | {100*sum(1 for r in allr if r.get('blocked') or r.get('abstained'))/len(allr):.1f}% | "
                  f"{sum(r.get('sec',0) for r in allr)/len(allr):.1f} |")

open(os.path.join(HERE, "RESULTS_TABLE2.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
with open(os.path.join(HERE, "RESULTS_TABLE2.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["variant", "dataset", "defense", "poison_rate_pct", "ACC", "ASR", "n", "refused_or_abstained_pct", "sec_per_query"])
    w.writerows(c1 + c2 + c3)

# LaTeX version of Table A (reproduced rows)
tex = ["\\begin{table*}[t]\\centering\\small", "\\begin{tabular}{llcccccc}", "\\toprule",
       "Dataset & Defense & " + " & ".join(f"Poison-({p*20}\\%)" for p in RATES) + " \\\\",
       " & & " + " & ".join("ACC$\\uparrow$/ASR$\\downarrow$" if p else "ACC$\\uparrow$" for p in RATES) + " \\\\", "\\midrule"]
for ds, dname in DS:
    cells = {s: [cell(load(s, ds, p, "without_q"), p) for p in RATES] for s, _ in SYS}
    if not any(c for s in cells for c in cells[s]):
        continue
    for j, (s, sname) in enumerate(SYS):
        vals = ["--" if c is None else (f"{c['acc']:.1f}" if c["asr"] is None else f"{c['acc']:.1f}/{c['asr']:.1f}") for c in cells[s]]
        esc = sname.replace("&", "\\&")
        tex.append((dname if j == 0 else "") + " & " + esc + " & " + " & ".join(vals) + " \\\\")
    tex.append("\\midrule")
tex[-1] = "\\bottomrule"
tex += ["\\end{tabular}", "\\caption{PoisonGuard-RAG vs.\\ TrustRAG on the TrustRAG/PoisonedRAG protocol (Llama-3.1-8B).}", "\\end{table*}"]
open(os.path.join(HERE, "RESULTS_TABLE2.tex"), "w", encoding="utf-8").write("\n".join(tex) + "\n")
print("\n".join(md))
