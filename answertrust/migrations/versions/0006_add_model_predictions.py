"""Move NLI output into a model predictions table."""

from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_predictions",
        sa.Column("prediction_id", sa.String(length=36), primary_key=True),
        sa.Column("claim_id", sa.String(length=36), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("predicted_label", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.claim_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_model_predictions_claim_id", "model_predictions", ["claim_id"])

    connection = op.get_bind()
    claims = sa.table(
        "claims",
        sa.column("claim_id", sa.String),
        sa.column("nli_label", sa.String),
        sa.column("nli_confidence", sa.Float),
    )
    predictions = sa.table(
        "model_predictions",
        sa.column("prediction_id", sa.String),
        sa.column("claim_id", sa.String),
        sa.column("model_name", sa.String),
        sa.column("predicted_label", sa.String),
        sa.column("confidence", sa.Float),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    for claim_id, label, confidence in connection.execute(
        sa.select(claims.c.claim_id, claims.c.nli_label, claims.c.nli_confidence).where(
            claims.c.nli_label.is_not(None), claims.c.nli_confidence.is_not(None)
        )
    ):
        connection.execute(
            predictions.insert().values(
                prediction_id=str(uuid4()),
                claim_id=claim_id,
                model_name="nli-classifier",
                predicted_label=label,
                confidence=confidence,
                created_at=datetime.now(timezone.utc),
            )
        )
    with op.batch_alter_table("claims") as batch:
        batch.drop_column("nli_label")
        batch.drop_column("nli_confidence")


def downgrade() -> None:
    with op.batch_alter_table("claims") as batch:
        batch.add_column(sa.Column("nli_label", sa.String(length=32)))
        batch.add_column(sa.Column("nli_confidence", sa.Float()))
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE claims SET nli_label = "
            "(SELECT predicted_label FROM model_predictions WHERE model_predictions.claim_id = claims.claim_id LIMIT 1), "
            "nli_confidence = (SELECT confidence FROM model_predictions WHERE model_predictions.claim_id = claims.claim_id LIMIT 1)"
        )
    )
    op.drop_index("ix_model_predictions_claim_id", table_name="model_predictions")
    op.drop_table("model_predictions")
