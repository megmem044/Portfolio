"""Tests for the self-authored labelled evaluation dataset."""

import json

import pytest

from src.config import EVALUATION_EXAMPLES_PATH
from src.example_data import (
    REQUIRED_CATEGORIES,
    load_examples,
    validate_examples,
)


def test_project_example_file_is_valid_and_balanced():
    examples = load_examples()

    assert len(examples) >= 20
    assert validate_examples(examples) == []
    assert {example["category"] for example in examples} == REQUIRED_CATEGORIES


def test_load_examples_rejects_non_list_json(tmp_path):
    path = tmp_path / "examples.json"
    path.write_text(json.dumps({"id": "not-a-list"}), encoding="utf-8")

    with pytest.raises(ValueError, match="JSON list"):
        load_examples(path)


def test_validator_reports_duplicate_ids():
    examples = load_examples()
    examples[1]["id"] = examples[0]["id"]

    errors = validate_examples(examples)

    assert any("Duplicate example IDs" in error for error in errors)


def test_validator_reports_missing_fields():
    examples = load_examples()
    del examples[0]["question"]

    errors = validate_examples(examples)

    assert any("missing fields" in error for error in errors)


def test_validator_reports_invalid_category():
    examples = load_examples()
    examples[0]["category"] = "unknown"

    errors = validate_examples(examples)

    assert any("invalid category" in error for error in errors)


def test_validator_reports_invalid_decision():
    examples = load_examples()
    examples[0]["expected_decision"] = "MAYBE"

    errors = validate_examples(examples)

    assert any("invalid expected decision" in error for error in errors)


def test_configured_example_path_points_to_project_data():
    assert EVALUATION_EXAMPLES_PATH.name == "evaluation_examples.json"
    assert EVALUATION_EXAMPLES_PATH.parent.name == "data"
