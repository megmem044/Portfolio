"""Store automatic merchant-category rules.

Revision ID: 20260808_04
Revises: 20260808_03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260808_04"
down_revision: Union[str, None] = "20260808_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STARTER_RULES = (
    ("starbucks", "Food & Dining", 10),
    ("restaurant", "Food & Dining", 20),
    ("uber", "Transportation", 30),
    ("lyft", "Transportation", 40),
    ("walmart", "Groceries", 50),
    ("grocery", "Groceries", 60),
)


def upgrade() -> None:
    op.create_table(
        "category_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=100), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_category_rules_category_id",
        "category_rules",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        "ix_category_rules_keyword",
        "category_rules",
        ["keyword"],
        unique=True,
    )
    op.create_index(
        "ix_category_rules_priority",
        "category_rules",
        ["priority"],
        unique=False,
    )

    connection = op.get_bind()
    for keyword, category_name, priority in STARTER_RULES:
        connection.execute(
            sa.text(
                "INSERT INTO category_rules "
                "(keyword, category_id, priority, is_active) "
                "SELECT :keyword, id, :priority, :is_active "
                "FROM categories WHERE name = :category_name"
            ),
            {
                "keyword": keyword,
                "category_name": category_name,
                "priority": priority,
                "is_active": True,
            },
        )


def downgrade() -> None:
    op.drop_index("ix_category_rules_priority", table_name="category_rules")
    op.drop_index("ix_category_rules_keyword", table_name="category_rules")
    op.drop_index("ix_category_rules_category_id", table_name="category_rules")
    op.drop_table("category_rules")
