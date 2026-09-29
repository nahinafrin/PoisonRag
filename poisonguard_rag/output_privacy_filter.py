"""Stage 7 - output privacy filter (data-loss prevention). Never refuses; masks.

Layer 1 Presidio NER + regex (e-mail, phone, card, SSN, IBAN, IP, passport, ...)
Layer 2 deterministic DLP regex (API keys, bearer tokens, AWS keys) with Luhn
        confirmation for card numbers (rejects benign long digit runs).
The Llama-Guard-1B output verdict of the earlier pipeline is removed: on the
TrustRAG benchmark it refused 10/1000 benign answers and caught no attack."""
from __future__ import annotations

import re

from .state import RAGState

ENTITIES = ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "US_SSN", "IBAN_CODE", "IP_ADDRESS",
            "US_PASSPORT", "US_DRIVER_LICENSE", "CRYPTO", "MEDICAL_LICENSE", "US_BANK_NUMBER"]
DLP = {"CARD": re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), "US_SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
       "AWS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "API_KEY": re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9]{16,}\b"),
       "BEARER": re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}\b")}
_ENGINES = None


def luhn(num: str) -> bool:
    d = [int(c) for c in num if c.isdigit()]
    if not 13 <= len(d) <= 19:
        return False
    s, par = 0, len(d) % 2
    for i, x in enumerate(d):
        if i % 2 == par:
            x = x * 2 - 9 if x * 2 > 9 else x * 2
        s += x
    return s % 10 == 0


def mask(text: str) -> tuple[str, list]:
    global _ENGINES
    hits = []
    if _ENGINES is None:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        _ENGINES = (AnalyzerEngine(), AnonymizerEngine())
    an, anon = _ENGINES
    res = [r for r in an.analyze(text=text, language="en") if r.entity_type in ENTITIES]
    if res:
        hits += [{"type": r.entity_type, "layer": "presidio"} for r in res]
        text = anon.anonymize(text=text, analyzer_results=res).text
    for kind, pat in DLP.items():
        for m in list(pat.finditer(text)):
            if kind == "CARD" and not luhn(m.group(0)):
                continue
            hits.append({"type": kind, "layer": "dlp"})
            text = text.replace(m.group(0), f"[REDACTED:{kind}]")
    return text, hits


def run(st: RAGState) -> RAGState:
    if st.blocked or st.abstained or not st.answer:
        return st
    st.answer, hits = mask(st.answer)
    st.meta["privacy_hits"] = hits
    return st
