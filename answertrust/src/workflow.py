"""Coordinate persistent run state with AnswerTrust evaluations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from src import database
from src.evaluator import evaluate_answer
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
    except Exception:
        database.update_evaluation_run_state(
            run_id,
            RunState.FAILED,
            database_path,
        )
        raise

    is_valid = result.dimension_scores[0].name != "Validation"
    if is_valid:
        database.save_evaluation(
            evaluation_input,
            result,
            database_path,
        )

    database.update_evaluation_run_state(
        run_id,
        _final_state(result),
        database_path,
        evaluation_id=result.evaluation_id if is_valid else None,
    )
    return run_id, result
