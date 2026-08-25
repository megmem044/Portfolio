# Focused SQL analytics

The authenticated analytics API exposes three read models:

- `GET /analytics/monthly-trends` groups trusted transactions by month and uses
  SQL `LAG` plus a three-row window to return previous totals, absolute and
  percentage changes, and rolling averages.
- `GET /analytics/merchants?limit=20` returns merchant totals, counts, and
  average transaction values ordered by spend.
- `GET /analytics/categories` returns category totals, counts, and share of the
  user's full trusted-transaction total.
- `GET /analytics/largest-transactions` returns the highest-value trusted rows.
- `GET /analytics/data-quality` reports uncategorized count and rate.
- `GET /transactions/export.csv` exports the authenticated user's filtered
  transaction dataset without requiring database access.

All queries filter by owner before aggregation. Responses preserve exact
two-decimal values, and automated tests compare analytical totals with seeded
trusted transactions.
