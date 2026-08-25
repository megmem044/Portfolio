"""Add import performance metrics and row review decisions.

Revision ID: 20260824_10
Revises: 20260824_09
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260824_10"
down_revision: Union[str, None] = "20260824_09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("transaction_imports") as batch_op:
        batch_op.add_column(sa.Column("parsing_ms", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("validation_ms", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("staging_ms", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("commit_ms", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("rows_per_second", sa.Numeric(12, 2), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("peak_memory_bytes", sa.Integer(), nullable=True))
    with op.batch_alter_table("transaction_import_rows") as batch_op:
        batch_op.add_column(sa.Column("review_decision", sa.String(length=20), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("transaction_import_rows") as batch_op:
        batch_op.drop_column("review_decision")
    with op.batch_alter_table("transaction_imports") as batch_op:
        batch_op.drop_column("peak_memory_bytes")
        batch_op.drop_column("rows_per_second")
        batch_op.drop_column("commit_ms")
        batch_op.drop_column("staging_ms")
        batch_op.drop_column("validation_ms")
        batch_op.drop_column("parsing_ms")
