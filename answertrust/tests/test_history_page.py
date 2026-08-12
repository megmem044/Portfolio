"""Interaction tests for the Streamlit evaluation-history page."""

from pathlib import Path
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from src import database
from src.models import Decision


PAGE_PATH = (
    Path(__file__).resolve().parent.parent
    / "pages"
    / "2_Evaluation_History.py"
)


def test_empty_history_shows_helpful_message(monkeypatch):
    monkeypatch.setattr(database, "get_evaluations", Mock(return_value=[]))
    monkeypatch.setattr(
        database,
        "get_evaluation_runs",
        Mock(return_value=[]),
    )

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert page.title[0].value == "Evaluation History"
    assert page.info[0].value == "No saved evaluations match this filter."


def test_saved_evaluation_is_rendered(monkeypatch):
    record = {
        "evaluation_id": "test-id",
        "timestamp": "2026-08-06T19:00:00+00:00",
        "question": "What is the capital of France?",
        "reference": "Paris",
        "answer": "Paris",
        "overall_score": 95,
        "final_decision": "PUBLISH",
        "dimension_scores": [
            {
                "name": "Source support",
                "score": 100,
                "explanation": "The answer matches the reference.",
                "concerns": [],
            }
        ],
        "main_concern": "No major concerns were detected.",
        "recommended_action": "The answer can be published.",
    }
    monkeypatch.setattr(
        database,
        "get_evaluations",
        Mock(return_value=[record]),
    )
    monkeypatch.setattr(
        database,
        "get_evaluation_runs",
        Mock(return_value=[]),
    )

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert any(
        markdown.value == "**Question:** What is the capital of France?"
        for markdown in page.markdown
    )
    assert any(
        caption.value == "The answer matches the reference."
        for caption in page.caption
    )
    assert any(
        markdown.value == "**Workflow state:** LEGACY"
        for markdown in page.markdown
    )
    assert any(
        caption.value
        == "This evaluation predates persistent workflow runs."
        for caption in page.caption
    )


def test_linked_run_state_and_id_are_rendered(monkeypatch):
    record = {
        "evaluation_id": "evaluation-1",
        "timestamp": "2026-08-06T19:00:00+00:00",
        "question": "What is the capital of France?",
        "reference": "Paris",
        "answer": "Paris",
        "overall_score": 95,
        "final_decision": "PUBLISH",
        "dimension_scores": [],
        "main_concern": "No major concerns were detected.",
        "recommended_action": "The answer can be published.",
    }
    run = {
        "run_id": "run-1",
        "evaluation_id": "evaluation-1",
        "state": "APPROVED",
    }
    monkeypatch.setattr(
        database,
        "get_evaluations",
        Mock(return_value=[record]),
    )
    monkeypatch.setattr(
        database,
        "get_evaluation_runs",
        Mock(return_value=[run]),
    )

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert any(
        markdown.value == "**Workflow state:** APPROVED"
        for markdown in page.markdown
    )
    assert any(
        caption.value == "Run ID: run-1"
        for caption in page.caption
    )


def test_decision_filter_is_passed_to_database(monkeypatch):
    get_mock = Mock(return_value=[])
    monkeypatch.setattr(database, "get_evaluations", get_mock)
    monkeypatch.setattr(
        database,
        "get_evaluation_runs",
        Mock(return_value=[]),
    )
    page = AppTest.from_file(str(PAGE_PATH)).run()

    page.selectbox[0].select("REJECT").run()

    assert not page.exception
    assert get_mock.call_args.args[1] == Decision.REJECT


def classified_record():
    return {
        "evaluation_id": "evaluation-1",
        "timestamp": "2026-08-06T19:00:00+00:00",
        "question": "What does the policy allow?",
        "reference": "The policy allows returns within 30 days.",
        "answer": "Returns may be allowed.",
        "overall_score": 70,
        "final_decision": "REVIEW",
        "dimension_scores": [],
        "main_concern": "The answer is incomplete.",
        "recommended_action": "Review before publishing.",
    }


def test_failure_classification_and_reason_are_rendered(monkeypatch):
    run = {
        "run_id": "run-1",
        "evaluation_id": "evaluation-1",
        "state": "HUMAN_REVIEW",
        "failure_type": "LOW_CONFIDENCE",
        "failure_message": "The answer is incomplete.",
    }
    monkeypatch.setattr(
        database,
        "get_evaluations",
        Mock(return_value=[classified_record()]),
    )
    monkeypatch.setattr(
        database,
        "get_evaluation_runs",
        Mock(return_value=[run]),
    )

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert any(
        warning.value == "**Run classification:** Low confidence"
        for warning in page.warning
    )
    assert any(
        markdown.value
        == "**Classification reason:** The answer is incomplete."
        for markdown in page.markdown
    )


def test_model_unavailable_shows_fallback_notice(monkeypatch):
    record = classified_record()
    record["final_decision"] = "PUBLISH"
    run = {
        "run_id": "run-2",
        "evaluation_id": "evaluation-1",
        "state": "APPROVED",
        "failure_type": "MODEL_UNAVAILABLE",
        "failure_message": "Deterministic evaluation was used.",
    }
    monkeypatch.setattr(
        database,
        "get_evaluations",
        Mock(return_value=[record]),
    )
    monkeypatch.setattr(
        database,
        "get_evaluation_runs",
        Mock(return_value=[run]),
    )

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert any(
        "Deterministic fallback used" in info.value
        for info in page.info
    )
