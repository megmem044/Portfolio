"""Add retry and failure details for asynchronous evaluation."""

from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.add_column(sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("failure_message", sa.Text()))


def downgrade() -> None:
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.drop_column("failure_message")
        batch.drop_column("attempt_count")
