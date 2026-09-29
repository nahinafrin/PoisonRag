"""Per-query state threaded through every stage, plus the adaptive-risk algebra.

Risk model: every detector i emits r_i in [0,1]; the running risk R is updated by
weighted noisy-OR, so evidence only accumulates and one confident detector is
enough to raise it:
        R_t = 1 - (1 - R_{t-1}) (1 - w_t r_t)
Downstream stages read R to tighten themselves (adaptive cascade).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def noisy_or(prev: float, r: float, w: float = 1.0) -> float:
    return 1.0 - (1.0 - prev) * (1.0 - w * max(0.0, min(1.0, r)))


@dataclass
class RAGState:
    question: str
    prompt: str = ""                         # normalized question
    risk: float = 0.0                        # adaptive risk R
    risk_trace: list = field(default_factory=list)
    passages: list[str] = field(default_factory=list)
    passage_trust: dict = field(default_factory=dict)   # passage -> 1 - r_i
    passage_group: dict = field(default_factory=dict)   # passage -> coordinated-group id
    answer: str = ""
    final_response: str = ""
    blocked: bool = False
    block_stage: str = ""
    block_reason: str = ""
    abstained: bool = False
    abstain_reason: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def add_risk(self, stage: str, r: float, w: float = 1.0) -> None:
        self.risk = noisy_or(self.risk, r, w)
        self.risk_trace.append({"stage": stage, "r": round(float(r), 4), "w": w,
                                "R": round(self.risk, 4)})

    def block(self, stage: str, reason: str) -> None:
        self.blocked, self.block_stage, self.block_reason = True, stage, reason

    def abstain(self, reason: str) -> None:
        self.abstained, self.abstain_reason = True, reason
