"""Run repeatable offline experiments on labelled AnswerTrust examples."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path
from statistics import mean

from src.config import EXPERIMENT_RESULTS_PATH
from src.evaluator import evaluate_answer
from src.example_data import load_examples, validate_examples
from src.models import Decision, EvaluationInput


RESULT_FIELDS = [
    "id",
    "category",
    "expected_decision",
    "actual_decision",
    "correct",
    "overall_score",
    "relevance_score",
    "source_support_score",
    "completeness_score",
    "clarity_score",
    "uncertainty_score",
    "latency_ms",
    "reason",
]


def calculate_metrics(rows: Sequence[dict]) -> dict[str, float | int]:
    """Calculate aggregate safety, quality, and speed metrics."""
    total = len(rows)
    correct = sum(bool(row["correct"]) for row in rows)
    unsafe_rows = [
        row for row in rows if row["expected_decision"] == Decision.REJECT.value
    ]
    false_publishes = sum(
        row["actual_decision"] == Decision.PUBLISH.value
        for row in unsafe_rows
    )
    unsupported_rows = [
        row for row in rows if row["category"] == "unsupported"
    ]
    unsupported_rejections = sum(
        row["actual_decision"] == Decision.REJECT.value
        for row in unsupported_rows
    )
    reviews = sum(
        row["actual_decision"] == Decision.REVIEW.value for row in rows
    )

    return {
        "total_examples": total,
        "correct_decisions": correct,
        "decision_accuracy_pct": round(correct / total * 100, 2) if total else 0.0,
        "unsafe_examples": len(unsafe_rows),
        "false_publishes": false_publishes,
        "false_publish_rate_pct": (
            round(false_publishes / len(unsafe_rows) * 100, 2)
            if unsafe_rows
            else 0.0
        ),
        "unsupported_examples": len(unsupported_rows),
        "unsupported_rejections": unsupported_rejections,
        "unsupported_detection_rate_pct": (
            round(unsupported_rejections / len(unsupported_rows) * 100, 2)
            if unsupported_rows
            else 0.0
        ),
        "review_rate_pct": round(reviews / total * 100, 2) if total else 0.0,
        "average_latency_ms": (
            round(mean(float(row["latency_ms"]) for row in rows), 2)
            if rows
            else 0.0
        ),
    }


def write_results(rows: Sequence[dict], output_path: Path) -> None:
    """Write per-example experiment results to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run_experiment(
    examples: list[dict] | None = None,
    output_path: Path = EXPERIMENT_RESULTS_PATH,
) -> tuple[list[dict], dict[str, float | int]]:
    """Evaluate labelled examples, save rows, and return rows and metrics."""
    experiment_examples = load_examples() if examples is None else examples
    validation_errors = validate_examples(experiment_examples)
    if validation_errors:
        raise ValueError("Invalid evaluation examples: " + " ".join(validation_errors))

    rows: list[dict] = []
    for example in experiment_examples:
        evaluation_input = EvaluationInput(
            question=example["question"],
            reference=example["reference"],
            answer=example["answer"],
        )
        result = evaluate_answer(evaluation_input)
        scores = {
            dimension.name: dimension.score
            for dimension in result.dimension_scores
        }
        actual_decision = result.final_decision.value

        rows.append(
            {
                "id": example["id"],
                "category": example["category"],
                "expected_decision": example["expected_decision"],
                "actual_decision": actual_decision,
                "correct": actual_decision == example["expected_decision"],
                "overall_score": result.overall_score,
                "relevance_score": scores["Relevance"],
                "source_support_score": scores["Source support"],
                "completeness_score": scores["Completeness"],
                "clarity_score": scores["Clarity"],
                "uncertainty_score": scores["Uncertainty handling"],
                "latency_ms": result.total_latency_ms,
                "reason": example["reason"],
            }
        )

    metrics = calculate_metrics(rows)
    write_results(rows, output_path)
    return rows, metrics


def main() -> None:
    """Run the configured experiment and print its measured summary."""
    rows, metrics = run_experiment()
    disagreements = [row for row in rows if not row["correct"]]

    print(f"Examples: {metrics['total_examples']}")
    print(f"Decision accuracy: {metrics['decision_accuracy_pct']}%")
    print(f"False-publish rate: {metrics['false_publish_rate_pct']}%")
    print(
        "Unsupported detection rate: "
        f"{metrics['unsupported_detection_rate_pct']}%"
    )
    print(f"Review rate: {metrics['review_rate_pct']}%")
    print(f"Average latency: {metrics['average_latency_ms']} ms")
    print(f"Disagreements: {len(disagreements)}")
    print(f"Results: {EXPERIMENT_RESULTS_PATH}")


if __name__ == "__main__":
    main()
