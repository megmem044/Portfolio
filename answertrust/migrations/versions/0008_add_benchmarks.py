"""Add benchmark run and result tables."""

from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "benchmark_runs",
        sa.Column("run_id", sa.String(length=36), primary_key=True),
        sa.Column("benchmark_name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("metrics", sa.JSON()),
        sa.Column("error_message", sa.Text()),
        sa.CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_benchmark_runs_status",
        ),
    )
    op.create_index("ix_benchmark_runs_status", "benchmark_runs", ["status"])
    op.create_index("ix_benchmark_runs_started_at", "benchmark_runs", ["started_at"])
    op.create_table(
        "benchmark_results",
        sa.Column("result_id", sa.String(length=36), primary_key=True),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("example_id", sa.String(length=128), nullable=False),
        sa.Column("expected_label", sa.String(length=64), nullable=False),
        sa.Column("actual_label", sa.String(length=64), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["benchmark_runs.run_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("run_id", "example_id", name="uq_benchmark_result_example"),
    )
    op.create_index("ix_benchmark_results_run_id", "benchmark_results", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_benchmark_results_run_id", table_name="benchmark_results")
    op.drop_table("benchmark_results")
    op.drop_index("ix_benchmark_runs_started_at", table_name="benchmark_runs")
    op.drop_index("ix_benchmark_runs_status", table_name="benchmark_runs")
    op.drop_table("benchmark_runs")
