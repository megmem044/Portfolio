"""Tests for persistent evaluation-run orchestration."""

from dataclasses import replace

import pytest

from src import database
from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput, FailureType, RunState
from src.workflow import execute_evaluation_run


def supported_input() -> EvaluationInput:
    return EvaluationInput(
        question="What is the capital of France?",
        reference="Paris is the capital of France.",
        answer="Paris is the capital of France.",
    )


def evaluator_with_decision(decision: Decision):
    """Return a test evaluator that forces a specific final decision."""

    def evaluator(evaluation_input, transformer_evaluator=None):
        result = evaluate_answer(evaluation_input)
        return replace(result, final_decision=decision)

    return evaluator


def test_publish_decision_finishes_as_approved(tmp_path):
    database_path = tmp_path / "answertrust.db"

    run_id, result = execute_evaluation_run(
        supported_input(),
        database_path,
    )
    run = database.get_evaluation_run(run_id, database_path)

    assert result.final_decision == Decision.PUBLISH
    assert run is not None
    assert run["state"] == RunState.APPROVED.value
    assert run["evaluation_id"] == result.evaluation_id


def test_review_decision_finishes_in_human_review(tmp_path):
    database_path = tmp_path / "answertrust.db"

    run_id, result = execute_evaluation_run(
        supported_input(),
        database_path,
        evaluator=evaluator_with_decision(Decision.REVIEW),
    )
    run = database.get_evaluation_run(run_id, database_path)

    assert run is not None
    assert run["state"] == RunState.HUMAN_REVIEW.value
    assert run["evaluation_id"] == result.evaluation_id
    assert run["failure_type"] == FailureType.LOW_CONFIDENCE.value
    assert run["failure_message"] == result.main_concern


def test_reject_decision_finishes_as_rejected(tmp_path):
    database_path = tmp_path / "answertrust.db"

    def insufficient_support_evaluator(
        evaluation_input,
        transformer_evaluator=None,
    ):
        result = evaluate_answer(evaluation_input)
        weak_scores = [
            replace(dimension, score=20)
            if dimension.name == "Source support"
            else dimension
            for dimension in result.dimension_scores
        ]
        return replace(
            result,
            final_decision=Decision.REJECT,
            dimension_scores=weak_scores,
        )

    run_id, result = execute_evaluation_run(
        supported_input(),
        database_path,
        evaluator=insufficient_support_evaluator,
    )
    run = database.get_evaluation_run(run_id, database_path)

    assert run is not None
    assert run["state"] == RunState.REJECTED.value
    assert run["evaluation_id"] == result.evaluation_id
    assert (
        run["failure_type"]
        == FailureType.INSUFFICIENT_SUPPORT.value
    )


def test_model_unavailable_records_deterministic_fallback(tmp_path):
    database_path = tmp_path / "answertrust.db"

    def unavailable_model_evaluator(
        evaluation_input,
        transformer_evaluator=None,
    ):
        return replace(
            evaluate_answer(evaluation_input),
            model_status="unavailable",
        )

    run_id, _ = execute_evaluation_run(
        supported_input(),
        database_path,
        evaluator=unavailable_model_evaluator,
    )
    run = database.get_evaluation_run(run_id, database_path)

    assert run is not None
    assert run["state"] == RunState.APPROVED.value
    assert run["failure_type"] == FailureType.MODEL_UNAVAILABLE.value
    assert "deterministic evaluation" in run["failure_message"]


def test_evaluator_exception_finishes_as_failed(tmp_path, monkeypatch):
    database_path = tmp_path / "answertrust.db"
    created_run_ids = []
    original_create = database.create_evaluation_run

    def capture_created_run(evaluation_input, path):
        run_id = original_create(evaluation_input, path)
        created_run_ids.append(run_id)
        return run_id

    def failing_evaluator(evaluation_input, transformer_evaluator=None):
        raise RuntimeError("evaluation unavailable")

    monkeypatch.setattr(
        database,
        "create_evaluation_run",
        capture_created_run,
    )

    with pytest.raises(RuntimeError, match="evaluation unavailable"):
        execute_evaluation_run(
            supported_input(),
            database_path,
            evaluator=failing_evaluator,
        )

    run = database.get_evaluation_run(created_run_ids[0], database_path)
    assert run is not None
    assert run["state"] == RunState.FAILED.value
    assert run["evaluation_id"] is None
    assert run["failure_type"] == FailureType.EVALUATION_ERROR.value
    assert run["failure_message"] == "evaluation unavailable"
