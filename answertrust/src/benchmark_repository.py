"""Database operations for benchmark runs and example results."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db_models import BenchmarkResultRecord, BenchmarkRunRecord


class BenchmarkRepository:
    """Store and retrieve benchmark lifecycle information."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def start(self, benchmark_name: str) -> BenchmarkRunRecord:
        run = BenchmarkRunRecord(
            run_id=str(uuid4()), benchmark_name=benchmark_name, status="RUNNING"
        )
        self.session.add(run)
        self.session.flush()
        return run

    def add_result(
        self,
        run_id: str,
        example_id: str,
        expected_label: str,
        actual_label: str,
        details: dict | None = None,
    ) -> BenchmarkResultRecord:
        run = self.get(run_id)
        if run is None:
            raise KeyError(f"Unknown benchmark run: {run_id}")
        if run.status != "RUNNING":
            raise ValueError("Results can only be added to a running benchmark.")
        result = BenchmarkResultRecord(
            result_id=str(uuid4()),
            run_id=run_id,
            example_id=example_id,
            expected_label=expected_label,
            actual_label=actual_label,
            is_correct=expected_label == actual_label,
            details=details or {},
        )
        self.session.add(result)
        self.session.flush()
        return result

    def complete(self, run_id: str, metrics: dict) -> BenchmarkRunRecord:
        run = self._running(run_id)
        run.status = "COMPLETED"
        run.metrics = metrics
        run.completed_at = datetime.now(timezone.utc)
        self.session.flush()
        return run

    def fail(self, run_id: str, message: str) -> BenchmarkRunRecord:
        run = self._running(run_id)
        run.status = "FAILED"
        run.error_message = message
        run.completed_at = datetime.now(timezone.utc)
        self.session.flush()
        return run

    def get(self, run_id: str) -> BenchmarkRunRecord | None:
        return self.session.get(BenchmarkRunRecord, run_id)

    def list(self) -> list[BenchmarkRunRecord]:
        return list(
            self.session.scalars(
                select(BenchmarkRunRecord).order_by(BenchmarkRunRecord.started_at.desc())
            )
        )

    def results(self, run_id: str) -> list[BenchmarkResultRecord]:
        return list(
            self.session.scalars(
                select(BenchmarkResultRecord)
                .where(BenchmarkResultRecord.run_id == run_id)
                .order_by(BenchmarkResultRecord.example_id)
            )
        )

    def _running(self, run_id: str) -> BenchmarkRunRecord:
        run = self.get(run_id)
        if run is None:
            raise KeyError(f"Unknown benchmark run: {run_id}")
        if run.status != "RUNNING":
            raise ValueError("The benchmark run is no longer running.")
        return run
