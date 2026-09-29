import json, math, collections, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import binomtest

D = json.load(open('/mnt/user-data/uploads/TrustRag/trustrag_benchmark/figures/_per_question.json'))
OUT = '/mnt/user-data/outputs/poisonguard_results'
os.makedirs(OUT, exist_ok=True)

DS = [('nq', 'NQ'), ('hotpotqa', 'HotpotQA'), ('msmarco', 'MS-MARCO')]
SYS = [('vanilla', 'Vanilla RAG'), ('trustrag', 'TrustRAG'), ('poisonguard_v4', 'PoisonGuard v4 (previous)'),
       ('poisonguard_v5', 'PoisonGuard-RAG (ours)')]
NAME = dict(SYS)
COL = {'vanilla': '#8f8e89', 'trustrag': '#eb6834', 'poisonguard_v4': '#1baf7a', 'poisonguard_v5': '#2a78d6'}
STY = {'vanilla': dict(ls=':', marker='s'), 'trustrag': dict(ls='-', marker='^'),
       'poisonguard_v4': dict(ls='--', marker='D'), 'poisonguard_v5': dict(ls='-', marker='o')}
RATES = [5, 4, 3, 2, 1, 0]
PR = [100, 80, 60, 40, 20, 0]
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.axisbelow': True,
                     'legend.frameon': False, 'savefig.dpi': 300, 'savefig.bbox': 'tight'})

by = collections.defaultdict(list)
for r in D:
    by[(r['sys'], r['ds'], r['p'])].append(r)


def m(s, ds, p, k):
    rs = by[(s, ds, p)]
    return 100 * sum(r[k] for r in rs) / len(rs)


def save(fig, name):
    fig.savefig(f'{OUT}/{name}.pdf'); fig.savefig(f'{OUT}/{name}.png'); plt.close(fig)


def legend_top(fig, axes, n=4):
    h, l = axes.get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', ncol=n, bbox_to_anchor=(0.5, 1.04))

# ---------- Fig 1: ACC / ASR vs poison rate ----------
for metric, (ka, ks) in [('paper', ('acc', 'asr')), ('strict', ('sacc', 'sasr'))]:
    fig, ax = plt.subplots(2, 3, figsize=(10, 5.4), sharex=True)
    for j, (ds, dn) in enumerate(DS):
        for s, _ in SYS:
            lw = 2.4 if s == 'poisonguard_v5' else 1.5
            ax[0, j].plot(PR, [m(s, ds, p, ka) for p in RATES], color=COL[s], lw=lw, ms=5, label=NAME[s], **STY[s])
            ax[1, j].plot(PR[:5], [m(s, ds, p, ks) for p in RATES[:5]], color=COL[s], lw=lw, ms=5, **STY[s])
        cbk = [r for r in by[('closedbook', ds, 0)]]
        if cbk:
            cb = 100 * np.mean([r['sacc' if ka == 'sacc' else 'acc'] for r in cbk])
            ax[0, j].axhline(cb, color=INK2, lw=1, ls=(0, (1, 2)))
            ax[0, j].text(99, cb + 1.5, f'no retrieval ({cb:.0f}%)', fontsize=7, color=INK2, ha='left')
        ax[0, j].set_title(dn, fontweight='bold')
        ax[0, j].set_ylim(0, 100); ax[1, j].set_ylim(0, 100)
        ax[1, j].set_xlabel('Poison rate (%)'); ax[1, j].set_xticks(PR); ax[1, j].invert_xaxis()
    ax[0, 0].set_ylabel('ACC (%) ↑'); ax[1, 0].set_ylabel('ASR (%) ↓')
    legend_top(fig, ax[0, 0])
    fig.tight_layout()
    save(fig, f'fig1_acc_asr_vs_poison_rate_{metric}')

