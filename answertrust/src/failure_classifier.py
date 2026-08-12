"""Classify evaluation outcomes into AnswerTrust's failure taxonomy."""

from __future__ import annotations

from src.models import Decision, EvaluationResult, FailureType


def classify_result(result: EvaluationResult) -> FailureType | None:
    """Return the intervention reason represented by an evaluation result."""
    if result.dimension_scores[0].name == "Validation":
        return FailureType.INVALID_OUTPUT

    if result.model_status == "unavailable":
        return FailureType.MODEL_UNAVAILABLE

    if result.model_status == "malformed_output":
        return FailureType.INVALID_OUTPUT

    if result.model_status == "error":
        return FailureType.EVALUATION_ERROR

    if result.final_decision == Decision.REVIEW:
        return FailureType.LOW_CONFIDENCE

    scores_by_name = {
        dimension.name: dimension.score
        for dimension in result.dimension_scores
    }
    source_support_score = scores_by_name.get("Source support")
    if (
        result.final_decision == Decision.REJECT
        and source_support_score is not None
        and source_support_score < 50
    ):
        return FailureType.INSUFFICIENT_SUPPORT

    return None


def classify_exception(error: Exception) -> FailureType:
    """Return a stable failure class for an exception from evaluation."""
    if isinstance(error, TimeoutError):
        return FailureType.MODEL_TIMEOUT

    if isinstance(error, (OSError, FileNotFoundError)):
        return FailureType.MODEL_UNAVAILABLE

    if isinstance(error, ValueError):
        return FailureType.INVALID_OUTPUT

    return FailureType.EVALUATION_ERROR
