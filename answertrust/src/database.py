"""SQLite persistence for evaluations, claims, runs, and reviewer decisions."""

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.models import Decision, EvaluationInput, EvaluationResult, FailureType, RunState


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(path: Path) -> None:
    with _connect(path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS evaluations (
          evaluation_id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, question TEXT NOT NULL,
          paper_text TEXT NOT NULL, answer TEXT NOT NULL, overall_score INTEGER NOT NULL,
          final_decision TEXT NOT NULL, dimension_scores TEXT NOT NULL, claim_results TEXT NOT NULL,
          main_concern TEXT NOT NULL, explanation TEXT NOT NULL, recommended_action TEXT NOT NULL,
          total_latency_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS evaluation_runs (
          run_id TEXT PRIMARY KEY, evaluation_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          state TEXT NOT NULL, attempt_count INTEGER NOT NULL DEFAULT 0, failure_type TEXT,
          failure_message TEXT, question TEXT NOT NULL, paper_text TEXT NOT NULL, answer TEXT NOT NULL,
          system_decision TEXT, reviewer_decision TEXT, reviewer_notes TEXT, reviewed_at TEXT);
        """)


def create_evaluation_run(item: EvaluationInput, path: Path) -> str:
    initialize_database(path); run_id = str(uuid4()); now = datetime.now(timezone.utc).isoformat()
    with _connect(path) as db:
        db.execute("INSERT INTO evaluation_runs (run_id,created_at,updated_at,state,question,paper_text,answer) VALUES (?,?,?,?,?,?,?)", (run_id,now,now,RunState.RECEIVED.value,item.question,item.paper_text,item.answer))
    return run_id


def update_evaluation_run_state(run_id: str, state: RunState, path: Path, evaluation_id: str|None=None, failure_type: FailureType|None=None, failure_message: str|None=None, attempt_count: int|None=None, system_decision: Decision|None=None) -> None:
    with _connect(path) as db:
        cursor=db.execute("UPDATE evaluation_runs SET state=?,updated_at=?,evaluation_id=COALESCE(?,evaluation_id),failure_type=?,failure_message=?,attempt_count=COALESCE(?,attempt_count),system_decision=COALESCE(?,system_decision) WHERE run_id=?", (state.value,datetime.now(timezone.utc).isoformat(),evaluation_id,failure_type.value if failure_type else None,failure_message,attempt_count,system_decision.value if system_decision else None,run_id))
        if not cursor.rowcount: raise KeyError(f"Unknown evaluation run: {run_id}")


def save_evaluation(item: EvaluationInput, result: EvaluationResult, path: Path) -> None:
    with _connect(path) as db:
        db.execute("INSERT INTO evaluations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (result.evaluation_id,result.timestamp.isoformat(),item.question,item.paper_text,item.answer,result.overall_score,result.final_decision.value,json.dumps([asdict(x) for x in result.dimension_scores]),json.dumps([asdict(x) for x in result.claim_results],default=lambda x:x.value),result.main_concern,result.explanation,result.recommended_action,result.total_latency_ms))


def get_evaluations(path: Path, decision: Decision|None=None) -> list[dict]:
    initialize_database(path); query="SELECT * FROM evaluations"; params=()
    if decision: query += " WHERE final_decision=?"; params=(decision.value,)
    with _connect(path) as db: rows=db.execute(query+" ORDER BY timestamp DESC",params).fetchall()
    result=[]
    for row in rows:
        item=dict(row); item["dimension_scores"]=json.loads(item["dimension_scores"]); item["claim_results"]=json.loads(item["claim_results"]); result.append(item)
    return result


def get_evaluation_run(run_id: str, path: Path) -> dict|None:
    initialize_database(path)
    with _connect(path) as db: row=db.execute("SELECT * FROM evaluation_runs WHERE run_id=?",(run_id,)).fetchone()
    return dict(row) if row else None


def get_evaluation_runs(path: Path, state: RunState|None=None) -> list[dict]:
    initialize_database(path); query="SELECT * FROM evaluation_runs"; params=()
    if state: query += " WHERE state=?"; params=(state.value,)
    with _connect(path) as db: return [dict(row) for row in db.execute(query+" ORDER BY created_at DESC",params).fetchall()]


def save_review(run_id: str, reviewer_decision: str, notes: str, path: Path) -> None:
    state=RunState.APPROVED if reviewer_decision=="APPROVE" else RunState.REJECTED
    with _connect(path) as db:
        cursor=db.execute("UPDATE evaluation_runs SET state=?,updated_at=?,reviewer_decision=?,reviewer_notes=?,reviewed_at=? WHERE run_id=? AND state=?",(state.value,datetime.now(timezone.utc).isoformat(),reviewer_decision,notes.strip(),datetime.now(timezone.utc).isoformat(),run_id,RunState.HUMAN_REVIEW.value))
        if not cursor.rowcount: raise ValueError("Only runs awaiting human review can be resolved.")
