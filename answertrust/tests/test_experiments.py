"""Tests for repeatable offline evaluator experiments."""

import csv

import pytest

from src.experiments import (
    RESULT_FIELDS,
    calculate_metrics,
    run_experiment,
    write_results,
)


def result_row(
    expected: str,
    actual: str,
    category: str = "supported",
    latency_ms: int = 2,
) -> dict:
    return {
        "expected_decision": expected,
        "actual_decision": actual,
        "category": category,
        "correct": expected == actual,
        "latency_ms": latency_ms,
    }


def test_metrics_calculate_accuracy_and_false_publish_rate():
    rows = [
        result_row("PUBLISH", "PUBLISH"),
        result_row("REJECT", "PUBLISH", "unsupported"),
        result_row("REJECT", "REJECT", "irrelevant"),
        result_row("REVIEW", "REVIEW", "partially_supported"),
    ]

    metrics = calculate_metrics(rows)

    assert metrics["decision_accuracy_pct"] == 75.0
    assert metrics["false_publish_rate_pct"] == 50.0
    assert metrics["review_rate_pct"] == 25.0


def test_metrics_calculate_unsupported_detection_rate():
    rows = [
        result_row("REJECT", "REJECT", "unsupported"),
        result_row("REJECT", "REVIEW", "unsupported"),
    ]

    metrics = calculate_metrics(rows)

    assert metrics["unsupported_detection_rate_pct"] == 50.0


def test_empty_metrics_do_not_divide_by_zero():
    metrics = calculate_metrics([])

    assert metrics["decision_accuracy_pct"] == 0.0
    assert metrics["false_publish_rate_pct"] == 0.0
    assert metrics["average_latency_ms"] == 0.0


def test_write_results_creates_folder_and_required_columns(tmp_path):
    output_path = tmp_path / "nested" / "results.csv"
    row = {field: "value" for field in RESULT_FIELDS}

    write_results([row], output_path)

    assert output_path.exists()
    with output_path.open(newline="", encoding="utf-8") as results_file:
        reader = csv.DictReader(results_file)
        assert reader.fieldnames == RESULT_FIELDS
        assert len(list(reader)) == 1


def test_run_experiment_rejects_invalid_dataset(tmp_path):
    with pytest.raises(ValueError, match="Invalid evaluation examples"):
        run_experiment(
            examples=[{"id": "incomplete"}],
            output_path=tmp_path / "results.csv",
        )


def test_project_dataset_runs_and_writes_one_row_per_example(tmp_path):
    output_path = tmp_path / "experiment_results.csv"

    rows, metrics = run_experiment(output_path=output_path)

    assert len(rows) == 20
    assert metrics["total_examples"] == 20
    assert output_path.exists()
    assert all(set(row) == set(RESULT_FIELDS) for row in rows)