# ---------- summary stats ----------
summ = {}
for ds, dn in DS:
    for s, _ in SYS:
        summ[(s, ds)] = dict(
            macc=np.mean([m(s, ds, p, 'acc') for p in RATES[:5]]), masr=np.mean([m(s, ds, p, 'asr') for p in RATES[:5]]),
            smacc=np.mean([m(s, ds, p, 'sacc') for p in RATES[:5]]), smasr=np.mean([m(s, ds, p, 'sasr') for p in RATES[:5]]),
            clean=m(s, ds, 0, 'acc'), sclean=m(s, ds, 0, 'sacc'),
            sec=np.mean([r['sec'] for p in RATES for r in by[(s, ds, p)]]),
            refuse=100 * np.mean([bool(r['blocked'] or r['abstained']) for p in RATES for r in by[(s, ds, p)]]))

# ---------- Fig 2: security-utility trade-off ----------
fig, ax = plt.subplots(1, 3, figsize=(10, 3.4), sharey=True)
for j, (ds, dn) in enumerate(DS):
    a = ax[j]
    for s, _ in SYS:
        x, y = summ[(s, ds)]['masr'], summ[(s, ds)]['macc']
        a.scatter(x, y, s=90 if s == 'poisonguard_v5' else 55, color=COL[s], marker=STY[s]['marker'],
                  edgecolor='white', linewidth=1.5, zorder=3, label=NAME[s])
    t, v = summ[('trustrag', ds)], summ[('poisonguard_v5', ds)]
    a.annotate('', xy=(v['masr'], v['macc']), xytext=(t['masr'], t['macc']),
               arrowprops=dict(arrowstyle='->', color=INK2, lw=1))
    a.set_title(dn, fontweight='bold'); a.set_xlabel('Mean ASR over poisoned settings (%) ↓')
    a.set_xlim(-3, 80); a.set_ylim(20, 100)
    a.fill_between([-3, 15], 60, 100, color='#2a78d6', alpha=0.06, zorder=0)
    a.text(1, 97, 'robust & useful', color=INK2, fontsize=7.5, va='top')
ax[0].set_ylabel('Mean ACC over poisoned settings (%) ↑')
legend_top(fig, ax[0]); fig.tight_layout()
save(fig, 'fig2_security_utility_tradeoff')

# ---------- passage-filter detection ----------
def filt(s, ds, rates=RATES):
    tp = fn = fp = tn = 0
    for p in rates:
        for r in by[(s, ds, p)]:
            adv, clean = r['adv_topk'], 5 - r['adv_topk']
            kept_adv, kept_clean = r['adv_gen'], r['n_kept'] - r['adv_gen']
            tp += adv - kept_adv; fn += kept_adv; fp += clean - kept_clean; tn += kept_clean
    P = tp / (tp + fp) if tp + fp else float('nan'); R = tp / (tp + fn) if tp + fn else float('nan')
    F = 2 * P * R / (P + R) if P + R else float('nan')
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, P=100 * P, R=100 * R, F=100 * F,
                clean_keep=100 * tn / (tn + fp))

fig, ax = plt.subplots(1, 3, figsize=(10, 3.2), sharey=True)
w = 0.2
for j, (ds, dn) in enumerate(DS):
    a = ax[j]; x = np.arange(5)
    vals = {}
    vals['topk'] = [np.mean([r['adv_topk'] for r in by[('trustrag', ds, p)]]) for p in RATES[:5]]
    vals['trustrag'] = [np.mean([r['adv_gen'] for r in by[('trustrag', ds, p)]]) for p in RATES[:5]]
    vals['poisonguard_v5'] = [np.mean([r['adv_gen'] for r in by[('poisonguard_v5', ds, p)]]) for p in RATES[:5]]
    for k, (key, lab, c) in enumerate([('topk', 'Retrieved (top-5, no defense)', '#c9c8c2'),
                                       ('trustrag', 'After TrustRAG filter', COL['trustrag']),
                                       ('poisonguard_v5', 'After PoisonGuard-RAG filters (ours)', COL['poisonguard_v5'])]):
        b = a.bar(x + (k - 1) * (w + 0.03), vals[key], w, color=c, label=lab)
        for xi, v in zip(x + (k - 1) * (w + 0.03), vals[key]):
            if False:
                a.text(xi, v + 0.06, f'{v:.2f}', ha='center', fontsize=6.3, color=INK2)
    a.set_xticks(x); a.set_xticklabels([f'{p}%' for p in PR[:5]]); a.set_xlabel('Poison rate')
    a.set_title(dn, fontweight='bold'); a.grid(axis='x', visible=False)
