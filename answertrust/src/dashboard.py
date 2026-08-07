"""Data preparation helpers for the AnswerTrust quality dashboard."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from statistics import mean

from src.experiments import calculate_metrics
from src.models import Decision


INTEGER_RESULT_FIELDS = {
    "overall_score",
    "relevance_score",
    "source_support_score",
    "completeness_score",
    "clarity_score",
    "uncertainty_score",
    "latency_ms",
}


def summarize_history(records: list[dict]) -> dict:
    """Return decision, score, speed, and concern summaries."""
    decision_counts = {decision.value: 0 for decision in Decision}
    for record in records:
        decision_counts[record["final_decision"]] += 1

    meaningful_concerns = [
        record["main_concern"]
        for record in records
        if record["main_concern"] != "No major concerns were detected."
    ]

    return {
        "total_evaluations": len(records),
        "average_score": (
            round(mean(record["overall_score"] for record in records), 2)
            if records
            else 0.0
        ),
        "average_latency_ms": (
            round(mean(record["total_latency_ms"] for record in records), 2)
            if records
            else 0.0
        ),
        "decision_counts": decision_counts,
        "common_concerns": Counter(meaningful_concerns).most_common(5),
    }


def load_experiment_results(path: Path) -> list[dict]:
    """Load experiment CSV rows with numeric and Boolean values restored."""
    with path.open(newline="", encoding="utf-8") as results_file:
        rows = list(csv.DictReader(results_file))

    for row in rows:
        row["correct"] = row["correct"].lower() == "true"
        for field in INTEGER_RESULT_FIELDS:
            row[field] = int(row[field])
    return rows


def summarize_experiment(rows: list[dict]) -> dict[str, float | int]:
    """Return the standard experiment metrics for dashboard display."""
    return calculate_metrics(rows)


def load_prompt_comparison_results(path: Path) -> list[dict]:
    """Load prompt-comparison CSV rows with typed status metrics."""
    with path.open(newline="", encoding="utf-8") as results_file:
        rows = list(csv.DictReader(results_file))

    for row in rows:
        for field in ("model_matches_expected", "agrees_with_deterministic"):
            value = row[field].strip().lower()
            row[field] = None if not value else value == "true"
        row["transformer_latency_ms"] = int(row["transformer_latency_ms"])
    return rows
