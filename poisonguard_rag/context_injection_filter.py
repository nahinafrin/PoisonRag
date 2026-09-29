"""Stage 4 - retrieved-context injection filter (indirect prompt injection).

Each passage is scanned with the same DeBERTa-v3 injection detector (LLM-Guard) and
a supersession-cue regex (planted "correction/update" framing). Risk-adaptive
threshold: theta = 0.50, tightened to 0.30 when R > 0.45. Dirty passages are
dropped; the strongest passage score is fused into R."""
from __future__ import annotations

from .query_injection_gate import injection_score
from .state import RAGState
from .supersession_cue import has_supersession_cue

BASE_T, STRICT_T, TIGHTEN_AT, W = 0.50, 0.30, 0.45, 1.0


def run(st: RAGState) -> RAGState:
    if st.blocked or not st.passages:
        return st
    theta = STRICT_T if st.risk > TIGHTEN_AT else BASE_T
    kept, dropped, scores = [], [], []
    for p in st.passages:
        r = injection_score(p)
        scores.append(r)
        if r >= theta or has_supersession_cue(p):
            dropped.append({"r": round(r, 3), "preview": p[:60]})
        else:
            kept.append(p)
    st.passages = kept
    st.meta["context_filter"] = {"theta": theta, "dropped": dropped}
    if scores:
        st.add_risk("context_injection_filter", max(scores), W)
    return st
