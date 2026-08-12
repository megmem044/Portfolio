"""Tests for local SQLite evaluation history."""

import sqlite3
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from src.database import (
    create_evaluation_run,
    get_evaluation_run,
    get_evaluation_runs,
    get_evaluations,
    initialize_database,
    save_evaluation,
    update_evaluation_run_state,
)
from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput, FailureType, RunState


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


def test_create_evaluation_run_starts_in_received_state(tmp_path):
    database_path = tmp_path / "answertrust.db"
    evaluation_input = supported_input()

    run_id = create_evaluation_run(evaluation_input, database_path)
    run = get_evaluation_run(run_id, database_path)

    assert run is not None
    assert run["run_id"] == run_id
    assert run["state"] == RunState.RECEIVED.value
    assert run["evaluation_id"] is None
    assert run["question"] == evaluation_input.question
    assert run["reference"] == evaluation_input.reference
    assert run["answer"] == evaluation_input.answer


def test_update_evaluation_run_state_and_evaluation_id(tmp_path):
    database_path = tmp_path / "answertrust.db"
    evaluation_input = supported_input()
    result = evaluate_answer(evaluation_input)
    save_evaluation(evaluation_input, result, database_path)
    run_id = create_evaluation_run(evaluation_input, database_path)

    update_evaluation_run_state(
        run_id,
        RunState.APPROVED,
        database_path,
        evaluation_id=result.evaluation_id,
    )
    run = get_evaluation_run(run_id, database_path)

    assert run is not None
    assert run["state"] == RunState.APPROVED.value
    assert run["evaluation_id"] == result.evaluation_id


def test_get_evaluation_runs_can_filter_by_state(tmp_path):
    database_path = tmp_path / "answertrust.db"
    first_run_id = create_evaluation_run(supported_input(), database_path)
    second_run_id = create_evaluation_run(supported_input("Lyon"), database_path)
    update_evaluation_run_state(
        second_run_id,
        RunState.REJECTED,
        database_path,
    )

    received_runs = get_evaluation_runs(database_path, RunState.RECEIVED)
    rejected_runs = get_evaluation_runs(database_path, RunState.REJECTED)

    assert [run["run_id"] for run in received_runs] == [first_run_id]
    assert [run["run_id"] for run in rejected_runs] == [second_run_id]


def test_updating_unknown_evaluation_run_raises_key_error(tmp_path):
    database_path = tmp_path / "answertrust.db"

    with pytest.raises(KeyError, match="Unknown evaluation run"):
        update_evaluation_run_state(
            "missing-run",
            RunState.FAILED,
            database_path,
        )


def test_update_evaluation_run_saves_failure_details(tmp_path):
    database_path = tmp_path / "answertrust.db"
    run_id = create_evaluation_run(supported_input(), database_path)

    update_evaluation_run_state(
        run_id,
        RunState.FAILED,
        database_path,
        failure_type=FailureType.MODEL_TIMEOUT,
        failure_message="The model exceeded its deadline.",
    )
    run = get_evaluation_run(run_id, database_path)

    assert run is not None
    assert run["failure_type"] == FailureType.MODEL_TIMEOUT.value
    assert run["failure_message"] == "The model exceeded its deadline."


def test_initialize_database_adds_failure_columns_to_existing_runs(tmp_path):
    database_path = tmp_path / "answertrust.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE evaluation_runs (
                run_id TEXT PRIMARY KEY,
                evaluation_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                state TEXT NOT NULL,
                question TEXT NOT NULL,
                reference TEXT NOT NULL,
                answer TEXT NOT NULL,
                prompt_version TEXT NOT NULL
            )
            """
        )

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(evaluation_runs)"
            ).fetchall()
        }
    assert "failure_type" in columns
    assert "failure_message" in columns
