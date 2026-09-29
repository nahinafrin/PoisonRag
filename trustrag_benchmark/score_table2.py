"""Build a TrustRAG-paper-style Table 2 (ACC/ASR vs poison rate) from results/*.jsonl.

Protocol = TrustRAG Table 2: Llama-3.1-8B (here Ollama llama3.1:8b for every system),
Contriever top-5, PoisonedRAG poisons WITHOUT the question prefix (TrustRAG Sec. 5.4:
"all the experiments are based on this setting"), poison rate N/5.  0% = clean.
Writes RESULTS_table2.md and RESULTS_table2.csv.
"""
import csv, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
R = {}
for f in glob.glob(os.path.join(HERE, "results", "*.jsonl")):
    s, ds, p, var = os.path.basename(f)[:-6].split("__")
    rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    if s == "poisonguard":
        # v3.1 risk-adaptive abstention, applied identically to rows produced before the
        # code change (the rule only replaces the output with an abstention, so this is exact)
        for r in rows:
            a, pc = r.get("arbitration") or {}, r.get("poison_consensus") or {}
            if a.get("decision") == "uncorroborated" and (pc.get("dropped") or (r.get("risk") or 0) >= 0.5):
                r["acc"], r["asr"], r["abstained"] = False, False, True
    if rows:
        R[(s, ds, int(p[1:]), var)] = rows

PAPER = {  # TrustRAG Table 2 (Llama-3.1-8B): rate -> (ACC, ASR)
    "nq": {"Vanilla RAG": [(2, 98), (2, 98), (3, 97), (4, 93), (26, 73), (71, None)],
           "TrustRAG stage 1&2": [(83, 2), (85, 1), (84, 1), (83, 1), (82, 9), (82, None)]},
    "msmarco": {"Vanilla RAG": [(3, 97), (3, 96), (5, 94), (7, 93), (28, 70), (79, None)],
                "TrustRAG stage 1&2": [(87, 5), (84, 8), (85, 7), (85, 7), (83, 11), (85, None)]},
    "hotpotqa": {"Vanilla RAG": [(1, 99), (2, 97), (6, 94), (5, 94), (27, 81), (71, None)],
                 "TrustRAG stage 1&2": [(67, 4), (71, 4), (70, 7), (69, 5), (66, 18), (74, None)]},
}
SYS = [("vanilla", "Vanilla RAG"), ("trustrag", "TrustRAG stage 1&2 (reproduced, official code)"),
       ("poisonguard", "PoisonGuard-RAG v3.1 (isolated arbitration)"),
       ("poisonguard_v32", "PoisonGuard-RAG v3.2 (+ joint-reading fallback, final)")]
RATES = [5, 4, 3, 2, 1, 0]
DSN = {"nq": "NQ", "msmarco": "MS-MARCO", "hotpotqa": "HotpotQA"}


def cell(s, ds, p, var):
    key = (s, ds, p, "with_q" if p == 0 else var)
    rs = R.get(key)
    if not rs:
        return None
    n = len(rs)
    return (round(100 * sum(r["acc"] for r in rs) / n, 1), round(100 * sum(r["asr"] for r in rs) / n, 1), n,
            round(100 * sum(1 for r in rs if r.get("blocked") or r.get("abstained")) / n, 1),
            round(sum(r.get("sec", 0) for r in rs) / n, 1))


