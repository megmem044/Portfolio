"""Coordinate AnswerTrust's deterministic evaluation pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import TYPE_CHECKING
from uuid import uuid4

from src.clarity import evaluate_clarity
from src.completeness import evaluate_completeness
from src.decision_engine import make_decision
from src.models import (
    Decision,
    DimensionScore,
    EvaluationInput,
    EvaluationResult,
    TransformerResult,
)
from src.relevance import evaluate_relevance
from src.scoring import calculate_overall_score
from src.source_support import evaluate_source_support
from src.uncertainty import evaluate_uncertainty
from src.validation import validate_input

if TYPE_CHECKING:
    from src.transformer_evaluator import LocalTransformerEvaluator


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
    deterministic_latency_ms: int,
    transformer_result: TransformerResult | None = None,
) -> EvaluationResult:
    """Build the shared result object returned by every evaluation path."""
    concerns = [
        concern
        for dimension in dimension_scores
        for concern in dimension.concerns
    ]
    deterministic_explanation = " ".join(
        dimension.explanation for dimension in dimension_scores
    )
    use_transformer_output = (
        transformer_result is not None
        and transformer_result.status == "generated"
    )
    transformer_latency_ms = (
        transformer_result.latency_ms if transformer_result else 0
    )
    model_status = transformer_result.status if transformer_result else "not_used"
    total_latency_ms = round((perf_counter() - started_at) * 1000)

    return EvaluationResult(
        evaluation_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc),
        overall_score=overall_score,
        final_decision=decision,
        dimension_scores=dimension_scores,
        main_concern=(
            concerns[0] if concerns else "No major concerns were detected."
        ),
        explanation=(
            transformer_result.explanation
            if use_transformer_output
            else deterministic_explanation
        ),
        recommended_action=_recommended_action(decision),
        deterministic_latency_ms=deterministic_latency_ms,
        transformer_latency_ms=transformer_latency_ms,
        total_latency_ms=total_latency_ms,
        prompt_version=evaluation_input.prompt_version,
        model_status=model_status,
    )


def evaluate_answer(
    evaluation_input: EvaluationInput,
    transformer_evaluator: "LocalTransformerEvaluator | None" = None,
) -> EvaluationResult:
    """Evaluate an answer and return scores, concerns, and a decision."""
    started_at = perf_counter()
    errors = validate_input(evaluation_input)

    if errors:
        deterministic_latency_ms = round((perf_counter() - started_at) * 1000)
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
            deterministic_latency_ms=deterministic_latency_ms,
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
    deterministic_latency_ms = round((perf_counter() - started_at) * 1000)
    transformer_result = None
    if transformer_evaluator is not None:
        transformer_result = transformer_evaluator.evaluate(
            evaluation_input,
            evaluation_input.prompt_version,
        )

    return _build_result(
        evaluation_input=evaluation_input,
        dimension_scores=dimension_scores,
        overall_score=overall_score,
        decision=decision,
        started_at=started_at,
        deterministic_latency_ms=deterministic_latency_ms,
        transformer_result=transformer_result,
    )
