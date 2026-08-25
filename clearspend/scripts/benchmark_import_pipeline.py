"""Generate synthetic CSV rows and benchmark parsing/validation without real data."""

import argparse
import json
import io
from pathlib import Path
import sys
import tracemalloc
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import Column, Date, Integer, MetaData, Numeric, String, Table, create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.category import Category  # noqa: F401
from app.models.category_rule import CategoryRule  # noqa: F401
from app.models.revoked_token import RevokedToken  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.transaction_import import TransactionImport, TransactionImportRow  # noqa: F401
from app.models.user import User  # noqa: F401
from app.schemas.transaction_import import ImportMapping
from app.services.transaction_imports import iter_classified_rows, iter_csv


def generate_csv(size: int) -> str:
    lines = ["date,merchant,amount,currency"]
    lines.extend(f"2026-{(number % 12) + 1:02d}-{(number % 28) + 1:02d},Merchant {number},10.{number % 100:02d},USD" for number in range(size))
    return "\n".join(lines)


def benchmark(size: int) -> dict:
    content = generate_csv(size)
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    tracemalloc.start()
    started = perf_counter()
    rows = iter_csv(io.StringIO(content))
    parsed_at = perf_counter()
    with Session(engine) as session:
        classified_count = sum(1 for _ in iter_classified_rows(rows, ImportMapping(), 1, session))
    finished = perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"rows": classified_count, "stream_setup_seconds": round(parsed_at - started, 6), "parse_validation_seconds": round(finished - parsed_at, 6), "total_seconds": round(finished - started, 6), "rows_per_second": round(size / (finished - started), 2), "peak_memory_mib": round(peak / 1024 / 1024, 2)}


benchmark_metadata = MetaData()
benchmark_table = Table(
    "benchmark_import_inserts",
    benchmark_metadata,
    Column("id", Integer, primary_key=True),
    Column("date", Date, nullable=False),
    Column("merchant", String(200), nullable=False),
    Column("amount", Numeric(12, 2), nullable=False),
    Column("currency", String(3), nullable=False),
    Column("fingerprint", String(64), nullable=False),
)


def insertion_rows(size: int) -> list[dict]:
    from datetime import date
    from decimal import Decimal
    import hashlib

    return [{"id": number + 1, "date": date(2026, (number % 12) + 1, (number % 28) + 1), "merchant": f"Merchant {number}", "amount": Decimal(f"10.{number % 100:02d}"), "currency": "USD", "fingerprint": hashlib.sha256(str(number).encode()).hexdigest()} for number in range(size)]


def measure_insert(engine, rows: list[dict], strategy: str, batch_size: int) -> dict:
    benchmark_metadata.drop_all(engine, checkfirst=True)
    benchmark_metadata.create_all(engine)
    started = perf_counter()
    with engine.begin() as connection:
        if strategy == "row_by_row":
            for row in rows:
                connection.execute(benchmark_table.insert(), row)
        elif strategy == "batch":
            for offset in range(0, len(rows), batch_size):
                connection.execute(benchmark_table.insert(), rows[offset : offset + batch_size])
        elif strategy == "bulk":
            connection.execute(benchmark_table.insert(), rows)
        else:
            raise ValueError(strategy)
    elapsed = perf_counter() - started
    return {"strategy": strategy, "rows": len(rows), "batch_size": batch_size if strategy == "batch" else None, "seconds": round(elapsed, 6), "rows_per_second": round(len(rows) / elapsed, 2)}


def measure_postgres_copy(engine, rows: list[dict]) -> dict:
    benchmark_metadata.drop_all(engine, checkfirst=True)
    benchmark_metadata.create_all(engine)
    started = perf_counter()
    raw = engine.raw_connection()
    try:
        with raw.driver_connection.cursor().copy("COPY benchmark_import_inserts (id, date, merchant, amount, currency, fingerprint) FROM STDIN") as copy:
            for row in rows:
                copy.write_row((row["id"], row["date"], row["merchant"], row["amount"], row["currency"], row["fingerprint"]))
        raw.commit()
    finally:
        raw.close()
    elapsed = perf_counter() - started
    return {"strategy": "postgres_copy", "rows": len(rows), "batch_size": None, "seconds": round(elapsed, 6), "rows_per_second": round(len(rows) / elapsed, 2)}


def benchmark_insertions(size: int, database_url: str, batch_size: int) -> list[dict]:
    engine = create_engine(database_url)
    rows = insertion_rows(size)
    connected = False
    try:
        with engine.connect():
            connected = True
        results = [measure_insert(engine, rows, strategy, batch_size) for strategy in ("row_by_row", "batch", "bulk")]
        if engine.dialect.name == "postgresql":
            results.append(measure_postgres_copy(engine, rows))
        return results
    finally:
        if connected:
            benchmark_metadata.drop_all(engine, checkfirst=True)
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[1_000, 10_000, 100_000])
    parser.add_argument("--phase", choices=("processing", "insertion", "all"), default="all")
    parser.add_argument("--database-url", default="sqlite://")
    parser.add_argument("--batch-size", type=int, default=1_000)
    args = parser.parse_args()
    report = {}
    if args.phase in ("processing", "all"):
        report["processing"] = [benchmark(size) for size in args.sizes]
    if args.phase in ("insertion", "all"):
        report["insertion"] = {str(size): benchmark_insertions(size, args.database_url, args.batch_size) for size in args.sizes}
    print(json.dumps(report, indent=2))
