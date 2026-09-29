"""Stage 1 - input normalization (ftfy mojibake repair, hidden/zero-width chars,
whitespace, contraction expansion, decoding of obfuscated payloads). Never blocks:
over-length is recorded, not refused (keeps benign-block rate at 0)."""
from __future__ import annotations

from .state import RAGState
from .text_normalizer import Preprocessor

_PRE = None


def run(st: RAGState) -> RAGState:
    global _PRE
    if _PRE is None:
        _PRE = Preprocessor(min_len=1, max_len=4000, use_spacy=True, lemmatize=False)
    st.prompt = _PRE.normalize_text(st.question) or st.question
    st.meta["length_verdict"] = _PRE.length_ok(st.prompt) or "ok"
    return st
