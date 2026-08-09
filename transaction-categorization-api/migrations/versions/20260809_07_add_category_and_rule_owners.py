"""Separate shared defaults from user-created categories and rules.

Revision ID: 20260809_07
Revises: 20260809_06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260809_07"
down_revision: Union[str, None] = "20260809_06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LEGACY_EMAIL = "legacy-data@local.invalid"
STARTER_KEYWORDS = ("starbucks", "restaurant", "uber", "lyft", "walmart", "grocery")


def get_or_create_legacy_user(connection) -> int:
    user_id = connection.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": LEGACY_EMAIL},
    ).scalar_one_or_none()
    if user_id is not None:
        return user_id

    connection.execute(
        sa.text(
            "INSERT INTO users (email, password_hash, is_active) "
            "VALUES (:email, :password_hash, :is_active)"
        ),
        {"email": LEGACY_EMAIL, "password_hash": "login-disabled", "is_active": False},
    )
    return connection.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": LEGACY_EMAIL},
    ).scalar_one()


def upgrade() -> None:
    connection = op.get_bind()
    op.add_column("categories", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.add_column(
        "category_rules",
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("category_rules", sa.Column("owner_id", sa.Integer(), nullable=True))

    placeholders = ", ".join(f":keyword_{index}" for index, _ in enumerate(STARTER_KEYWORDS))
    keyword_values = {
        f"keyword_{index}": keyword
        for index, keyword in enumerate(STARTER_KEYWORDS)
    }
    connection.execute(
        sa.text(
            f"UPDATE category_rules SET is_default = :is_default "
            f"WHERE keyword IN ({placeholders})"
        ),
        {"is_default": True, **keyword_values},
    )

    custom_category_count = connection.execute(
        sa.text("SELECT COUNT(*) FROM categories WHERE is_default = :is_default"),
        {"is_default": False},
    ).scalar_one()
    custom_rule_count = connection.execute(
        sa.text("SELECT COUNT(*) FROM category_rules WHERE is_default = :is_default"),
        {"is_default": False},
    ).scalar_one()
    if custom_category_count or custom_rule_count:
        legacy_user_id = get_or_create_legacy_user(connection)
        connection.execute(
            sa.text(
                "UPDATE categories SET owner_id = :owner_id "
                "WHERE is_default = :is_default"
            ),
            {"owner_id": legacy_user_id, "is_default": False},
        )
        connection.execute(
            sa.text(
                "UPDATE category_rules SET owner_id = :owner_id "
                "WHERE is_default = :is_default"
            ),
            {"owner_id": legacy_user_id, "is_default": False},
        )

    with op.batch_alter_table("categories") as batch_op:
        batch_op.create_foreign_key(
            "fk_categories_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
        )
        batch_op.create_unique_constraint(
            "uq_categories_owner_name",
            ["owner_id", "name"],
        )
    with op.batch_alter_table("category_rules") as batch_op:
        batch_op.create_foreign_key(
            "fk_category_rules_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
        )
        batch_op.create_unique_constraint(
            "uq_category_rules_owner_keyword",
            ["owner_id", "keyword"],
        )
        batch_op.alter_column("is_default", server_default=None)

    op.drop_index("ix_categories_name", table_name="categories")
    op.create_index("ix_categories_name", "categories", ["name"], unique=False)
    op.drop_index("ix_category_rules_keyword", table_name="category_rules")
    op.create_index(
        "ix_category_rules_keyword",
        "category_rules",
        ["keyword"],
        unique=False,
    )
    op.create_index("ix_categories_owner_id", "categories", ["owner_id"], unique=False)
    op.create_index(
        "ix_category_rules_owner_id",
        "category_rules",
        ["owner_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_category_rules_owner_id", table_name="category_rules")
    op.drop_index("ix_categories_owner_id", table_name="categories")
    op.drop_index("ix_category_rules_keyword", table_name="category_rules")
    op.create_index(
        "ix_category_rules_keyword",
        "category_rules",
        ["keyword"],
        unique=True,
    )
    op.drop_index("ix_categories_name", table_name="categories")
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    with op.batch_alter_table("category_rules") as batch_op:
        batch_op.drop_constraint("uq_category_rules_owner_keyword", type_="unique")
        batch_op.drop_constraint("fk_category_rules_owner_id_users", type_="foreignkey")
        batch_op.drop_column("owner_id")
        batch_op.drop_column("is_default")
    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_constraint("uq_categories_owner_name", type_="unique")
        batch_op.drop_constraint("fk_categories_owner_id_users", type_="foreignkey")
        batch_op.drop_column("owner_id")
