"""Print PostgreSQL execution plans for ClearSpend's priority analytics queries."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import create_engine, text
from app.core.config import settings

QUERIES = {
    "monthly_trends": """SELECT EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date), COUNT(*), SUM(amount) FROM transactions WHERE owner_id = :owner_id GROUP BY 1, 2 ORDER BY 1, 2""",
    "merchant_summary": """SELECT merchant, COUNT(*), SUM(amount), AVG(amount) FROM transactions WHERE owner_id = :owner_id GROUP BY merchant ORDER BY SUM(amount) DESC LIMIT 20""",
    "filtered_export": """SELECT date, merchant, category_id, amount FROM transactions WHERE owner_id = :owner_id AND date >= DATE '2026-01-01' AND date < DATE '2027-01-01' ORDER BY date DESC""",
}

if __name__ == "__main__":
    engine = create_engine(settings.database_url)
    if engine.dialect.name != "postgresql": raise SystemExit("Set DATABASE_URL to PostgreSQL.")
    with engine.connect() as connection:
        owner_id = connection.execute(text("SELECT id FROM users ORDER BY id LIMIT 1")).scalar() or 0
        for name, query in QUERIES.items():
            print(f"\n{name}\n{'-' * len(name)}")
            for line, in connection.execute(text(f"EXPLAIN (ANALYZE, BUFFERS) {query}"), {"owner_id": owner_id}): print(line)
