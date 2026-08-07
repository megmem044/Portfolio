"""Coordinate AnswerTrust's deterministic evaluation pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from src.clarity import evaluate_clarity
from src.completeness import evaluate_completeness
from src.decision_engine import make_decision
from src.models import (
    Decision,
    DimensionScore,
    EvaluationInput,
    EvaluationResult,
)
from src.relevance import evaluate_relevance
from src.scoring import calculate_overall_score
from src.source_support import evaluate_source_support
from src.uncertainty import evaluate_uncertainty
from src.validation import validate_input


def _recommended_action(decision: Decision) -> str:
    """Return a clear next action for a publication decision."""
    actions = {
        Decision.PUBLISH: "The answer can be published.",
        Decision.REVIEW: "Review and revise the identified concerns.",
        Decision.REJECT: "Do not publish this answer without substantial revision.",
    }
    return actions[decision]


def _build_result(
    evaluation_input: EvaluationInput,
    dimension_scores: list[DimensionScore],
    overall_score: int,
    decision: Decision,
    started_at: float,
) -> EvaluationResult:
    """Build the shared result object returned by every evaluation path."""
    concerns = [
        concern
        for dimension in dimension_scores
        for concern in dimension.concerns
    ]
    latency_ms = round((perf_counter() - started_at) * 1000)

    return EvaluationResult(
        evaluation_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc),
        overall_score=overall_score,
        final_decision=decision,
        dimension_scores=dimension_scores,
        main_concern=(
            concerns[0] if concerns else "No major concerns were detected."
        ),
        explanation=" ".join(
            dimension.explanation for dimension in dimension_scores
        ),
        recommended_action=_recommended_action(decision),
        deterministic_latency_ms=latency_ms,
        transformer_latency_ms=0,
        total_latency_ms=latency_ms,
        prompt_version=evaluation_input.prompt_version,
        model_status="not_used",
    )


def evaluate_answer(evaluation_input: EvaluationInput) -> EvaluationResult:
    """Evaluate an answer and return scores, concerns, and a decision."""
    started_at = perf_counter()
    errors = validate_input(evaluation_input)

    if errors:
        validation_score = DimensionScore(
            name="Validation",
            score=0,
            explanation="The submitted input could not be evaluated.",
            concerns=errors,
        )
        return _build_result(
            evaluation_input=evaluation_input,
            dimension_scores=[validation_score],
            overall_score=0,
            decision=Decision.REJECT,
            started_at=started_at,
        )

    dimension_scores = [
        evaluate_relevance(
            evaluation_input.question,
            evaluation_input.reference,
            evaluation_input.answer,
        ),
        evaluate_source_support(
            evaluation_input.reference,
            evaluation_input.answer,
        ),
        evaluate_completeness(
            evaluation_input.question,
            evaluation_input.reference,
            evaluation_input.answer,
        ),
        evaluate_clarity(evaluation_input.answer),
        evaluate_uncertainty(
            evaluation_input.reference,
            evaluation_input.answer,
        ),
    ]

    overall_score = calculate_overall_score(dimension_scores)
    decision = make_decision(overall_score, dimension_scores)

    return _build_result(
        evaluation_input=evaluation_input,
        dimension_scores=dimension_scores,
        overall_score=overall_score,
        decision=decision,
        started_at=started_at,
    )
