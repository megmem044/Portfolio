"""Read persistent operational trends from the application database."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db_models import BenchmarkRunRecord, EvaluationRecord, ReviewRecord, ReviewTaskRecord


class AnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def dashboard(self) -> dict:
        decision_rows = self.session.execute(
            select(EvaluationRecord.final_decision, func.count(EvaluationRecord.evaluation_id))
            .where(EvaluationRecord.final_decision.is_not(None))
            .group_by(EvaluationRecord.final_decision)
        ).all()
        review_rows = self.session.execute(
            select(ReviewRecord.reviewer_decision, func.count(ReviewRecord.evaluation_id))
            .group_by(ReviewRecord.reviewer_decision)
        ).all()
        benchmark_rows = self.session.scalars(
            select(BenchmarkRunRecord)
            .where(BenchmarkRunRecord.status == "COMPLETED")
            .order_by(BenchmarkRunRecord.started_at.desc())
            .limit(12)
        ).all()
        decisions = {name: count for name, count in decision_rows}
        reviews = {name: count for name, count in review_rows}
        return {
            "total_evaluations": sum(decisions.values()),
            "average_evaluation_latency_ms": round(self.session.scalar(select(func.avg(EvaluationRecord.total_latency_ms))) or 0, 2),
            "open_reviews": self.session.scalar(select(func.count(ReviewTaskRecord.task_id)).where(ReviewTaskRecord.status == "OPEN")) or 0,
            "resolved_reviews": sum(reviews.values()),
            "decision_counts": {"PUBLISH": decisions.get("PUBLISH", 0), "REVIEW": decisions.get("REVIEW", 0), "REJECT": decisions.get("REJECT", 0)},
            "review_counts": {"APPROVE": reviews.get("APPROVE", 0), "REJECT": reviews.get("REJECT", 0)},
            "benchmark_history": [
                {
                    "run_id": run.run_id,
                    "started_at": run.started_at,
                    "decision_accuracy_pct": (run.metrics or {}).get("decision_accuracy_pct", 0),
                    "false_publish_rate_pct": (run.metrics or {}).get("false_publish_rate_pct", 0),
                }
                for run in reversed(benchmark_rows)
            ],
        }
