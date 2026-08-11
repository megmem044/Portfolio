"""Tests for persistent evaluation-run orchestration."""

from dataclasses import replace

import pytest

from src import database
from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput, RunState
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


def test_reject_decision_finishes_as_rejected(tmp_path):
    database_path = tmp_path / "answertrust.db"

    run_id, result = execute_evaluation_run(
        supported_input(),
        database_path,
        evaluator=evaluator_with_decision(Decision.REJECT),
    )
    run = database.get_evaluation_run(run_id, database_path)

    assert run is not None
    assert run["state"] == RunState.REJECTED.value
    assert run["evaluation_id"] == result.evaluation_id


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