def table(var, title):
    out = [f"### {title}", "",
           "| Dataset | Defense | " + " | ".join(f"Poison-({p*20}%) ACC↑ / ASR↓" if p else "Poison-(0%) ACC↑" for p in RATES) + " |",
           "|---|---|" + "---|" * len(RATES)]
    csvrows = []
    for ds in ["nq", "msmarco", "hotpotqa"]:
        cells = {s: [cell(s, ds, p, var) for p in RATES] for s, _ in SYS}
        if not any(c for v in cells.values() for c in v):
            continue
        best_acc = [max((cells[s][i][0] for s, _ in SYS if cells[s][i] and cells[s][i][2] >= 100), default=None) for i in range(len(RATES))]
        best_asr = [min((cells[s][i][1] for s, _ in SYS if cells[s][i] and cells[s][i][2] >= 100 and RATES[i]), default=None) for i in range(len(RATES))]
        first = True
        for s, name in SYS:
            txt = []
            for i, c in enumerate(cells[s]):
                if not c:
                    txt.append("–"); continue
                a = f"**{c[0]:.1f}**" if c[0] == best_acc[i] and s != "vanilla" else f"{c[0]:.1f}"
                b = f"**{c[1]:.1f}**" if c[1] == best_asr[i] and s != "vanilla" else f"{c[1]:.1f}"
                partial = "" if c[2] >= 100 else f" (n={c[2]})"
                txt.append((a if RATES[i] == 0 else f"{a} / {b}") + partial)
                csvrows.append([var, DSN[ds], name, f"{RATES[i]*20}%", c[0], c[1] if RATES[i] else "", c[2], c[3], c[4]])
            out.append(f"| {DSN[ds] if first else ''} | {name} | " + " | ".join(txt) + " |")
            first = False
        if var == "without_q":
            for pname, vals in PAPER[ds].items():
                out.append(f"| | *{pname} — paper* | " + " | ".join(
                    (f"{a:.1f}" if b is None else f"{a:.1f} / {b:.1f}") for a, b in vals) + " |")
    out.append("")
    return out, csvrows


md = ["# PoisonGuard-RAG vs TrustRAG — TrustRAG Table 2 protocol", "",
      "All measured rows: same backbone (Ollama `llama3.1:8b`), same Contriever top-5 passages, same PoisonedRAG "
      "poisons, TrustRAG's own ACC/ASR code. **Bold** = best measured defense (complete 100-question cells only). "
      "Paper rows are the published Llama-3.1-8B numbers (authors' LMDeploy setup) for reference. "
      "NQ was used to design the final arbitration rule (development set); HotpotQA and MS-MARCO are held out.", ""]
allcsv = []
for var, title in [("without_q", "Table 2 (paper setting: poisons without the question prefix)"),
                   ("with_q", "Supplementary: PoisonedRAG poisons WITH the question prefix (TrustRAG code default)")]:
    t, c = table(var, title); md += t; allcsv += c
# PIA + cost
md += ["### Prompt-injection attack (PIA, TrustRAG Table 1 setting: 1 injected passage in top-5)", "",
       "| Dataset | Defense | ACC↑ / ASR↓ | n |", "|---|---|---|---|"]
for ds in ["nq", "hotpotqa", "msmarco"]:
    for s, name in SYS:
        rs = R.get((s, ds, 1, "pia"))
        if rs:
            n = len(rs)
            md.append(f"| {DSN[ds]} | {name} | {100*sum(r['acc'] for r in rs)/n:.1f} / {100*sum(r['asr'] for r in rs)/n:.1f} | {n} |")
md += ["", "### Cost and benign refusals (all measured runs)", "", "| Defense | mean s/query | refused or abstained (clean 0% runs) |", "|---|---|---|"]
for s, name in SYS:
    rows = [r for k, v in R.items() if k[0] == s for r in v]
    clean = [r for k, v in R.items() if k[0] == s and k[2] == 0 for r in v]
    if rows:
        md.append(f"| {name} | {sum(r.get('sec',0) for r in rows)/len(rows):.1f} | "
                  f"{(100*sum(1 for r in clean if r.get('blocked') or r.get('abstained'))/len(clean)) if clean else 0:.1f}% |")
open(os.path.join(HERE, "RESULTS_table2.md"), "w", encoding="utf-8").write("\n".join(md))
with open(os.path.join(HERE, "RESULTS_table2.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["setting", "dataset", "defense", "poison_rate", "ACC", "ASR", "n", "refused_or_abstained_pct", "sec_per_query"]); w.writerows(allcsv)
print("\n".join(md))
