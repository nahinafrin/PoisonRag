import json, collections
S = json.load(open('/home/claude/stats.json'))
D = json.load(open('/mnt/user-data/uploads/TrustRag/trustrag_benchmark/figures/_per_question.json'))
OUT = '/mnt/user-data/outputs/poisonguard_results'
DS = [('nq', 'NQ'), ('hotpotqa', 'HotpotQA'), ('msmarco', 'MS-MARCO')]
SYS = [('vanilla', 'Vanilla RAG'), ('trustrag', 'TrustRAG'), ('poisonguard_v4', 'PoisonGuard v4 (previous)'), ('poisonguard_v5', 'PoisonGuard-RAG (ours)')]
DEF = ['trustrag', 'poisonguard_v4', 'poisonguard_v5']
RATES = [5, 4, 3, 2, 1, 0]
tex, md = [], []


def B(v, best, fmt='{:.0f}'):
    t = fmt.format(v)
    return (r'\textbf{' + t + '}', f'**{t}**') if best else (t, t)


def main_table(ia, is_, label, caption):
    tex.append(r'\begin{table*}[t]\centering\small' + '\n' + r'\caption{' + caption + '}\\label{' + label + '}')
    tex.append(r'\begin{tabular}{ll' + 'cc' * 5 + 'c}\\toprule')
    tex.append('Dataset & Defense & ' + ' & '.join(r'\multicolumn{2}{c}{Poison ' + f'{p*20}\\%' + '}' for p in RATES[:5]) + r' & Clean \\')
    tex.append(' & & ' + ' & '.join(['ACC$\\uparrow$ & ASR$\\downarrow$'] * 5) + r' & ACC$\uparrow$ \\\midrule')
    md.append('| Dataset | Defense | ' + ' | '.join(f'{p*20}% ACC↑ / ASR↓' for p in RATES[:5]) + ' | Clean ACC↑ |')
    md.append('|---|---|' + '---|' * 6)
    for ds, dn in DS:
        for i, (s, name) in enumerate(SYS):
            tr, mr = [], []
            for p in RATES:
                c = S['cells'][f'{s}|{ds}|{p}']
                ba = s != 'vanilla' and c[ia] >= max(S['cells'][f'{d}|{ds}|{p}'][ia] for d in DEF)
                a = B(c[ia], ba)
                if p:
                    bs = s != 'vanilla' and c[is_] <= min(S['cells'][f'{d}|{ds}|{p}'][is_] for d in DEF)
                    b = B(c[is_], bs); tr += [a[0], b[0]]; mr.append(f'{a[1]} / {b[1]}')
                else:
                    tr.append(a[0]); mr.append(a[1])
            nm = r'\textbf{' + name + '}' if s == 'poisonguard_v5' else name
            tex.append((r'\multirow{4}{*}{' + dn + '}' if i == 0 else '') + f' & {nm} & ' + ' & '.join(tr) + r' \\')
            md.append(f"| {dn if i == 0 else ''} | {'**'+name+'**' if s=='poisonguard_v5' else name} | " + ' | '.join(mr) + ' |')
        tex.append(r'\midrule' if ds != 'msmarco' else r'\bottomrule')
    tex.append(r'\end{tabular}\end{table*}' + '\n')
    md.append('')


md += ['# PoisonGuard-RAG — result tables', '',
       'Held-out test half: PoisonedRAG targets 51–100 of each dataset, 50 questions per cell, Llama-3.1-8B (Ollama) for every system, '
       'Contriever top-5, poison rate = poisoned passages / 5. Bold = best among the three defenses (ties bold all).', '',
       '## Table 1 — ACC / ASR under corpus poisoning (TrustRAG substring metric)', '']
main_table(0, 1, 'tab:main', r'Accuracy (ACC, \%) and attack success rate (ASR, \%) under PoisonedRAG corpus poisoning on the held-out test half (50 questions per cell, Llama-3.1-8B). Best defense per column in bold.')
md += ['## Table 2 — same, strict whole-word matching (applied identically to every system)', '']
main_table(2, 3, 'tab:strict', r'As Table~\ref{tab:main}, scored with strict whole-word matching (so ``no'' is not matched inside ``know''), applied identically to every system.')

# Table 3 summary
md += ['## Table 3 — Summary: robustness, utility and cost', '',
       '| Dataset | Defense | mean ACC↑ | mean ASR↓ | Clean ACC↑ | Refusal/abstain↓ | s/query↓ | Speed-up vs TrustRAG |', '|---|---|---|---|---|---|---|---|']
