"""Import data from the original SQLite prototype into SQLAlchemy tables."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from src.db import session_scope
from src.evaluation_repository import EvaluationRepository
from src.models import (
    ClaimLabel,
    ClaimResult,
    Decision,
    DimensionScore,
    EvaluationInput,
    EvaluationResult,
    Evidence,
)


def migrate_legacy_sqlite(
    source_path: Path, factory: sessionmaker[Session]
) -> dict[str, int]:
    """Copy legacy evaluations and completed reviews without duplicating rows."""
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    migrated = skipped = reviews = 0
    try:
        evaluation_rows = source.execute("SELECT * FROM evaluations").fetchall()
        review_rows = {
            row["evaluation_id"]: row
            for row in source.execute(
                "SELECT evaluation_id, reviewer_decision, reviewer_notes "
                "FROM evaluation_runs WHERE evaluation_id IS NOT NULL "
                "AND reviewer_decision IS NOT NULL"
            ).fetchall()
        }
        with session_scope(factory) as session:
            repository = EvaluationRepository(session)
            for row in evaluation_rows:
                if repository.get(row["evaluation_id"]) is not None:
                    skipped += 1
                    continue
                item = EvaluationInput(row["question"], row["paper_text"], row["answer"])
                result = _legacy_result(row)
                repository.save_queued(result.evaluation_id, item)
                repository.save_result(result)
                migrated += 1
                review = review_rows.get(result.evaluation_id)
                if review is not None and result.final_decision == Decision.REVIEW:
                    repository.save_review(
                        result.evaluation_id,
                        review["reviewer_decision"],
                        review["reviewer_notes"] or "Imported legacy review.",
                    )
                    reviews += 1
    finally:
        source.close()
    return {"migrated": migrated, "skipped": skipped, "reviews": reviews}


def _legacy_result(row: sqlite3.Row) -> EvaluationResult:
    claim_data = json.loads(row["claim_results"])
    dimension_data = json.loads(row["dimension_scores"])
    claims = [
        ClaimResult(
            claim=item["claim"],
            label=ClaimLabel(item["label"]),
            evidence=[Evidence(**evidence) for evidence in item["evidence"]],
            explanation=item["explanation"],
            failure_types=item.get("failure_types", []),
            nli_label=item.get("nli_label"),
            nli_confidence=item.get("nli_confidence"),
        )
        for item in claim_data
    ]
    return EvaluationResult(
        evaluation_id=row["evaluation_id"],
        timestamp=datetime.fromisoformat(row["timestamp"]),
        overall_score=row["overall_score"],
        final_decision=Decision(row["final_decision"]),
        claim_results=claims,
        dimension_scores=[DimensionScore(**item) for item in dimension_data],
        main_concern=row["main_concern"],
        explanation=row["explanation"],
        recommended_action=row["recommended_action"],
        total_latency_ms=row["total_latency_ms"],
        deterministic_latency_ms=row["total_latency_ms"],
    )