ax[0].set_ylabel('Poisoned passages reaching\nthe generator (mean / query) ↓')
legend_top(fig, ax[0], 3); fig.tight_layout()
save(fig, 'fig3_poisoned_passages_reaching_llm')

# ---------- latency ----------
fig, ax = plt.subplots(1, 2, figsize=(10, 3.2), gridspec_kw=dict(width_ratios=[1, 1.5]))
a = ax[0]; x = np.arange(3)
for k, s in enumerate(['vanilla', 'trustrag', 'poisonguard_v5']):
    v = [summ[(s, ds)]['sec'] for ds, _ in DS]
    a.bar(x + (k - 1) * 0.27, v, 0.25, color=COL[s], label=NAME[s])
    for xi, vi in zip(x + (k - 1) * 0.27, v):
        a.text(xi, vi + 0.4, f'{vi:.1f}', ha='center', fontsize=7, color=INK2)
a.set_xticks(x); a.set_xticklabels([dn for _, dn in DS]); a.set_ylabel('Seconds per query ↓')
a.grid(axis='x', visible=False); a.legend(loc='upper right', fontsize=7.5)
a.set_title('End-to-end latency (same laptop, llama3.1:8b)', fontsize=9)
# stage breakdown
stages = collections.OrderedDict()
for r in D:
    if r['sys'] == 'poisonguard_v5' and r['step_sec']:
        for k, v in r['step_sec'].items():
            stages.setdefault(k, []).append(v)
nice = {'input_normalization': 'Input normalisation', 'query_injection_gate': 'Query-injection gate',
        'context_injection_filter': 'Context-injection filter', 'poison_consensus_filter': 'Poison-consensus filter',
        'evidence_arbitration': 'Evidence arbitration', 'output_privacy_filter': 'Output privacy filter',
        'safe_response': 'Safe response'}
means = {k: np.mean(v) for k, v in stages.items()}
a = ax[1]; left = 0
pal = ['#c9c8c2', '#e87ba4', '#eda100', '#2a78d6', '#4a3aa7', '#1baf7a', '#8f8e89']
for (k, v), c in zip(means.items(), pal):
    a.barh(0, v, left=left, color=c, edgecolor='white', linewidth=2, label=f'{nice.get(k,k)} ({v:.1f}s)')
    left += v
a.set_yticks([]); a.set_xlabel('Mean seconds per query (all datasets, all poison rates)')
a.legend(loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=2, fontsize=7.5)
a.set_title('PoisonGuard-RAG per-stage time (logged step timers)', fontsize=9); a.grid(axis='y', visible=False)
fig.tight_layout(); save(fig, 'fig4_latency')

# ---------- risk-score ROC ----------
def roc(scores, labels):
    order = np.argsort(-np.array(scores)); lab = np.array(labels)[order]; sc = np.array(scores)[order]
    P, N = lab.sum(), (1 - lab).sum(); tpr = [0]; fpr = [0]; tp = fp = 0
    for i in range(len(sc)):
        tp += lab[i]; fp += 1 - lab[i]
        if i == len(sc) - 1 or sc[i] != sc[i + 1]:
            tpr.append(tp / P); fpr.append(fp / N)
    auc = np.trapezoid(tpr, fpr)
    return np.array(fpr), np.array(tpr), auc

fig, a = plt.subplots(figsize=(4.2, 3.8))
aucs = {}
for ds, dn in DS:
    rs = [r for p in RATES for r in by[('poisonguard_v5', ds, p)]]
    f, t, auc = roc([r['risk'] or 0 for r in rs], [int(r['adv_topk'] > 0) for r in rs])
    aucs[ds] = auc
    a.plot(f, t, lw=2, label=f'{dn} (AUROC {auc:.3f})', color={'nq': '#2a78d6', 'hotpotqa': '#eb6834', 'msmarco': '#1baf7a'}[ds])
