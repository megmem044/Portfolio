"""Tests for local SQLite evaluation history."""

import sqlite3
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from src.database import (
    get_evaluations,
    initialize_database,
    save_evaluation,
)
from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput


def supported_input(answer: str = "Paris") -> EvaluationInput:
    return EvaluationInput(
        question="What is the capital of France?",
        reference="Paris",
        answer=answer,
    )


def test_initialize_database_creates_table(tmp_path):
    database_path = tmp_path / "history" / "answertrust.db"

    initialize_database(database_path)

    assert database_path.exists()
    with sqlite3.connect(database_path) as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name = 'evaluations'"
        ).fetchone()
    assert table == ("evaluations",)


def test_empty_database_returns_empty_history(tmp_path):
    database_path = tmp_path / "answertrust.db"

    assert get_evaluations(database_path) == []


def test_save_and_read_evaluation(tmp_path):
    database_path = tmp_path / "answertrust.db"
    evaluation_input = supported_input()
    result = evaluate_answer(evaluation_input)

    save_evaluation(evaluation_input, result, database_path)
    records = get_evaluations(database_path)

    assert len(records) == 1
    assert records[0]["evaluation_id"] == result.evaluation_id
    assert records[0]["question"] == evaluation_input.question
    assert records[0]["final_decision"] == Decision.PUBLISH.value
    assert len(records[0]["dimension_scores"]) == 5


def test_history_is_returned_newest_first(tmp_path):
    database_path = tmp_path / "answertrust.db"
    evaluation_input = supported_input()
    first = replace(
        evaluate_answer(evaluation_input),
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    second = replace(
        evaluate_answer(evaluation_input),
        timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    save_evaluation(evaluation_input, first, database_path)
    save_evaluation(evaluation_input, second, database_path)

    records = get_evaluations(database_path)
    assert [record["evaluation_id"] for record in records] == [
        second.evaluation_id,
        first.evaluation_id,
    ]


def test_history_can_be_filtered_by_decision(tmp_path):
    database_path = tmp_path / "answertrust.db"
    publish_input = supported_input()
    reject_input = EvaluationInput(
        question="What is the capital of France?",
        reference="Paris",
        answer="Whales live in the ocean.",
    )

    save_evaluation(
        publish_input,
        evaluate_answer(publish_input),
        database_path,
    )
    save_evaluation(
        reject_input,
        evaluate_answer(reject_input),
        database_path,
    )

    records = get_evaluations(database_path, Decision.REJECT)
    assert len(records) == 1
    assert records[0]["final_decision"] == Decision.REJECT.value


def test_duplicate_evaluation_id_is_rejected(tmp_path):
    database_path = tmp_path / "answertrust.db"
    evaluation_input = supported_input()
    result = evaluate_answer(evaluation_input)
    save_evaluation(evaluation_input, result, database_path)

    with pytest.raises(sqlite3.IntegrityError):
        save_evaluation(evaluation_input, result, database_path)
