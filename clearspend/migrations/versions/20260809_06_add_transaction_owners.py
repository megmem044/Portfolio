"""Connect every transaction to its owner.

Revision ID: 20260809_06
Revises: 20260809_05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260809_06"
down_revision: Union[str, None] = "20260809_05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LEGACY_EMAIL = "legacy-data@local.invalid"


def upgrade() -> None:
    connection = op.get_bind()
    op.add_column("transactions", sa.Column("owner_id", sa.Integer(), nullable=True))

    transaction_count = connection.execute(
        sa.text("SELECT COUNT(*) FROM transactions")
    ).scalar_one()
    if transaction_count:
        connection.execute(
            sa.text(
                "INSERT INTO users (email, password_hash, is_active) "
                "VALUES (:email, :password_hash, :is_active)"
            ),
            {
                "email": LEGACY_EMAIL,
                "password_hash": "login-disabled",
                "is_active": False,
            },
        )
        legacy_user_id = connection.execute(
            sa.text("SELECT id FROM users WHERE email = :email"),
            {"email": LEGACY_EMAIL},
        ).scalar_one()
        connection.execute(
            sa.text("UPDATE transactions SET owner_id = :owner_id"),
            {"owner_id": legacy_user_id},
        )

    with op.batch_alter_table("transactions") as batch_op:
        batch_op.alter_column("owner_id", nullable=False)
        batch_op.create_foreign_key(
            "fk_transactions_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
        )

    op.create_index(
        "ix_transactions_owner_id",
        "transactions",
        ["owner_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_owner_id", table_name="transactions")
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.drop_constraint(
            "fk_transactions_owner_id_users",
            type_="foreignkey",
        )
        batch_op.drop_column("owner_id")

    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM users WHERE email = :email"),
        {"email": LEGACY_EMAIL},
    )
