"""Tests for resolving evaluation runs through human review."""

import pytest

from src import database
from src.models import EvaluationInput, RunState
from src.review import ReviewDecision, resolve_human_review


def review_run(database_path):
    """Create and return a run waiting for a human decision."""
    evaluation_input = EvaluationInput(
        question="Should this answer be published?",
        reference="The policy requires a human decision.",
        answer="This answer needs review.",
    )
    run_id = database.create_evaluation_run(
        evaluation_input,
        database_path,
    )
    database.update_evaluation_run_state(
        run_id,
        RunState.HUMAN_REVIEW,
        database_path,
    )
    return run_id


def test_human_reviewer_can_approve_run(tmp_path):
    database_path = tmp_path / "answertrust.db"
    run_id = review_run(database_path)

    updated_run = resolve_human_review(
        run_id,
        ReviewDecision.APPROVE,
        database_path,
    )

    assert updated_run["state"] == RunState.APPROVED.value


def test_human_reviewer_can_reject_run(tmp_path):
    database_path = tmp_path / "answertrust.db"
    run_id = review_run(database_path)

    updated_run = resolve_human_review(
        run_id,
        ReviewDecision.REJECT,
        database_path,
    )

    assert updated_run["state"] == RunState.REJECTED.value


def test_unknown_run_cannot_be_reviewed(tmp_path):
    database_path = tmp_path / "answertrust.db"

    with pytest.raises(KeyError, match="Unknown evaluation run"):
        resolve_human_review(
            "missing-run",
            ReviewDecision.APPROVE,
            database_path,
        )


def test_run_outside_human_review_cannot_be_resolved(tmp_path):
    database_path = tmp_path / "answertrust.db"
    evaluation_input = EvaluationInput(
        question="What is the capital of France?",
        reference="Paris",
        answer="Paris",
    )
    run_id = database.create_evaluation_run(
        evaluation_input,
        database_path,
    )

    with pytest.raises(ValueError, match="HUMAN_REVIEW"):
        resolve_human_review(
            run_id,
            ReviewDecision.APPROVE,
            database_path,
        )

    unchanged_run = database.get_evaluation_run(run_id, database_path)
    assert unchanged_run is not None
    assert unchanged_run["state"] == RunState.RECEIVED.value
