"""Move existing paper text into the papers table."""

from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    evaluations = sa.table(
        "evaluations_v2",
        sa.column("evaluation_id", sa.String),
        sa.column("paper_id", sa.String),
        sa.column("paper_text", sa.Text),
    )
    papers = sa.table(
        "papers",
        sa.column("paper_id", sa.String),
        sa.column("content_hash", sa.String),
        sa.column("paper_text", sa.Text),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    rows = connection.execute(
        sa.select(evaluations.c.evaluation_id, evaluations.c.paper_text).where(
            evaluations.c.paper_id.is_(None)
        )
    ).all()
    known_papers: dict[str, str] = {
        content_hash: paper_id
        for content_hash, paper_id in connection.execute(
            sa.select(papers.c.content_hash, papers.c.paper_id)
        )
    }
    for evaluation_id, paper_text in rows:
        content_hash = sha256(paper_text.encode("utf-8")).hexdigest()
        paper_id = known_papers.get(content_hash)
        if paper_id is None:
            paper_id = str(uuid4())
            connection.execute(
                papers.insert().values(
                    paper_id=paper_id,
                    content_hash=content_hash,
                    paper_text=paper_text,
                    created_at=datetime.now(timezone.utc),
                )
            )
            known_papers[content_hash] = paper_id
        connection.execute(
            evaluations.update()
            .where(evaluations.c.evaluation_id == evaluation_id)
            .values(paper_id=paper_id)
        )
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.alter_column("paper_id", existing_type=sa.String(length=36), nullable=False)
        batch.drop_column("paper_text")


def downgrade() -> None:
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.add_column(sa.Column("paper_text", sa.Text()))
        batch.alter_column("paper_id", existing_type=sa.String(length=36), nullable=True)
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE evaluations_v2 SET paper_text = "
            "(SELECT papers.paper_text FROM papers WHERE papers.paper_id = evaluations_v2.paper_id)"
        )
    )
    with op.batch_alter_table("evaluations_v2") as batch:
        batch.alter_column("paper_text", existing_type=sa.Text(), nullable=False)
