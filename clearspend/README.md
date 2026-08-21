# ClearSpend

_Last updated: August 15, 2026_

ClearSpend is a personal finance data application. It turns messy transaction data from bank files and manual entries into clean, reliable records and useful spending reports.

The main focus of this project is data engineering: importing data, checking its quality, cleaning it, preventing duplicates, and using SQL to produce accurate analytics. The FastAPI backend and React website provide a simple way to use and demonstrate that data pipeline.

## How it works

```text
Bank CSV files or manual entries
              |
              v
       Import and staging
              |
              v
     Validation and cleaning
              |
              v
  Duplicate checks and review
              |
              v
     Trusted transactions
          /          \
         v            v
 Categorization   SQL analytics
         \            /
          v          v
        ClearSpend dashboard
```

ClearSpend will support different bank CSV formats by mapping them into one standard transaction format. Imported rows will first go into a staging area, where the app can explain errors and possible duplicates before saving approved records.

## What works today

- Register, sign in, sign out, and keep each user's data private
- Add, view, edit, and delete transactions
- Search, filter, sort, and page through transactions
- Suggest categories using merchant rules
- Create and manage categories and categorization rules through the API
- Calculate exact monthly totals by category in the database
- Run with SQLite for simple development or PostgreSQL
- Apply repeatable database changes with Alembic migrations
- Demonstrate a measured improvement from a PostgreSQL index
- Use a React dashboard for authentication, transactions, and monthly totals
- Test the main backend, database, and security behavior

## What comes next

The next major feature is a reliable CSV data pipeline. It will:

1. Accept files from different banks.
2. Map different column names into one standard format.
3. Store uploaded rows in staging tables before final approval.
4. Validate dates, amounts, merchants, and currencies.
5. Clean merchant names and other inconsistent values.
6. Mark rows as new, exact duplicates, possible duplicates, or invalid.
7. Preview results before saving transactions.
8. Make retries safe so the same file does not create duplicate records.
9. Reconcile every input row with an imported, duplicate, or invalid result.
10. Measure processing speed and data-quality results.

After importing is reliable, the project will add:

- SQL reports for monthly change, category share, merchant totals, rolling averages, and uncategorized transactions
- Analytics tables designed for reporting
- dbt models and data-quality tests
- CSV exports for analysts
- Import performance benchmarks using large generated datasets
- A small category model trained from reviewed corrections
- Monitoring for import quality and changes in categorization results
- Automated delivery and deployment checks

## Data correctness

Financial data must remain exact and explainable. ClearSpend uses Python `Decimal` values and exact database number types instead of binary floating-point values for money.

Important checks will include:

- Category totals add up to the monthly total.
- Imported, duplicate, and invalid rows add up to the number of input rows.
- Retrying an import does not create duplicate transactions.
- Every saved transaction can be traced back to its source import and row.
- Invalid data is explained instead of silently changed or discarded.

## Main technologies

- Python and FastAPI for the API and data-processing services
- PostgreSQL and SQL for storage, validation, and analytics
- SQLAlchemy and Alembic for database access and migrations
- dbt for planned analytics models and data tests
- React and TypeScript for the supporting web interface
- Pytest for automated backend and pipeline tests

## Run the backend

You need Python 3.11 or newer.

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install the application and test tools:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

3. Apply database migrations:

   ```powershell
   python -m alembic upgrade head
   ```

4. Start the API:

   ```powershell
   python -m uvicorn app.main:app --reload
   ```

5. Open `http://127.0.0.1:8000/docs` to explore the API.

Run backend tests with:

```powershell
python -m pytest
```

Copy `.env.example` to `.env` to change local settings. Never commit `.env` or real financial data.

## Run the frontend

From the `frontend` folder:

```powershell
npm install
npm run dev
```

Use `npm run lint` and `npm run build` to check the frontend.

## Project folders

- `app/api` contains API routes and shared request helpers.
- `app/services` contains business rules and categorization logic.
- `app/models` contains database models.
- `app/schemas` defines accepted and returned data.
- `app/db` manages database connections.
- `migrations` contains repeatable database changes.
- `tests` contains automated backend tests.
- `frontend` contains the React and TypeScript website.
- `docs` contains the product, architecture, database, frontend, and phase guides.

Planned data-pipeline and analytics folders will be added only when their features are implemented.

## Documentation

- [Project plan](PROJECT_PLAN.md): priorities, milestones, and completion checks
- [Product requirements](docs/product-requirements.md): user stories and expected behavior
- [Detailed phase plan](docs/phase-plan.md): the existing implementation log
- [Architecture guide](docs/architecture.md): how the current application is organized
- [PostgreSQL guide](docs/postgresql.md): database setup and performance notes
- [Frontend guide](docs/frontend.md): React structure and API integration
