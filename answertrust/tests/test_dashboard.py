"""Tests for quality-dashboard data preparation."""

import csv

from src.dashboard import (
    load_experiment_results,
    load_prompt_comparison_results,
    summarize_experiment,
    summarize_history,
)
from src.experiments import RESULT_FIELDS


def test_empty_history_summary_has_zero_values():
    summary = summarize_history([])

    assert summary["total_evaluations"] == 0
    assert summary["average_score"] == 0.0
    assert summary["decision_counts"] == {
        "PUBLISH": 0,
        "REVIEW": 0,
        "REJECT": 0,
    }


def test_history_summary_calculates_counts_averages_and_concerns():
    records = [
        {
            "final_decision": "PUBLISH",
            "overall_score": 90,
            "total_latency_ms": 2,
            "main_concern": "No major concerns were detected.",
        },
        {
            "final_decision": "REJECT",
            "overall_score": 50,
            "total_latency_ms": 4,
            "main_concern": "Unsupported claim.",
        },
    ]

    summary = summarize_history(records)

    assert summary["average_score"] == 70
    assert summary["average_latency_ms"] == 3
    assert summary["decision_counts"]["REJECT"] == 1
    assert summary["common_concerns"] == [("Unsupported claim.", 1)]


def test_experiment_csv_is_loaded_with_restored_types(tmp_path):
    path = tmp_path / "results.csv"
    row = {field: "sample" for field in RESULT_FIELDS}
    row.update(
        {
            "correct": "True",
            "overall_score": "90",
            "relevance_score": "90",
            "source_support_score": "90",
            "completeness_score": "90",
            "clarity_score": "90",
            "uncertainty_score": "90",
            "latency_ms": "2",
        }
    )
    with path.open("w", newline="", encoding="utf-8") as results_file:
        writer = csv.DictWriter(results_file, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerow(row)

    loaded = load_experiment_results(path)

    assert loaded[0]["correct"] is True
    assert loaded[0]["overall_score"] == 90
    assert loaded[0]["latency_ms"] == 2


def test_experiment_summary_uses_standard_metrics():
    rows = [
        {
            "expected_decision": "REJECT",
            "actual_decision": "REJECT",
            "category": "unsupported",
            "correct": True,
            "latency_ms": 1,
        }
    ]

    summary = summarize_experiment(rows)

    assert summary["decision_accuracy_pct"] == 100.0
    assert summary["false_publish_rate_pct"] == 0.0
    assert summary["unsupported_detection_rate_pct"] == 100.0


def test_prompt_comparison_csv_restores_optional_booleans(tmp_path):
    path = tmp_path / "prompt_results.csv"
    path.write_text(
        "model_matches_expected,agrees_with_deterministic,"
        "transformer_latency_ms\nTrue,,12\n",
        encoding="utf-8",
    )

    rows = load_prompt_comparison_results(path)

    assert rows[0]["model_matches_expected"] is True
    assert rows[0]["agrees_with_deterministic"] is None
    assert rows[0]["transformer_latency_ms"] == 12
