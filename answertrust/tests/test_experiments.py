"""Tests for repeatable offline evaluator experiments."""

import csv

import pytest

from src.experiments import (
    PROMPT_COMPARISON_FIELDS,
    RESULT_FIELDS,
    calculate_prompt_comparison_metrics,
    calculate_metrics,
    run_prompt_comparison,
    run_experiment,
    write_prompt_comparison,
    write_results,
)
from src.models import Decision, TransformerResult


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

    assert len(rows) == 30
    assert metrics["total_examples"] == 30
    assert output_path.exists()
    assert all(set(row) == set(RESULT_FIELDS) for row in rows)


class FakePromptEvaluator:
    def evaluate(self, evaluation_input, prompt_version):
        decision = (
            Decision.REVIEW if prompt_version == "baseline" else Decision.PUBLISH
        )
        return TransformerResult(
            explanation=f"{prompt_version} explanation",
            suggested_decision=decision,
            prompt_version=prompt_version,
            model_name="fake-model",
            status="generated",
            latency_ms=5,
        )


def test_prompt_comparison_records_both_prompt_versions(tmp_path):
    output_path = tmp_path / "prompt_results.csv"

    rows, metrics = run_prompt_comparison(
        FakePromptEvaluator(),
        output_path=output_path,
    )

    assert len(rows) == 60
    assert {row["prompt_version"] for row in rows} == {"baseline", "safety"}
    assert all(set(row) == set(PROMPT_COMPARISON_FIELDS) for row in rows)
    assert metrics["baseline"]["availability_rate_pct"] == 100.0
    assert output_path.exists()


def test_prompt_metrics_do_not_invent_unavailable_accuracy():
    rows = [
        {
            "prompt_version": "baseline",
            "model_status": "unavailable",
            "model_matches_expected": "",
            "agrees_with_deterministic": "",
            "transformer_latency_ms": 2,
        }
    ]

    metrics = calculate_prompt_comparison_metrics(rows)

    assert metrics["baseline"]["availability_rate_pct"] == 0.0
    assert metrics["baseline"]["model_accuracy_pct"] == 0.0
    assert metrics["safety"]["total_attempts"] == 0


def test_write_prompt_comparison_creates_required_columns(tmp_path):
    path = tmp_path / "nested" / "prompt_results.csv"
    row = {field: "value" for field in PROMPT_COMPARISON_FIELDS}

    write_prompt_comparison([row], path)

    with path.open(newline="", encoding="utf-8") as results_file:
        reader = csv.DictReader(results_file)
        assert reader.fieldnames == PROMPT_COMPARISON_FIELDS
