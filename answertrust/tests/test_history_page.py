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


def test_decision_filter_is_passed_to_database(monkeypatch):
    get_mock = Mock(return_value=[])
    monkeypatch.setattr(database, "get_evaluations", get_mock)
    page = AppTest.from_file(str(PAGE_PATH)).run()

    page.selectbox[0].select("REJECT").run()

    assert not page.exception
    assert get_mock.call_args.args[1] == Decision.REJECT
