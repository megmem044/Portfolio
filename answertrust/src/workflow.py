"""Coordinate persistent run state with AnswerTrust evaluations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from src import database
from src.evaluator import evaluate_answer
from src.failure_classifier import classify_exception, classify_result
from src.models import (
    Decision,
    EvaluationInput,
    EvaluationResult,
    RunState,
)

if TYPE_CHECKING:
    from src.transformer_evaluator import LocalTransformerEvaluator


Evaluator = Callable[..., EvaluationResult]


def _final_state(result: EvaluationResult) -> RunState:
    """Map an evaluation decision to its workflow state."""
    states = {
        Decision.PUBLISH: RunState.APPROVED,
        Decision.REVIEW: RunState.HUMAN_REVIEW,
        Decision.REJECT: RunState.REJECTED,
    }
    return states[result.final_decision]


def execute_evaluation_run(
    evaluation_input: EvaluationInput,
    database_path: Path,
    transformer_evaluator: "LocalTransformerEvaluator | None" = None,
    evaluator: Evaluator = evaluate_answer,
) -> tuple[str, EvaluationResult]:
    """Evaluate an answer while persisting its current workflow state."""
    run_id = database.create_evaluation_run(
        evaluation_input,
        database_path,
    )
    database.update_evaluation_run_state(
        run_id,
        RunState.EVALUATING,
        database_path,
    )

    try:
        result = evaluator(
            evaluation_input,
            transformer_evaluator=transformer_evaluator,
        )
    except Exception as error:
        database.update_evaluation_run_state(
            run_id,
            RunState.FAILED,
            database_path,
            failure_type=classify_exception(error),
            failure_message=str(error) or type(error).__name__,
        )
        raise

    is_valid = result.dimension_scores[0].name != "Validation"
    if is_valid:
        database.save_evaluation(
            evaluation_input,
            result,
            database_path,
        )

    failure_type = classify_result(result)
    failure_message = None
    if failure_type is not None:
        failure_message = {
            "MODEL_UNAVAILABLE": (
                "The optional model was unavailable; deterministic "
                "evaluation was used."
            ),
            "INVALID_OUTPUT": (
                "The submitted input or optional model output was invalid."
            ),
            "LOW_CONFIDENCE": result.main_concern,
            "INSUFFICIENT_SUPPORT": result.main_concern,
            "EVALUATION_ERROR": (
                "The optional model encountered an evaluation error."
            ),
        }.get(failure_type.value, result.main_concern)

    database.update_evaluation_run_state(
        run_id,
        _final_state(result),
        database_path,
        evaluation_id=result.evaluation_id if is_valid else None,
        failure_type=failure_type,
        failure_message=failure_message,
    )
    return run_id, result
