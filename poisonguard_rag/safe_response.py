"""Stage 8 - safe response: formatted answer, transparent abstention, or fixed refusal."""
from __future__ import annotations

import re

from .state import RAGState

REFUSAL = ("I'm sorry, I can't respond to that request because it appears to contain an instruction-"
           "injection attempt.")
ABSTENTION = "I can't give a trustworthy answer to that from the available sources."


def run(st: RAGState) -> RAGState:
    if st.blocked:
        st.final_response = REFUSAL
    elif st.abstained or not st.answer.strip():
        st.final_response = ABSTENTION
    else:
        t = re.sub(r"[ \t]+", " ", st.answer).strip()
        st.final_response = t if t[-1:] in ".!?\"')]}" else t + "."
    return st
