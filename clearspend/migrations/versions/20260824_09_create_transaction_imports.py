"""Create transaction import staging, lineage, and fingerprint storage.

Revision ID: 20260824_09
Revises: 20260809_08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260824_09"
down_revision: Union[str, None] = "20260809_08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(sa.Column("fingerprint", sa.String(length=64), nullable=True))
        batch_op.create_index("ix_transactions_fingerprint", ["fingerprint"])
        batch_op.create_unique_constraint("uq_transaction_owner_fingerprint", ["owner_id", "fingerprint"])
    op.create_table(
        "transaction_imports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("input_count", sa.Integer(), nullable=False),
        sa.Column("imported_count", sa.Integer(), nullable=False),
        sa.Column("duplicate_count", sa.Integer(), nullable=False),
        sa.Column("invalid_count", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transaction_imports_owner_id", "transaction_imports", ["owner_id"])
    op.create_index("ix_transaction_imports_state", "transaction_imports", ["state"])
    op.create_table(
        "transaction_import_rows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("raw_values", sa.JSON(), nullable=False),
        sa.Column("merchant_raw", sa.String(length=500), nullable=True),
        sa.Column("merchant", sa.String(length=200), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("fingerprint", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("error_reason", sa.Text(), nullable=True),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["import_id"], ["transaction_imports.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("import_id", "row_number", name="uq_import_row_number"),
        sa.UniqueConstraint("transaction_id"),
    )
    op.create_index("ix_transaction_import_rows_import_id", "transaction_import_rows", ["import_id"])
    op.create_index("ix_transaction_import_rows_fingerprint", "transaction_import_rows", ["fingerprint"])
    op.create_index("ix_transaction_import_rows_status", "transaction_import_rows", ["status"])


def downgrade() -> None:
    op.drop_table("transaction_import_rows")
    op.drop_table("transaction_imports")
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.drop_constraint("uq_transaction_owner_fingerprint", type_="unique")
        batch_op.drop_index("ix_transactions_fingerprint")
        batch_op.drop_column("fingerprint")
