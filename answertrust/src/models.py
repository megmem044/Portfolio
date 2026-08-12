"""Typed data structures shared across AnswerTrust components."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Decision(str, Enum):
    PUBLISH = "PUBLISH"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class RunState(str, Enum):
    """Durable lifecycle states for one answer evaluation run."""

    RECEIVED = "RECEIVED"
    EVALUATING = "EVALUATING"
    RETRYING = "RETRYING"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class FailureType(str, Enum):
    """Known reasons an evaluation run may fail or need intervention."""

    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    INVALID_OUTPUT = "INVALID_OUTPUT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    INSUFFICIENT_SUPPORT = "INSUFFICIENT_SUPPORT"
    EVALUATION_ERROR = "EVALUATION_ERROR"


@dataclass
class EvaluationInput:
    question: str
    reference: str
    answer: str
    prompt_version: str = "baseline"


@dataclass
class DimensionScore:
    name: str
    score: int
    explanation: str
    concerns: list[str]


@dataclass
class TransformerResult:
    """Supplemental output from the optional local transformer."""

    explanation: str
    suggested_decision: Decision | None
    prompt_version: str
    model_name: str
    status: str
    latency_ms: int
    raw_output: str = ""


@dataclass
class EvaluationResult:
    evaluation_id: str
    timestamp: datetime
    overall_score: int
    final_decision: Decision
    dimension_scores: list[DimensionScore]
    main_concern: str
    explanation: str
    recommended_action: str
    # Time used by AnswerTrust's rule-based scoring, measured in milliseconds.
    deterministic_latency_ms: int
    # Time used by the optional local AI model, measured in milliseconds.
    transformer_latency_ms: int
    # Total time for the complete evaluation, measured in milliseconds.
    total_latency_ms: int
    prompt_version: str
    model_status: str

