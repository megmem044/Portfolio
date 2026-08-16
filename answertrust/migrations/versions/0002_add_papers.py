"""Store papers separately and link evaluations to them."""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "papers",
        sa.Column("paper_id", sa.String(length=36), primary_key=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("paper_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.add_column(sa.Column("paper_id", sa.String(length=36)))
        batch.create_foreign_key(
            "fk_evaluations_v2_paper_id", "papers", ["paper_id"], ["paper_id"]
        )
        batch.create_index("ix_evaluations_v2_paper_id", ["paper_id"])


def downgrade() -> None:
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.drop_index("ix_evaluations_v2_paper_id")
        batch.drop_constraint("fk_evaluations_v2_paper_id", type_="foreignkey")
        batch.drop_column("paper_id")
    op.drop_table("papers")
