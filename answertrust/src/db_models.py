"""SQLAlchemy database models for the new persistence layer."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


EVALUATION_STATES = (
    "QUEUED",
    "PROCESSING",
    "COMPLETED",
    "REVIEW_REQUIRED",
    "APPROVED",
    "REJECTED",
    "FAILED",
    "RETRYING",
)


class Base(DeclarativeBase):
    """Base class shared by all new database models."""


class UserRecord(Base):
    """A minimal account used for protected reviewer and administrator work."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('REVIEWER', 'ADMIN')", name="ck_users_role"),
    )

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class PaperRecord(Base):
    """A paper stored once and reused by evaluations."""

    __tablename__ = "papers"

    paper_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    paper_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class EvaluationRecord(Base):
    """One evaluation request, its state, and its final result."""

    __tablename__ = "evaluations_v2"
    __table_args__ = (
        CheckConstraint(
            f"state IN {EVALUATION_STATES}",
            name="ck_evaluations_v2_state",
        ),
        CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)",
            name="ck_evaluations_v2_score",
        ),
    )

    evaluation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    paper_id: Mapped[str] = mapped_column(
        ForeignKey("papers.paper_id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    state: Mapped[str] = mapped_column(
        String(24), default="QUEUED", nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[int | None] = mapped_column(Integer)
    final_decision: Mapped[str | None] = mapped_column(String(16))
    dimension_scores: Mapped[list | None] = mapped_column(JSON)
    main_concern: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    recommended_action: Mapped[str | None] = mapped_column(Text)
    total_latency_ms: Mapped[int | None] = mapped_column(Integer)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_message: Mapped[str | None] = mapped_column(Text)


class ReviewTaskRecord(Base):
    """A human-review task created for an uncertain evaluation."""

    __tablename__ = "review_tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('OPEN', 'RESOLVED')", name="ck_review_tasks_status"
        ),
    )

    task_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(
        ForeignKey("evaluations_v2.evaluation_id"),
        unique=True,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(16), default="OPEN", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReviewRecord(Base):
    """One human decision linked to a review task and evaluation."""

    __tablename__ = "review_decisions"
    __table_args__ = (
        CheckConstraint(
            "reviewer_decision IN ('APPROVE', 'REJECT')",
            name="ck_review_decisions_decision",
        ),
    )

    evaluation_id: Mapped[str] = mapped_column(
        ForeignKey("evaluations_v2.evaluation_id"), primary_key=True
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey("review_tasks.task_id"), unique=True, nullable=False
    )
    reviewer_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id"), index=True)
    reviewer_decision: Mapped[str] = mapped_column(String(16), nullable=False)
    reviewer_notes: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ClaimRecord(Base):
    """One independently reviewable claim from an evaluation."""

    __tablename__ = "claims"
    __table_args__ = (
        UniqueConstraint("evaluation_id", "position", name="uq_claims_evaluation_position"),
    )

    claim_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(
        ForeignKey("evaluations_v2.evaluation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(String(32), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    failure_types: Mapped[list] = mapped_column(JSON, nullable=False)


class EvidencePassageRecord(Base):
    """One paper passage used to judge a claim."""

    __tablename__ = "evidence_passages"
    __table_args__ = (
        UniqueConstraint("claim_id", "position", name="uq_evidence_claim_position"),
    )

    evidence_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    claim_id: Mapped[str] = mapped_column(
        ForeignKey("claims.claim_id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str] = mapped_column(String(64), nullable=False)
    passage: Mapped[str] = mapped_column(Text, nullable=False)
    similarity: Mapped[float] = mapped_column(Float, nullable=False)


class ModelPredictionRecord(Base):
    """A model prediction kept separately from the final claim decision."""

    __tablename__ = "model_predictions"

    prediction_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    claim_id: Mapped[str] = mapped_column(
        ForeignKey("claims.claim_id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    predicted_label: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BenchmarkRunRecord(Base):
    """One measured benchmark execution."""

    __tablename__ = "benchmark_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_benchmark_runs_status",
        ),
    )

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    benchmark_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metrics: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)


class BenchmarkResultRecord(Base):
    """The expected and actual outcome for one benchmark example."""

    __tablename__ = "benchmark_results"
    __table_args__ = (
        UniqueConstraint("run_id", "example_id", name="uq_benchmark_result_example"),
    )

    result_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("benchmark_runs.run_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    example_id: Mapped[str] = mapped_column(String(128), nullable=False)
    expected_label: Mapped[str] = mapped_column(String(64), nullable=False)
    actual_label: Mapped[str] = mapped_column(String(64), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False)
