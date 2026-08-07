"""Interaction tests for the main Streamlit evaluation page."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from src import database

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


@pytest.fixture(autouse=True)
def prevent_real_database_writes(monkeypatch):
    """Keep Streamlit interaction tests isolated from local history."""
    save_mock = Mock()
    monkeypatch.setattr(database, "save_evaluation", save_mock)
    return save_mock


def load_app() -> AppTest:
    """Run a fresh instance of the Streamlit application."""
    app = AppTest.from_file(str(APP_PATH)).run()
    assert not app.exception
    return app


def submit_evaluation(
    app: AppTest,
    question: str,
    reference: str,
    answer: str,
) -> AppTest:
    """Fill and submit the evaluation form."""
    app.text_area[0].input(question)
    app.text_area[1].input(reference)
    app.text_area[2].input(answer)
    app.button[0].click().run()
    assert not app.exception
    return app


def test_app_renders_evaluation_form():
    app = load_app()

    assert app.title[0].value == "AnswerTrust"
    assert [field.label for field in app.text_area] == [
        "Question",
        "Reference information",
        "AI-generated answer",
    ]
    assert app.button[0].label == "Evaluate Answer"


def test_exact_supported_answer_shows_publish_result(
    prevent_real_database_writes,
):
    app = submit_evaluation(
        load_app(),
        "At what temperature does water freeze?",
        "Water freezes at 0 degrees Celsius.",
        "Water freezes at 0 degrees Celsius.",
    )

    assert app.success
    assert app.success[0].value.startswith("PUBLISH")
    assert app.metric[0].label == "Overall score"
    assert app.metric[0].value.endswith("/100")
    assert len(app.caption) == 6
    assert app.caption[-1].value == "Evaluation saved to local history."
    prevent_real_database_writes.assert_called_once()


def test_partially_supported_answer_shows_review_result():
    app = submit_evaluation(
        load_app(),
        "What are the main benefits of regular exercise?",
        (
            "Regular exercise can improve cardiovascular health, strengthen "
            "muscles, support mental well-being, and help maintain a healthy weight."
        ),
        "Regular exercise can improve cardiovascular health.",
    )

    assert app.warning
    assert app.warning[0].value.startswith("REVIEW")


def test_unrelated_answer_shows_reject_result():
    app = submit_evaluation(
        load_app(),
        "What are the main benefits of regular exercise?",
        "Regular exercise can improve cardiovascular health.",
        "Whales live in the ocean.",
    )

    assert app.error
    assert app.error[0].value.startswith("REJECT")


def test_empty_submission_shows_validation_messages(
    prevent_real_database_writes,
):
    app = load_app()
    app.button[0].click().run()

    assert not app.exception
    assert len(app.error) == 3
    assert any("question" in error.value.lower() for error in app.error)
    assert any("reference" in error.value.lower() for error in app.error)
    assert any("answer" in error.value.lower() for error in app.error)
    prevent_real_database_writes.assert_not_called()
