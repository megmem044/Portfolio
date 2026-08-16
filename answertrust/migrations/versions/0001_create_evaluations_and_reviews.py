"""Create evaluation and review tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evaluations_v2",
        sa.Column("evaluation_id", sa.String(length=36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("paper_text", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("overall_score", sa.Integer()),
        sa.Column("final_decision", sa.String(length=16)),
        sa.Column("claim_results", sa.JSON()),
        sa.Column("dimension_scores", sa.JSON()),
        sa.Column("main_concern", sa.Text()),
        sa.Column("explanation", sa.Text()),
        sa.Column("recommended_action", sa.Text()),
        sa.Column("total_latency_ms", sa.Integer()),
        sa.CheckConstraint(
            "state IN ('QUEUED', 'PROCESSING', 'COMPLETED', 'REVIEW_REQUIRED', 'APPROVED', 'REJECTED', 'FAILED', 'RETRYING')",
            name="ck_evaluations_v2_state",
        ),
        sa.CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)",
            name="ck_evaluations_v2_score",
        ),
    )
    op.create_index("ix_evaluations_v2_created_at", "evaluations_v2", ["created_at"])
    op.create_index("ix_evaluations_v2_state", "evaluations_v2", ["state"])
    op.create_table(
        "review_decisions",
        sa.Column(
            "evaluation_id",
            sa.String(length=36),
            sa.ForeignKey("evaluations_v2.evaluation_id"),
            primary_key=True,
        ),
        sa.Column("reviewer_decision", sa.String(length=16), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "reviewer_decision IN ('APPROVE', 'REJECT')",
            name="ck_review_decisions_decision",
        ),
    )


def downgrade() -> None:
    op.drop_table("review_decisions")
    op.drop_index("ix_evaluations_v2_state", table_name="evaluations_v2")
    op.drop_index("ix_evaluations_v2_created_at", table_name="evaluations_v2")
    op.drop_table("evaluations_v2")
