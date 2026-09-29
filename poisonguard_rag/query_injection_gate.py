"""Stage 2 - query-side prompt-injection gate (LLM-Guard / DeBERTa-v3
protectai/deberta-v3-base-prompt-injection-v2).

r_q = detector probability. Hard block only when r_q >= 0.90 (the C3RF hard
override); otherwise r_q is fused into the adaptive risk. The Llama-Guard-1B
content gate of the earlier pipeline is removed: on the TrustRAG benchmark it
blocked 20/1000 benign questions (e.g. "who wrote the song what child is this" ->
S4) and caught no attack."""
from __future__ import annotations

from .state import RAGState

HARD_BLOCK = 0.90
_SCANNER = None


def injection_score(text: str) -> float:
    global _SCANNER
    if _SCANNER is None:
        from llm_guard.input_scanners import PromptInjection
        from llm_guard.input_scanners.prompt_injection import MatchType
        _SCANNER = PromptInjection(threshold=0.5, match_type=MatchType.FULL)
    _s, _valid, risk = _SCANNER.scan(text)
    return float(risk)


def run(st: RAGState) -> RAGState:
    r_q = injection_score(st.prompt)
    st.meta["query_injection"] = round(r_q, 4)
    st.add_risk("query_injection_gate", r_q, 1.0)
    if r_q >= HARD_BLOCK:
        st.block("query_injection_gate", f"prompt injection in query (r={r_q:.2f})")
    return st
