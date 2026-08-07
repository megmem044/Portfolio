"""Load and validate AnswerTrust's labelled evaluation examples."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.config import EVALUATION_EXAMPLES_PATH
from src.models import Decision


REQUIRED_FIELDS = {
    "id",
    "category",
    "question",
    "reference",
    "answer",
    "expected_decision",
    "reason",
}
REQUIRED_CATEGORIES = {
    "supported",
    "partially_supported",
    "unsupported",
    "irrelevant",
    "insufficient_reference",
}
MINIMUM_EXAMPLES_PER_CATEGORY = 6


def load_examples(
    path: Path = EVALUATION_EXAMPLES_PATH,
) -> list[dict]:
    """Read labelled examples from a UTF-8 JSON file."""
    with path.open(encoding="utf-8") as examples_file:
        examples = json.load(examples_file)

    if not isinstance(examples, list):
        raise ValueError("The evaluation example file must contain a JSON list.")
    return examples


def validate_examples(examples: object) -> list[str]:
    """Return all schema and balance problems found in example data."""
    if not isinstance(examples, list):
        return ["Evaluation examples must be provided as a list."]

    errors: list[str] = []
    identifiers: list[str] = []
    category_counts: Counter[str] = Counter()
    valid_decisions = {decision.value for decision in Decision}

    for index, example in enumerate(examples, start=1):
        location = f"Example {index}"
        if not isinstance(example, dict):
            errors.append(f"{location} must be a JSON object.")
            continue

        missing_fields = REQUIRED_FIELDS - set(example)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            errors.append(f"{location} is missing fields: {missing}.")
            continue

        for field in REQUIRED_FIELDS:
            value = example[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{location} has an empty or invalid {field}.")

        identifier = example["id"]
        if isinstance(identifier, str):
            identifiers.append(identifier)

        category = example["category"]
        if category not in REQUIRED_CATEGORIES:
            errors.append(f"{location} has an invalid category: {category}.")
        else:
            category_counts[category] += 1

        decision = example["expected_decision"]
        if decision not in valid_decisions:
            errors.append(
                f"{location} has an invalid expected decision: {decision}."
            )

    duplicate_ids = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    if duplicate_ids:
        errors.append(f"Duplicate example IDs: {', '.join(duplicate_ids)}.")

    for category in sorted(REQUIRED_CATEGORIES):
        count = category_counts[category]
        if count < MINIMUM_EXAMPLES_PER_CATEGORY:
            errors.append(
                f"Category {category} requires at least "
                f"{MINIMUM_EXAMPLES_PER_CATEGORY} examples; found {count}."
            )

    return errors
