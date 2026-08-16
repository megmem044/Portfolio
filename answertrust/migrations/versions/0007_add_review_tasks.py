"""Add persistent human review tasks."""

from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review_tasks",
        sa.Column("task_id", sa.String(length=36), primary_key=True),
        sa.Column("evaluation_id", sa.String(length=36), nullable=False, unique=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations_v2.evaluation_id"]),
        sa.CheckConstraint("status IN ('OPEN', 'RESOLVED')", name="ck_review_tasks_status"),
    )
    op.create_index("ix_review_tasks_evaluation_id", "review_tasks", ["evaluation_id"])
    with op.batch_alter_table("review_decisions") as batch:
        batch.add_column(sa.Column("task_id", sa.String(length=36)))

    connection = op.get_bind()
    evaluations = sa.table(
        "evaluations_v2",
        sa.column("evaluation_id", sa.String),
        sa.column("state", sa.String),
    )
    decisions = sa.table(
        "review_decisions",
        sa.column("evaluation_id", sa.String),
        sa.column("task_id", sa.String),
        sa.column("reviewed_at", sa.DateTime(timezone=True)),
    )
    tasks = sa.table(
        "review_tasks",
        sa.column("task_id", sa.String),
        sa.column("evaluation_id", sa.String),
        sa.column("status", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("resolved_at", sa.DateTime(timezone=True)),
    )
    reviewed = {
        evaluation_id: reviewed_at
        for evaluation_id, reviewed_at in connection.execute(
            sa.select(decisions.c.evaluation_id, decisions.c.reviewed_at)
        )
    }
    relevant_ids = set(reviewed)
    relevant_ids.update(
        connection.scalars(
            sa.select(evaluations.c.evaluation_id).where(
                evaluations.c.state == "REVIEW_REQUIRED"
            )
        )
    )
    now = datetime.now(timezone.utc)
    for evaluation_id in relevant_ids:
        task_id = str(uuid4())
        resolved_at = reviewed.get(evaluation_id)
        connection.execute(
            tasks.insert().values(
                task_id=task_id,
                evaluation_id=evaluation_id,
                status="RESOLVED" if evaluation_id in reviewed else "OPEN",
                created_at=resolved_at or now,
                resolved_at=resolved_at,
            )
        )
        if evaluation_id in reviewed:
            connection.execute(
                decisions.update()
                .where(decisions.c.evaluation_id == evaluation_id)
                .values(task_id=task_id)
            )
    with op.batch_alter_table("review_decisions") as batch:
        batch.alter_column("task_id", existing_type=sa.String(length=36), nullable=False)
        batch.create_foreign_key(
            "fk_review_decisions_task_id", "review_tasks", ["task_id"], ["task_id"]
        )
        batch.create_unique_constraint("uq_review_decisions_task_id", ["task_id"])


def downgrade() -> None:
    with op.batch_alter_table("review_decisions") as batch:
        batch.drop_constraint("uq_review_decisions_task_id", type_="unique")
        batch.drop_constraint("fk_review_decisions_task_id", type_="foreignkey")
        batch.drop_column("task_id")
    op.drop_index("ix_review_tasks_evaluation_id", table_name="review_tasks")
    op.drop_table("review_tasks")
