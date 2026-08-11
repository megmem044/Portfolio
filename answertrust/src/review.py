"""Human decisions for evaluation runs awaiting review."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from src import database
from src.models import RunState


class ReviewDecision(str, Enum):
    """Decisions a human reviewer can make."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"


def resolve_human_review(
    run_id: str,
    decision: ReviewDecision,
    database_path: Path,
) -> dict:
    """Resolve a HUMAN_REVIEW run and return its updated record."""
    run = database.get_evaluation_run(run_id, database_path)
    if run is None:
        raise KeyError(f"Unknown evaluation run: {run_id}")

    if run["state"] != RunState.HUMAN_REVIEW.value:
        raise ValueError(
            "Only evaluation runs in HUMAN_REVIEW can be resolved."
        )

    final_state = {
        ReviewDecision.APPROVE: RunState.APPROVED,
        ReviewDecision.REJECT: RunState.REJECTED,
    }[decision]
    database.update_evaluation_run_state(
        run_id,
        final_state,
        database_path,
    )

    updated_run = database.get_evaluation_run(run_id, database_path)
    if updated_run is None:
        raise RuntimeError("The resolved evaluation run could not be loaded.")
    return updated_run
