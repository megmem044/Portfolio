"""Interaction tests for the Streamlit quality dashboard."""

from pathlib import Path
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from src import dashboard, database


PAGE_PATH = (
    Path(__file__).resolve().parent.parent
    / "pages"
    / "3_Quality_Dashboard.py"
)


def test_dashboard_handles_empty_local_data(monkeypatch):
    monkeypatch.setattr(database, "get_evaluations", Mock(return_value=[]))
    monkeypatch.setattr(
        dashboard,
        "load_experiment_results",
        Mock(side_effect=FileNotFoundError),
    )

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    assert page.title[0].value == "Quality Dashboard"
    assert page.metric[0].value == "0"
    assert len(page.info) == 2


def test_dashboard_displays_experiment_metrics(monkeypatch):
    monkeypatch.setattr(database, "get_evaluations", Mock(return_value=[]))
    rows = [
        {
            "expected_decision": "REJECT",
            "actual_decision": "REJECT",
            "category": "unsupported",
            "correct": True,
            "latency_ms": 1,
        }
    ]
    monkeypatch.setattr(
        dashboard,
        "load_experiment_results",
        Mock(return_value=rows),
    )

    page = AppTest.from_file(str(PAGE_PATH)).run()

    assert not page.exception
    metric_values = [metric.value for metric in page.metric]
    assert "100.0%" in metric_values
    assert "0.0%" in metric_values
