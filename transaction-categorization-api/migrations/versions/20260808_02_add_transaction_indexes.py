"""Add indexes for common transaction filters.

Revision ID: 20260808_02
Revises: 20260808_01
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260808_02"
down_revision: Union[str, None] = "20260808_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_transactions_category",
        "transactions",
        ["category"],
        unique=False,
    )
    op.create_index(
        "ix_transactions_date",
        "transactions",
        ["date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_date", table_name="transactions")
    op.drop_index("ix_transactions_category", table_name="transactions")
