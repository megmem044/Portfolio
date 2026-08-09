"""Compare a PostgreSQL date query before and after adding an index."""

from sqlalchemy import create_engine, text

from app.core.config import settings


ROW_COUNT = 50_000
DATE_QUERY = """
    SELECT *
    FROM benchmark_transactions
    WHERE transaction_date >= DATE '2025-01-01'
      AND transaction_date < DATE '2025-02-01'
"""


def explain_query(connection) -> tuple[str, float]:
    result = connection.execute(
        text(f"EXPLAIN (ANALYZE, FORMAT JSON) {DATE_QUERY}")
    ).scalar_one()
    report = result[0]
    return report["Plan"]["Node Type"], report["Execution Time"]


def main() -> None:
    engine = create_engine(settings.database_url)
    if engine.dialect.name != "postgresql":
        raise SystemExit("This measurement requires a PostgreSQL DATABASE_URL.")

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TEMPORARY TABLE benchmark_transactions (
                    id INTEGER PRIMARY KEY,
                    amount NUMERIC(12, 2) NOT NULL,
                    merchant VARCHAR(200) NOT NULL,
                    transaction_date DATE NOT NULL
                ) ON COMMIT DROP
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO benchmark_transactions
                    (id, amount, merchant, transaction_date)
                SELECT
                    number,
                    ((number % 5000) + 1) / 100.0,
                    'Merchant ' || (number % 200),
                    DATE '2024-01-01' + (number % 1000)
                FROM generate_series(1, :row_count) AS number
                """
            ),
            {"row_count": ROW_COUNT},
        )
        connection.execute(text("ANALYZE benchmark_transactions"))
        before_method, before_time = explain_query(connection)

        connection.execute(
            text(
                "CREATE INDEX benchmark_transactions_date_idx "
                "ON benchmark_transactions (transaction_date)"
            )
        )
        connection.execute(text("ANALYZE benchmark_transactions"))
        after_method, after_time = explain_query(connection)

    improvement = before_time / after_time if after_time else float("inf")
    print(f"Rows tested: {ROW_COUNT:,}")
    print(f"Before index: {before_method}, {before_time:.3f} ms")
    print(f"After index:  {after_method}, {after_time:.3f} ms")
    print(f"Measured speedup: {improvement:.2f}x")
    print("Temporary benchmark data was removed automatically.")


if __name__ == "__main__":
    main()