a.plot([0, 1], [0, 1], ls=':', color=INK2, lw=1)
a.set_xlabel('False-positive rate'); a.set_ylabel('True-positive rate')
a.set_title('Pipeline risk score as a poisoning detector', fontsize=9); a.legend(loc='lower right', fontsize=7.5)
fig.tight_layout(); save(fig, 'fig5_risk_roc')

# ---------- decision routes ----------
routes = ['internal_anchored', 'internal_anchored_conflict', 'corroborated', 'best_effort_joint', 'best_effort_closed_book']
rnice = {'internal_anchored': 'Parametric answer agrees with evidence', 'internal_anchored_conflict': 'Parametric answer overrides conflicting evidence',
         'corroborated': 'Answer corroborated by independent passages', 'best_effort_joint': 'Best effort: knowledge + surviving passages',
         'best_effort_closed_book': 'Best effort: closed book (lone passage hidden)'}
rcol = ['#2a78d6', '#4a3aa7', '#1baf7a', '#eda100', '#e87ba4']
fig, ax = plt.subplots(1, 3, figsize=(10, 3.2), sharey=True)
for j, (ds, dn) in enumerate(DS):
    a = ax[j]; bottom = np.zeros(6)
    for rt, c in zip(routes, rcol):
        v = np.array([100 * np.mean([r['decision'] == rt for r in by[('poisonguard_v5', ds, p)]]) for p in RATES])
        a.bar(range(6), v, bottom=bottom, color=c, edgecolor='white', linewidth=1, label=rnice[rt], width=0.75)
        bottom += v
    a.set_xticks(range(6)); a.set_xticklabels([f'{p}%' for p in PR]); a.set_xlabel('Poison rate')
    a.set_title(dn, fontweight='bold'); a.grid(axis='x', visible=False); a.set_ylim(0, 100)
ax[0].set_ylabel('Share of queries (%)')
h, l = ax[0].get_legend_handles_labels(); fig.legend(h, l, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.12), fontsize=7.5)
fig.tight_layout(); save(fig, 'fig6_decision_routes')

# ---------- paired comparison vs TrustRAG ----------
def paired(ds, key, rates):
    a = {(r['qid'], r['p']): r for p in rates for r in by[('poisonguard_v5', ds, p)]}
    b = {(r['qid'], r['p']): r for p in rates for r in by[('trustrag', ds, p)]}
    w = l = t = 0
    for k in a:
        x, y = a[k][key], b[k][key]
        if x and not y: w += 1
        elif y and not x: l += 1
        else: t += 1
    p = binomtest(w, w + l, 0.5).pvalue if w + l else 1.0
    return w, l, t, p

pair = {}
for ds, dn in DS:
    pair[ds] = dict(acc=paired(ds, 'acc', RATES[:5]), asr=paired(ds, 'asr', RATES[:5]),
                    sacc=paired(ds, 'sacc', RATES[:5]), sasr=paired(ds, 'sasr', RATES[:5]))
pair['all'] = {k: tuple(np.sum([pair[d][k][:3] for d, _ in DS], axis=0)) for k in ['acc', 'asr', 'sacc', 'sasr']}
for k in pair['all']:
    w, l, t = pair['all'][k]; pair['all'][k] = (int(w), int(l), int(t), binomtest(int(w), int(w + l), 0.5).pvalue)