tex.append(r'\begin{table}[t]\centering\small\caption{Summary over the five poisoned settings (mean ACC/ASR), clean accuracy, refusal rate and latency on the same laptop.}\label{tab:summary}')
tex.append(r'\begin{tabular}{llrrrrrr}\toprule Dataset & Defense & mACC$\uparrow$ & mASR$\downarrow$ & Clean$\uparrow$ & Refuse$\downarrow$ & s/q$\downarrow$ & Speed-up \\\midrule')
for ds, dn in DS:
    for i, s in enumerate(DEF):
        v = S['summ'][f'{s}|{ds}']; t = S['summ'][f'trustrag|{ds}']
        best = lambda k, lo=False: (min if lo else max)(S['summ'][f'{d}|{ds}'][k] for d in DEF) == v[k]
        cells = [B(v['macc'], best('macc'), '{:.1f}'), B(v['masr'], best('masr', True), '{:.1f}'), B(v['clean'], best('clean')),
                 B(v['refuse'], best('refuse', True), '{:.1f}'), B(v['sec'], best('sec', True), '{:.1f}'), (f"{t['sec']/v['sec']:.1f}$\\times$", f"{t['sec']/v['sec']:.1f}×")]
        name = dict(SYS)[s]
        tex.append((r'\multirow{3}{*}{' + dn + '}' if i == 0 else '') + f' & {name} & ' + ' & '.join(c[0] for c in cells) + r' \\')
        md.append(f"| {dn if i==0 else ''} | {name} | " + ' | '.join(c[1] for c in cells) + ' |')
    tex.append(r'\midrule' if ds != 'msmarco' else r'\bottomrule')
tex.append(r'\end{tabular}\end{table}' + '\n'); md.append('')

# Table 4 filter + exposure
# Table 3b: no-retrieval baseline and retrieval-needed subset
md += ['## Table 3b — Does the defence keep the benefit of retrieval? (clean ACC unless noted)', '',
       '| Dataset | No retrieval (closed book) | Ours @100% poison | Ours clean | TrustRAG clean | Vanilla clean | Retrieval-needed subset: n / Vanilla / TrustRAG / Ours |', '|---|---|---|---|---|---|---|']
for ds, dn in DS:
    cb = {r['qid']: r for r in D if r['sys'] == 'closedbook' and r['ds'] == ds}
    g = lambda s, p: {r['qid']: r for r in D if r['sys'] == s and r['ds'] == ds and r['p'] == p}
    v0, v5, t0, va = g('poisonguard_v5', 0), g('poisonguard_v5', 5), g('trustrag', 0), g('vanilla', 0)
    need = [q for q in cb if not cb[q]['acc']]
    pct = lambda d: 100 * sum(d[q]['acc'] for q in cb) / len(cb)
    md.append(f"| {dn} | {pct(cb):.0f} | {pct(v5):.0f} | {pct(v0):.0f} | {pct(t0):.0f} | {pct(va):.0f} | {len(need)} / {sum(va[q]['acc'] for q in need)} / {sum(t0[q]['acc'] for q in need)} / {sum(v0[q]['acc'] for q in need)} |")
md.append('')

# Table 7: paper-reported baselines (TrustRAG Table 2, Llama3.1-8B, all 100 q) next to ours (held-out 50 q)
import csv as _csv
md += ['## Table 7 — Reported baselines (TrustRAG paper, Table 2, Llama3.1-8B, 100 q) vs ours (held-out q 51-100)', '',
       'Different question sets and serving stacks: indicative only; the controlled comparison is Table 1.', '',
       '| Dataset | Defense | 100% | 80% | 60% | 40% | 20% | clean |', '|---|---|---|---|---|---|---|---|']
rows = list(_csv.DictReader(open('/mnt/user-data/uploads/TrustRag/trustrag_benchmark/paper_reported_table2.csv')))
for ds, dn in DS:
    for r in rows:
        if r['dataset'] == dn:
            md.append(f"| {dn} | {r['defense']} (reported) | " + ' | '.join(f"{r[f'p{p}_acc']} / {r[f'p{p}_asr']}" for p in [100, 80, 60, 40, 20]) + f" | {r['p0_acc']} |")
    c = lambda p, i: S['cells'][f'poisonguard_v5|{ds}|{p}'][i]
    md.append(f"| {dn} | **PoisonGuard-RAG (ours, measured)** | " + ' | '.join(f"{c(p,0):.0f} / {c(p,1):.0f}" for p in [5, 4, 3, 2, 1]) + f" | {c(0,0):.0f} |")
md.append('')

md += ['## Table 4 — Passage filtering and robustness after exposure (poisoned settings only)', '',
       'Poison recall = share of retrieved poisoned passages removed before generation; clean retention = share of retrieved clean passages kept; '
       'ASR | exposed = ASR on queries where ≥1 poisoned passage still reached the LLM.', '',
       '| Dataset | Defense | Poison recall | Filter precision | Clean retention↑ | Exposed queries | ASR given exposure↓ |', '|---|---|---|---|---|---|---|']
