"""Domain types for research-grounded answer evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ClaimLabel(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Decision(str, Enum):
    PUBLISH = "PUBLISH"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class RunState(str, Enum):
    RECEIVED = "RECEIVED"
    EVALUATING = "EVALUATING"
    RETRYING = "RETRYING"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class FailureType(str, Enum):
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    EVALUATION_ERROR = "EVALUATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass
class EvaluationInput:
    question: str
    paper_text: str
    answer: str

    @property
    def reference(self) -> str:  # compatibility for callers using the old name
        return self.paper_text


@dataclass
class Evidence:
    section: str
    passage: str
    similarity: float


@dataclass
class ClaimResult:
    claim: str
    label: ClaimLabel
    evidence: list[Evidence]
    explanation: str
    failure_types: list[str] = field(default_factory=list)
    nli_label: str | None = None
    nli_confidence: float | None = None


@dataclass
class DimensionScore:
    name: str
    score: int
    explanation: str
    concerns: list[str]


@dataclass
class EvaluationResult:
    evaluation_id: str
    timestamp: datetime
    overall_score: int
    final_decision: Decision
    claim_results: list[ClaimResult]
    dimension_scores: list[DimensionScore]
    main_concern: str
    explanation: str
    recommended_action: str
    total_latency_ms: int
    deterministic_latency_ms: int = 0
