"""Add composite indexes for owner-scoped analytics.

Revision ID: 20260824_11
Revises: 20260824_10
"""
from typing import Sequence, Union
from alembic import op

revision: str = "20260824_11"
down_revision: Union[str, None] = "20260824_10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index("ix_transactions_owner_date", "transactions", ["owner_id", "date"])
    op.create_index("ix_transactions_owner_merchant", "transactions", ["owner_id", "merchant"])

def downgrade() -> None:
    op.drop_index("ix_transactions_owner_merchant", table_name="transactions")
    op.drop_index("ix_transactions_owner_date", table_name="transactions")