tex.append(r'\begin{table}[t]\centering\small\caption{Passage-level filtering (poisoned settings) and attack success on queries where at least one poisoned passage reached the generator.}\label{tab:filter}')
tex.append(r'\begin{tabular}{llrrrrr}\toprule Dataset & Defense & Recall & Prec. & Clean kept$\uparrow$ & Exposed & ASR$|$exp.$\downarrow$ \\\midrule')
for ds, dn in DS:
    for i, s in enumerate(['trustrag', 'poisonguard_v5']):
        f = S['filt_pois'][f'{s}|{ds}']; e = S['exposed'][f'{s}|{ds}']
        o = S['filt_pois'][f"{'poisonguard_v5' if s=='trustrag' else 'trustrag'}|{ds}"]; oe = S['exposed'][f"{'poisonguard_v5' if s=='trustrag' else 'trustrag'}|{ds}"]
        cells = [B(f['R'], f['R'] >= o['R'], '{:.1f}'), B(f['P'], f['P'] >= o['P'], '{:.1f}'), B(f['clean_keep'], f['clean_keep'] >= o['clean_keep'], '{:.1f}'),
                 (str(e['n']), str(e['n'])), B(e['asr'], e['asr'] <= oe['asr'], '{:.1f}')]
        name = dict(SYS)[s]
        tex.append((r'\multirow{2}{*}{' + dn + '}' if i == 0 else '') + f' & {name} & ' + ' & '.join(c[0] for c in cells) + r' \\')
        md.append(f"| {dn if i==0 else ''} | {name} | " + ' | '.join(c[1] for c in cells) + ' |')
    tex.append(r'\midrule' if ds != 'msmarco' else r'\bottomrule')
tex.append(r'\end{tabular}\end{table}' + '\n'); md.append('')

# Table 5 paired
md += ['## Table 5 — Paired comparison vs TrustRAG (same question, same poison rate; 250 pairs per dataset)', '',
       'Wins/losses count only discordant pairs; p = two-sided exact sign (McNemar) test.', '',
       '| Dataset | ACC: ours ✓ TrustRAG ✗ | ACC: TrustRAG ✓ ours ✗ | p | Attacks only TrustRAG fell for | Attacks only ours fell for | p |', '|---|---|---|---|---|---|---|']
tex.append(r'\begin{table}[t]\centering\small\caption{Paired per-question comparison with TrustRAG over the five poisoned settings (exact McNemar test on discordant pairs).}\label{tab:paired}')
tex.append(r'\begin{tabular}{lrrrrrr}\toprule & \multicolumn{3}{c}{Correct answers} & \multicolumn{3}{c}{Successful attacks} \\ Dataset & Ours only & TrustRAG only & $p$ & TrustRAG only & Ours only & $p$ \\\midrule')
fp = lambda p: '<0.001' if p < 0.001 else f'{p:.3f}'
for k, dn in DS + [('all', 'All')]:
    a, s_ = S['pair'][k]['acc'], S['pair'][k]['asr']
    row = [str(a[0]), str(a[1]), fp(a[3]), str(s_[1]), str(s_[0]), fp(s_[3])]
    if k == 'all': tex.append(r'\midrule')
    tex.append(f'{dn} & ' + ' & '.join(r.replace('<', '$<$') for r in row) + r' \\')
    md.append(f'| {dn} | ' + ' | '.join(row) + ' |')
tex.append(r'\bottomrule\end{tabular}\end{table}' + '\n'); md.append('')

# Table 6 decision routes
routes = [('internal_anchored', 'Parametric answer agrees with evidence'), ('internal_anchored_conflict', 'Parametric answer overrides conflicting evidence'),
          ('corroborated', 'Corroborated by independent passages'), ('best_effort_joint', 'Best effort: knowledge + surviving passages'),
          ('best_effort_closed_book', 'Best effort: closed book (lone passage hidden)')]
md += ['## Table 6 — Which decision route answered (PoisonGuard-RAG, % of queries, poisoned settings) and accuracy on that route', '',
       '| Route | ' + ' | '.join(f'{dn} share / ACC' for _, dn in DS) + ' |', '|---|---|---|---|']
tex.append(r'\begin{table}[t]\centering\small\caption{Evidence-arbitration routes taken by PoisonGuard-RAG in the poisoned settings: share of queries (\%) and ACC (\%) on that route.}\label{tab:routes}')
tex.append(r'\begin{tabular}{lccc}\toprule Route & NQ & HotpotQA & MS-MARCO \\\midrule')
for rk, rn in routes:
    cs = []
    for ds, _ in DS:
        rs = [r for r in D if r['sys'] == 'poisonguard_v5' and r['ds'] == ds and r['p'] > 0]
        sel = [r for r in rs if r['decision'] == rk]
        cs.append(f"{100*len(sel)/len(rs):.1f} / {100*sum(r['acc'] for r in sel)/len(sel):.0f}" if sel else '0 / –')
    tex.append(f'{rn} & ' + ' & '.join(cs) + r' \\'); md.append(f'| {rn} | ' + ' | '.join(cs) + ' |')
tex.append(r'\bottomrule\end{tabular}\end{table}' + '\n'); md.append('')

md += ['## Risk score as a detector (diagnostic)', '', 'AUROC of the pipeline risk score for "≥1 poisoned passage in the top-5": ' +
       ', '.join(f"{dn} {S['aucs'][ds]:.3f}" for ds, dn in DS) + '.', '']
open(f'{OUT}/tables.tex', 'w').write('% requires \\usepackage{booktabs,multirow}\n' + '\n'.join(tex))
open(f'{OUT}/tables.md', 'w').write('\n'.join(md))
print('\n'.join(md))
