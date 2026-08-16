"""Add normalized claim and evidence tables."""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "claims",
        sa.Column("claim_id", sa.String(length=36), primary_key=True),
        sa.Column("evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("label", sa.String(length=32), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("failure_types", sa.JSON(), nullable=False),
        sa.Column("nli_label", sa.String(length=32)),
        sa.Column("nli_confidence", sa.Float()),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations_v2.evaluation_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("evaluation_id", "position", name="uq_claims_evaluation_position"),
    )
    op.create_index("ix_claims_evaluation_id", "claims", ["evaluation_id"])
    op.create_table(
        "evidence_passages",
        sa.Column("evidence_id", sa.String(length=36), primary_key=True),
        sa.Column("claim_id", sa.String(length=36), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=64), nullable=False),
        sa.Column("passage", sa.Text(), nullable=False),
        sa.Column("similarity", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.claim_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("claim_id", "position", name="uq_evidence_claim_position"),
    )
    op.create_index("ix_evidence_passages_claim_id", "evidence_passages", ["claim_id"])


def downgrade() -> None:
    op.drop_index("ix_evidence_passages_claim_id", table_name="evidence_passages")
    op.drop_table("evidence_passages")
    op.drop_index("ix_claims_evaluation_id", table_name="claims")
    op.drop_table("claims")
