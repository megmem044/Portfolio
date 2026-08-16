"""Move old claim JSON into normalized tables."""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    evaluations = sa.table(
        "evaluations_v2",
        sa.column("evaluation_id", sa.String),
        sa.column("claim_results", sa.JSON),
    )
    claims = sa.table(
        "claims",
        sa.column("claim_id", sa.String),
        sa.column("evaluation_id", sa.String),
        sa.column("position", sa.Integer),
        sa.column("claim_text", sa.Text),
        sa.column("label", sa.String),
        sa.column("explanation", sa.Text),
        sa.column("failure_types", sa.JSON),
        sa.column("nli_label", sa.String),
        sa.column("nli_confidence", sa.Float),
    )
    evidence_table = sa.table(
        "evidence_passages",
        sa.column("evidence_id", sa.String),
        sa.column("claim_id", sa.String),
        sa.column("position", sa.Integer),
        sa.column("section", sa.String),
        sa.column("passage", sa.Text),
        sa.column("similarity", sa.Float),
    )
    existing = set(connection.scalars(sa.select(claims.c.evaluation_id)))
    for evaluation_id, claim_results in connection.execute(
        sa.select(evaluations.c.evaluation_id, evaluations.c.claim_results)
    ):
        if evaluation_id in existing:
            continue
        for claim_position, claim in enumerate(claim_results or []):
            claim_id = str(uuid4())
            connection.execute(
                claims.insert().values(
                    claim_id=claim_id,
                    evaluation_id=evaluation_id,
                    position=claim_position,
                    claim_text=claim["claim"],
                    label=claim["label"],
                    explanation=claim["explanation"],
                    failure_types=claim.get("failure_types", []),
                    nli_label=claim.get("nli_label"),
                    nli_confidence=claim.get("nli_confidence"),
                )
            )
            for evidence_position, evidence in enumerate(claim.get("evidence", [])):
                connection.execute(
                    evidence_table.insert().values(
                        evidence_id=str(uuid4()),
                        claim_id=claim_id,
                        position=evidence_position,
                        section=evidence["section"],
                        passage=evidence["passage"],
                        similarity=evidence["similarity"],
                    )
                )
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.drop_column("claim_results")


def downgrade() -> None:
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.add_column(sa.Column("claim_results", sa.JSON()))
