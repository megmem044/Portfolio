"""SQLite persistence for AnswerTrust evaluation history."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from src.models import Decision, EvaluationInput, EvaluationResult


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