fig, ax = plt.subplots(1, 2, figsize=(10, 2.8), sharey=True)
labels = [dn for _, dn in DS] + ['All three']
keys = [d for d, _ in DS] + ['all']
for a, (k, title, good) in zip(ax, [('acc', 'Correct answers (ACC)', 'v4 correct, TrustRAG wrong'),
                                    ('asr', 'Successful attacks (ASR)', 'TrustRAG attacked, v4 not')]):
    y = np.arange(len(keys))[::-1]
    for yi, kk in zip(y, keys):
        w, l, t, p = pair[kk][k]
        win, loss = (w, l) if k == 'acc' else (l, w)
        a.barh(yi, win, color=COL['poisonguard_v5'], height=0.55)
        a.barh(yi, -loss, color=COL['trustrag'], height=0.55)
        a.text(win + 1, yi, f'{win}', va='center', fontsize=7.5, color=INK)
        a.text(-loss - 1, yi, f'{loss}', va='center', ha='right', fontsize=7.5, color=INK)
        a.text(a.get_xlim()[1] if False else 75, yi, f'p={p:.3f}' if p >= 0.001 else 'p<0.001', va='center', fontsize=7, color=INK2)
    a.axvline(0, color=INK2, lw=0.8); a.set_yticks(y); a.set_yticklabels(labels); a.set_xlim(-60, 90); a.set_ylim(-0.6, len(keys)-0.2)
    a.set_title(title, fontsize=9); a.grid(axis='y', visible=False)
    a.set_xlabel('Discordant (question, poison-rate) pairs'); a.text(-58, len(keys)-0.45, '← TrustRAG better', fontsize=7, color=INK2); a.text(2, len(keys)-0.45, 'ours better →', fontsize=7, color=INK2)
fig.tight_layout(); save(fig, 'fig7_paired_vs_trustrag')

json.dump(dict(summ={f'{a}|{b}': v for (a, b), v in summ.items()},
               filt={f'{s}|{ds}': filt(s, ds) for s in ['trustrag', 'poisonguard_v5'] for ds, _ in DS},
               filt_pois={f'{s}|{ds}': filt(s, ds, RATES[:5]) for s in ['trustrag', 'poisonguard_v5'] for ds, _ in DS},
               aucs=aucs, pair=pair,
               cells={f'{s}|{ds}|{p}': [m(s, ds, p, k) for k in ['acc', 'asr', 'sacc', 'sasr']] for s, _ in SYS for ds, _ in DS for p in RATES},
               stages=means), open('/home/claude/stats.json', 'w'), indent=1, default=float)
print('ok')

# ---------- Fig 8: robustness once poison reaches the generator ----------
exp = {}
fig, a = plt.subplots(figsize=(6.2, 3.2)); x = np.arange(3)
for k, s in enumerate(['vanilla', 'trustrag', 'poisonguard_v5']):
    key = 'adv_topk' if s == 'vanilla' else 'adv_gen'
    vals = []
    for ds, _ in DS:
        e = [r for p in RATES[:5] for r in by[(s, ds, p)] if (r[key] or 0) > 0]
        exp[f'{s}|{ds}'] = dict(n=len(e), asr=100 * np.mean([r['asr'] for r in e]), acc=100 * np.mean([r['acc'] for r in e]))
        vals.append(exp[f'{s}|{ds}']['asr'])
    a.bar(x + (k - 1) * 0.27, vals, 0.25, color=COL[s], label=NAME[s])
    for xi, v, (ds, _) in zip(x + (k - 1) * 0.27, vals, DS):
        a.text(xi, v + 1.2, f'{v:.1f}', ha='center', fontsize=7, color=INK)
        a.text(xi, -7, f'n={exp[f"{s}|{ds}"]["n"]}', ha='center', fontsize=6, color=INK2)
a.set_xticks(x); a.set_xticklabels([dn for _, dn in DS]); a.tick_params(axis='x', pad=12)
a.set_ylim(-9, 90); a.set_ylabel('ASR (%) among queries where ≥1\npoisoned passage reached the LLM ↓')
a.grid(axis='x', visible=False); a.legend(loc='upper right', fontsize=7.5)
fig.tight_layout(); save(fig, 'fig8_asr_when_poison_reaches_llm')
st = json.load(open('/home/claude/stats.json')); st['exposed'] = exp
json.dump(st, open('/home/claude/stats.json', 'w'), indent=1, default=float)
