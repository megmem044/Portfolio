"""Create blind review sheets and measure independent label agreement."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from src.config import RESULTS_DIR
from src.example_data import load_examples
from src.models import ClaimLabel

REVIEW_FIELDS = [
    "id", "category", "difficulty_category", "source_title", "source_locator",
    "excerpt_section", "question", "paper_text", "answer",
    "independent_label", "reviewer_confidence", "reviewer_notes",
]
VALID_LABELS = {label.value for label in ClaimLabel}
DEFAULT_SHEET = RESULTS_DIR / "independent_review.csv"
DEFAULT_REPORT = RESULTS_DIR / "reviewer_agreement.json"


def export_review_sheet(path: Path = DEFAULT_SHEET, sample_size: int = 30, seed: int = 42) -> list[dict]:
    """Export a repeatable sample without project or system labels."""
    examples = [item for item in load_examples() if item["source_type"] == "REAL_EXCERPT"]
    if not 1 <= sample_size <= len(examples):
        raise ValueError(f"Sample size must be between 1 and {len(examples)}.")
    selected = random.Random(seed).sample(examples, sample_size)
    rows = [
        {
            **{field: item.get(field, "") for field in REVIEW_FIELDS},
            "independent_label": "",
            "reviewer_confidence": "",
            "reviewer_notes": "",
        }
        for item in sorted(selected, key=lambda item: item["id"])
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _wilson_interval(matches: int, total: int) -> tuple[float, float]:
    """Return a 95% Wilson confidence interval for observed agreement."""
    if total == 0:
        return 0.0, 0.0
    z = 1.96
    proportion = matches / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    spread = z * math.sqrt((proportion * (1 - proportion) + z * z / (4 * total)) / total) / denominator
    return round(100 * max(0, center - spread), 2), round(100 * min(1, center + spread), 2)


def _cohens_kappa(project_labels: list[str], independent_labels: list[str]) -> float:
    total = len(project_labels)
    observed = sum(left == right for left, right in zip(project_labels, independent_labels)) / total
    project_counts, independent_counts = Counter(project_labels), Counter(independent_labels)
    expected = sum(project_counts[label] * independent_counts[label] for label in VALID_LABELS) / (total * total)
    return round((observed - expected) / (1 - expected), 4) if expected < 1 else 1.0


def calculate_agreement(review_rows: list[dict], examples: list[dict] | None = None) -> dict:
    """Validate completed labels and compare them with project-authored labels."""
    examples_by_id = {item["id"]: item for item in (examples or load_examples())}
    errors, seen, compared = [], set(), []
    for row_number, row in enumerate(review_rows, 2):
        example_id = row.get("id", "").strip()
        label = row.get("independent_label", "").strip().upper()
        if example_id in seen:
            errors.append(f"Row {row_number}: duplicate id {example_id}.")
        elif example_id not in examples_by_id:
            errors.append(f"Row {row_number}: unknown id {example_id}.")
        if label not in VALID_LABELS:
            errors.append(f"Row {row_number}: invalid or missing independent_label.")
        confidence_text = row.get("reviewer_confidence", "").strip()
        try:
            confidence = float(confidence_text)
            if not 0 <= confidence <= 1:
                raise ValueError
        except ValueError:
            errors.append(f"Row {row_number}: reviewer_confidence must be between 0 and 1.")
            confidence = 0.0
        seen.add(example_id)
        if example_id in examples_by_id and label in VALID_LABELS:
            item = examples_by_id[example_id]
            compared.append((item, label, confidence))
    if errors:
        raise ValueError(" ".join(errors))
    if not compared:
        raise ValueError("The review sheet contains no completed examples.")

    project_labels = [item["reviewer_label"] for item, _, _ in compared]
    independent_labels = [label for _, label, _ in compared]
    matches = sum(left == right for left, right in zip(project_labels, independent_labels))
    by_category: dict[str, list[bool]] = defaultdict(list)
    disagreements = []
    for (item, label, confidence), project_label in zip(compared, project_labels):
        agreed = label == project_label
        by_category[item["category"]].append(agreed)
        if not agreed:
            disagreements.append({"id": item["id"], "category": item["category"], "project_label": project_label, "independent_label": label, "reviewer_confidence": confidence})
    low, high = _wilson_interval(matches, len(compared))
    return {
        "reviewed_examples": len(compared),
        "agreement_pct": round(100 * matches / len(compared), 2),
        "agreement_95_ci_pct": [low, high],
        "cohens_kappa": _cohens_kappa(project_labels, independent_labels),
        "category_agreement": {
            category: {"reviewed": len(values), "agreement_pct": round(100 * sum(values) / len(values), 2)}
            for category, values in sorted(by_category.items())
        },
        "disagreements": disagreements,
    }


def load_and_report(sheet_path: Path, report_path: Path = DEFAULT_REPORT) -> dict:
    with sheet_path.open(newline="", encoding="utf-8-sig") as handle:
        report = calculate_agreement(list(csv.DictReader(handle)))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent benchmark review tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    export_parser = subparsers.add_parser("export", help="Create a blind CSV review sheet")
    export_parser.add_argument("--sample-size", type=int, default=30)
    export_parser.add_argument("--seed", type=int, default=42)
    export_parser.add_argument("--output", type=Path, default=DEFAULT_SHEET)
    report_parser = subparsers.add_parser("report", help="Validate a completed sheet and calculate agreement")
    report_parser.add_argument("sheet", type=Path)
    report_parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    if arguments.command == "export":
        rows = export_review_sheet(arguments.output, arguments.sample_size, arguments.seed)
        print(f"Exported {len(rows)} blind review cases to {arguments.output}")
    else:
        report = load_and_report(arguments.sheet, arguments.output)
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
