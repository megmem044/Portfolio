"""Human review decisions with an audit trail."""
from enum import Enum
from pathlib import Path
from src import database

class ReviewDecision(str,Enum):
    APPROVE="APPROVE"
    REJECT="REJECT"

def resolve_human_review(run_id: str, decision: ReviewDecision, database_path: Path, notes: str="") -> dict:
    database.save_review(run_id,decision.value,notes,database_path)
    result=database.get_evaluation_run(run_id,database_path)
    if result is None: raise KeyError(run_id)
    return result
