"""Add users and identify reviewers in the audit trail."""

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('REVIEWER', 'ADMIN')", name="ck_users_role"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    with op.batch_alter_table("review_decisions") as batch:
        batch.add_column(sa.Column("reviewer_user_id", sa.String(length=36)))
        batch.create_foreign_key("fk_review_decisions_reviewer_user_id", "users", ["reviewer_user_id"], ["user_id"])
        batch.create_index("ix_review_decisions_reviewer_user_id", ["reviewer_user_id"])


def downgrade() -> None:
    with op.batch_alter_table("review_decisions") as batch:
        batch.drop_index("ix_review_decisions_reviewer_user_id")
        batch.drop_constraint("fk_review_decisions_reviewer_user_id", type_="foreignkey")
        batch.drop_column("reviewer_user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
