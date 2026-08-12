"""SQLite persistence for AnswerTrust evaluation history."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.models import (
    Decision,
    EvaluationInput,
    EvaluationResult,
    FailureType,
    RunState,
)


CREATE_EVALUATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS evaluations (
    evaluation_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    question TEXT NOT NULL,
    reference TEXT NOT NULL,
    answer TEXT NOT NULL,
    overall_score INTEGER NOT NULL,
    final_decision TEXT NOT NULL,
    dimension_scores TEXT NOT NULL,
    main_concern TEXT NOT NULL,
    explanation TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    deterministic_latency_ms INTEGER NOT NULL,
    transformer_latency_ms INTEGER NOT NULL,
    total_latency_ms INTEGER NOT NULL,
    prompt_version TEXT NOT NULL,
    model_status TEXT NOT NULL
)
"""

CREATE_EVALUATION_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS evaluation_runs (
    run_id TEXT PRIMARY KEY,
    evaluation_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    state TEXT NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    failure_type TEXT,
    failure_message TEXT,
    question TEXT NOT NULL,
    reference TEXT NOT NULL,
    answer TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id)
)
"""


def _connect(database_path: Path) -> sqlite3.Connection:
    """Open a database connection whose rows behave like mappings."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path) -> None:
    """Create the database folder and evaluations table when needed."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(database_path) as connection:
        connection.execute(CREATE_EVALUATIONS_TABLE)
        connection.execute(CREATE_EVALUATION_RUNS_TABLE)
        run_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(evaluation_runs)"
            ).fetchall()
        }
        if "failure_type" not in run_columns:
            connection.execute(
                "ALTER TABLE evaluation_runs ADD COLUMN failure_type TEXT"
            )
        if "failure_message" not in run_columns:
            connection.execute(
                "ALTER TABLE evaluation_runs ADD COLUMN failure_message TEXT"
            )
        if "attempt_count" not in run_columns:
            connection.execute(
                "ALTER TABLE evaluation_runs "
                "ADD COLUMN attempt_count INTEGER NOT NULL DEFAULT 0"
            )


def save_evaluation(
    evaluation_input: EvaluationInput,
    result: EvaluationResult,
    database_path: Path,
) -> None:
    """Save one input and result as an evaluation-history record."""
    initialize_database(database_path)
    serialized_scores = json.dumps(
        [asdict(score) for score in result.dimension_scores]
    )

    with _connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO evaluations (
                evaluation_id,
                timestamp,
                question,
                reference,
                answer,
                overall_score,
                final_decision,
                dimension_scores,
                main_concern,
                explanation,
                recommended_action,
                deterministic_latency_ms,
                transformer_latency_ms,
                total_latency_ms,
                prompt_version,
                model_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.evaluation_id,
                result.timestamp.isoformat(),
                evaluation_input.question,
                evaluation_input.reference,
                evaluation_input.answer,
                result.overall_score,
                result.final_decision.value,
                serialized_scores,
                result.main_concern,
                result.explanation,
                result.recommended_action,
                result.deterministic_latency_ms,
                result.transformer_latency_ms,
                result.total_latency_ms,
                result.prompt_version,
                result.model_status,
            ),
        )


def get_evaluations(
    database_path: Path,
    decision: Decision | None = None,
) -> list[dict]:
    """Return saved evaluations newest-first, optionally by decision."""
    initialize_database(database_path)
    query = "SELECT * FROM evaluations"
    parameters: tuple[str, ...] = ()

    if decision is not None:
        query += " WHERE final_decision = ?"
        parameters = (decision.value,)

    query += " ORDER BY timestamp DESC"

    with _connect(database_path) as connection:
        rows = connection.execute(query, parameters).fetchall()

    evaluations: list[dict] = []
    for row in rows:
        evaluation = dict(row)
        evaluation["dimension_scores"] = json.loads(
            evaluation["dimension_scores"]
        )
        evaluations.append(evaluation)

    return evaluations


def create_evaluation_run(
    evaluation_input: EvaluationInput,
    database_path: Path,
) -> str:
    """Persist a newly received evaluation run and return its identifier."""
    initialize_database(database_path)
    run_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    with _connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO evaluation_runs (
                run_id,
                evaluation_id,
                created_at,
                updated_at,
                state,
                question,
                reference,
                answer,
                prompt_version
            ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                timestamp,
                timestamp,
                RunState.RECEIVED.value,
                evaluation_input.question,
                evaluation_input.reference,
                evaluation_input.answer,
                evaluation_input.prompt_version,
            ),
        )

    return run_id


def update_evaluation_run_state(
    run_id: str,
    state: RunState,
    database_path: Path,
    evaluation_id: str | None = None,
    failure_type: FailureType | None = None,
    failure_message: str | None = None,
    attempt_count: int | None = None,
) -> None:
    """Persist a run's current state and optional completed evaluation ID."""
    initialize_database(database_path)
    timestamp = datetime.now(timezone.utc).isoformat()

    with _connect(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE evaluation_runs
            SET state = ?,
                updated_at = ?,
                evaluation_id = COALESCE(?, evaluation_id),
                failure_type = COALESCE(?, failure_type),
                failure_message = COALESCE(?, failure_message),
                attempt_count = COALESCE(?, attempt_count)
            WHERE run_id = ?
            """,
            (
                state.value,
                timestamp,
                evaluation_id,
                failure_type.value if failure_type else None,
                failure_message,
                attempt_count,
                run_id,
            ),
        )
        if cursor.rowcount == 0:
            raise KeyError(f"Unknown evaluation run: {run_id}")


def get_evaluation_run(
    run_id: str,
    database_path: Path,
) -> dict | None:
    """Return one persisted evaluation run, or None when it does not exist."""
    initialize_database(database_path)
    with _connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM evaluation_runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def get_evaluation_runs(
    database_path: Path,
    state: RunState | None = None,
) -> list[dict]:
    """Return persisted runs newest-first, optionally filtered by state."""
    initialize_database(database_path)
    query = "SELECT * FROM evaluation_runs"
    parameters: tuple[str, ...] = ()
    if state is not None:
        query += " WHERE state = ?"
        parameters = (state.value,)
    query += " ORDER BY created_at DESC"

    with _connect(database_path) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [dict(row) for row in rows]
