"""Store categories in their own table.

Revision ID: 20260808_03
Revises: 20260808_02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260808_03"
down_revision: Union[str, None] = "20260808_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_CATEGORIES = (
    "Food & Dining",
    "Transportation",
    "Groceries",
    "Uncategorized",
)


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    categories = sa.table(
        "categories",
        sa.column("name", sa.String),
        sa.column("is_default", sa.Boolean),
    )
    op.bulk_insert(
        categories,
        [{"name": name, "is_default": True} for name in DEFAULT_CATEGORIES],
    )

    connection = op.get_bind()
    existing_names = list(
        connection.execute(
            sa.text("SELECT DISTINCT category FROM transactions")
        ).scalars()
    )
    for name in existing_names:
        category_exists = connection.execute(
            sa.text("SELECT 1 FROM categories WHERE name = :name"),
            {"name": name},
        ).first()
        if category_exists is None:
            connection.execute(
                sa.text(
                    "INSERT INTO categories (name, is_default) "
                    "VALUES (:name, :is_default)"
                ),
                {"name": name, "is_default": False},
            )

    op.add_column("transactions", sa.Column("category_id", sa.Integer(), nullable=True))
    connection.execute(
        sa.text(
            "UPDATE transactions SET category_id = "
            "(SELECT id FROM categories WHERE categories.name = transactions.category)"
        )
    )
    op.drop_index("ix_transactions_category", table_name="transactions")

    with op.batch_alter_table("transactions") as batch_op:
        batch_op.alter_column("category_id", nullable=False)
        batch_op.create_foreign_key(
            "fk_transactions_category_id_categories",
            "categories",
            ["category_id"],
            ["id"],
        )
        batch_op.drop_column("category")

    op.create_index(
        "ix_transactions_category_id",
        "transactions",
        ["category_id"],
        unique=False,
    )


def downgrade() -> None:
    op.add_column("transactions", sa.Column("category", sa.String(100), nullable=True))
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE transactions SET category = "
            "(SELECT name FROM categories WHERE categories.id = transactions.category_id)"
        )
    )
    op.drop_index("ix_transactions_category_id", table_name="transactions")

    with op.batch_alter_table("transactions") as batch_op:
        batch_op.drop_constraint(
            "fk_transactions_category_id_categories",
            type_="foreignkey",
        )
        batch_op.drop_column("category_id")
        batch_op.alter_column("category", nullable=False)

    op.create_index(
        "ix_transactions_category",
        "transactions",
        ["category"],
        unique=False,
    )
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
