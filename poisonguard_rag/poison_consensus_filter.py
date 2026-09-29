"""Stage 5 - poison-consensus filter (knowledge-corruption channel).

Injection detectors cannot see PoisonedRAG-style poison: it is fluent, factual-
sounding text with no instruction. Two structural signatures of retrieval-
optimised poison are scored per passage (no LLM call, thresholds fixed a priori):

  q_i  query echo     LCS(question tokens, passage prefix)/|question tokens|
                      (poison is written as S = question (+) I to maximise retrieval)
  c_i  coordination   max_j sig((cos_ij-0.85)/0.02) * sig((ROUGE-L_ij-0.25)/0.03)
                      (several poisons for one target are near-paraphrases; 0.85 /
                      0.25 are TrustRAG's published thresholds, reused unchanged)
  r_i = 1 - (1 - 0.9 sig((q_i-0.75)/0.05)) (1 - 0.9 c_i)        (noisy-OR)

Passages with r_i >= 0.5 are dropped; R <- noisy-OR(R, max_i r_i, w=0.8).
Coordinated passages are recorded as ONE source group, so the arbitration stage
counts them as a single witness (sybil resistance).
"""
from __future__ import annotations

import math
import re

import numpy as np

from .state import RAGState

ECHO_C, ECHO_S, COS_T, COS_S, ROUGE_T, ROUGE_S = 0.75, 0.05, 0.85, 0.02, 0.25, 0.03
W_ECHO, W_COORD, W_POISON, DROP = 0.9, 0.9, 0.8, 0.5
EMBED_MODEL = "BAAI/bge-m3"

_TOK = re.compile(r"[a-z0-9]+")
_EMB = None
_ROUGE = None


def _sig(x):
    return 0.0 if x < -60 else 1.0 if x > 60 else 1.0 / (1.0 + math.exp(-x))


def _toks(s):
    return _TOK.findall((s or "").lower())


def _lcs(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def query_echo(q, p):
    qt = _toks(q)
    return _lcs(qt, _toks(p)[: len(qt) + 5]) / len(qt) if qt else 0.0


def rouge_l(a, b):
    global _ROUGE
    if _ROUGE is None:
        from rouge_score import rouge_scorer
        _ROUGE = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    return _ROUGE.score(a, b)["rougeL"].fmeasure


def embed(texts):
    global _EMB
    if _EMB is None:
        from sentence_transformers import SentenceTransformer
        _EMB = SentenceTransformer(EMBED_MODEL)
    return np.asarray(_EMB.encode(texts, normalize_embeddings=True))


def score(question, passages):
    n = len(passages)
    echo = [query_echo(question, p) for p in passages]
    coord, pairs = [0.0] * n, {}
    if n >= 2:
        E = embed(passages)
        cos = E @ E.T
        for i in range(n):
            for j in range(i + 1, n):
                v = _sig((float(cos[i, j]) - COS_T) / COS_S) * _sig((rouge_l(passages[i], passages[j]) - ROUGE_T) / ROUGE_S)
                pairs[(i, j)] = v
                coord[i], coord[j] = max(coord[i], v), max(coord[j], v)
    risk = [1 - (1 - W_ECHO * _sig((e - ECHO_C) / ECHO_S)) * (1 - W_COORD * c) for e, c in zip(echo, coord)]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for (i, j), v in pairs.items():
        if v >= 0.5:
            parent[find(i)] = find(j)
    return echo, coord, risk, [find(i) for i in range(n)]


def run(st: RAGState) -> RAGState:
    if st.blocked or not st.passages:
        return st
    ps = list(st.passages)
    echo, coord, risk, group = score(st.prompt, ps)
    keep = [i for i, r in enumerate(risk) if r < DROP]
    st.passages = [ps[i] for i in keep]
    for i in keep:
        st.passage_trust[ps[i]] = round(1 - risk[i], 4)
        st.passage_group[ps[i]] = int(group[i])
    st.meta["poison_consensus"] = {"echo": [round(x, 3) for x in echo], "coord": [round(x, 3) for x in coord],
                                   "risk": [round(x, 3) for x in risk], "group": group,
                                   "dropped": [i for i in range(len(ps)) if i not in keep]}
    st.add_risk("poison_consensus_filter", max(risk), W_POISON)
    return st
