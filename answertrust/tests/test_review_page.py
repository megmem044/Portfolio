"""Interaction tests for the Streamlit human-review page."""

from pathlib import Path
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from src import database, review
from src.models import RunState


PAGE_PATH = (
    Path(__file__).resolve().parent.parent
    / "pages"
    / "1_Human_Review.py"
)


def review_run():
    return {
        "run_id": "run-12345678",
        "evaluation_id": "evaluation-1",
        "state": RunState.HUMAN_REVIEW.value,
        "question": "What is the refund policy?",
        "reference": "Refunds are available within 30 days.",
        "answer": "Customers can request a refund within 30 days.",
    }


def evaluation():
    return {
        "evaluation_id": "evaluation-1",
        "overall_score": 72,
        "main_concern": "The answer may be incomplete.",
        "recommended_action": "Review before publishing.",
        "dimension_scores": [
            {
                "name": "Completeness",
                "score": 65,
                "explanation": "Some policy details are missing.",
                "concerns": ["The answer does not mention exceptions."],
            }
        ],
    }


def mock_page_data(monkeypatch, runs, evaluations):
    runs_mock = Mock(return_value=runs)
    evaluations_mock = Mock(return_value=evaluations)
    monkeypatch.setattr(
        database,
        "get_evaluation_runs",
        runs_mock,
    )
    monkeypatch.setattr(
        database,
        "get_evaluations",
        evaluations_mock,
    )
    return runs_mock, evaluations_mock


def test_empty_review_queue_shows_helpful_message(monkeypatch):
    mock_page_data(monkeypatch, [], [])

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert page.title[0].value == "Human Review"
    assert page.metric[0].value == "0"
    assert page.info[0].value == (
        "No evaluation runs currently require human review."
    )


def test_review_run_displays_context_and_concerns(monkeypatch):
    mock_page_data(monkeypatch, [review_run()], [evaluation()])

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert page.metric[0].value == "1"
    assert any(
        item.value == "**Question:** What is the refund policy?"
        for item in page.markdown
    )
    assert any(
        item.value == "The answer does not mention exceptions."
        for item in page.warning
    )
    assert [button.label for button in page.button] == [
        "Approve",
        "Reject",
    ]


def test_approve_button_resolves_review(monkeypatch):
    runs_mock, _ = mock_page_data(
        monkeypatch,
        [review_run()],
        [evaluation()],
    )
    runs_mock.side_effect = [[review_run()], [review_run()], []]
    resolve_mock = Mock(return_value={"state": "APPROVED"})
    monkeypatch.setattr(review, "resolve_human_review", resolve_mock)

    page = AppTest.from_file(str(PAGE_PATH)).run()
    page.button[0].click().run()

    assert not page.exception
    resolve_mock.assert_called_once()
    assert resolve_mock.call_args.args[0] == "run-12345678"
    assert resolve_mock.call_args.args[1].value == "APPROVE"


def test_reject_button_resolves_review(monkeypatch):
    runs_mock, _ = mock_page_data(
        monkeypatch,
        [review_run()],
        [evaluation()],
    )
    runs_mock.side_effect = [[review_run()], [review_run()], []]
    resolve_mock = Mock(return_value={"state": "REJECTED"})
    monkeypatch.setattr(review, "resolve_human_review", resolve_mock)

    page = AppTest.from_file(str(PAGE_PATH)).run()
    page.button[1].click().run()

    assert not page.exception
    resolve_mock.assert_called_once()
    assert resolve_mock.call_args.args[0] == "run-12345678"
    assert resolve_mock.call_args.args[1].value == "REJECT"
