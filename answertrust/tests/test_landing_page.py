"""Interaction tests for the AnswerTrust landing page."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


def load_landing_page() -> AppTest:
    page = AppTest.from_file(str(APP_PATH)).run()
    assert not page.exception
    return page


def test_landing_page_has_one_clear_product_message():
    page = load_landing_page()

    assert len(page.button) == 1
    assert page.button[0].label == "Start an evaluation"
    assert any("AnswerTrust" in markdown.value for markdown in page.markdown)
    assert any(
        "checks a generated answer against the evidence" in markdown.value
        for markdown in page.markdown
    )


def test_landing_page_does_not_render_evaluation_fields():
    page = load_landing_page()

    assert len(page.text_area) == 0
    assert len(page.checkbox) == 0
    assert len(page.selectbox) == 0
