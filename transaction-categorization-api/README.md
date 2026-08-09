# Transaction Categorization

This project is an early version of an app that helps people organize their spending.

A user records a transaction with an amount, merchant, and date. The app suggests a category, saves the transaction, and includes it in a monthly spending summary.

Example:

`Starbucks, $8.50, July 10 → Food & Dining`

## What works today

- Add and save a transaction
- Suggest categories for a few known merchant names
- Search, filter, sort, and page through saved transactions
- View, edit, or delete one transaction
- Create and manage custom spending categories
- Create, prioritize, pause, and manage merchant category rules
- Show monthly totals grouped by category
- Run with SQLite or PostgreSQL
- Demonstrate a measured PostgreSQL index improvement
- Register, log in, log out, and protect each user's data
- Register, log in, reach the dashboard, and log out through React
- Create, search, filter, sort, edit, and delete transactions through React
- Display real monthly totals for the signed-in user
- Check whether the service is running

The project currently provides only the backend—the part that stores information and performs the work. It does not yet have a website for users.

## What we plan to add

- Better input checks and automated testing
- Category and rule management screens
- Monthly category charts and month selection
- A simple dashboard
- CSV imports from bank files
- Category suggestions that improve using user corrections

## How we will build it

The project will be developed in small phases. Each phase must work and pass its tests before the next one begins.

| Phase | Main result | Skills demonstrated |
|---|---|---|
| 1. Foundation | A reliable backend that is easy to run | Python, FastAPI, Git, testing |
| 2. Data and API | Safe storage and complete transaction features | SQL, PostgreSQL, database design, REST APIs |
| 3. Users and security | Private accounts and protected data | Authentication, authorization, security |
| 4. Frontend | A usable dashboard and transaction screens | JavaScript, React, API integration |
| 5. Imports | Bank CSV upload and duplicate checking | Algorithms, file processing, background work |
| 6. Machine learning | Category suggestions that learn from corrections | ML, model evaluation, data handling |
| 7. Delivery | Automated checks and a deployed application | Linux, Bash, Docker, CI/CD, debugging |

See the [phase plan and progress log](docs/phase-plan.md) for implementation and testing details.

Project documentation:

- [Product guide and user stories](docs/product-requirements.md): what users need and when a feature is complete
- [Phase plan and progress log](docs/phase-plan.md): what we will build and test in each phase
- [Architecture guide](docs/architecture.md): how the folders work together and where new code belongs
- [PostgreSQL guide](docs/postgresql.md): how to run and test with the PostgreSQL database
- [Frontend guide](docs/frontend.md): how React state, forms, and API requests work together

## Run the backend

You need Python 3.11 or newer.

1. Create a private project environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install the app and its testing tools:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

3. Start the app:

   First, apply the database changes:

   ```powershell
   python -m alembic upgrade head
   ```

   Then start the server:

   ```powershell
   python -m uvicorn app.main:app --reload
   ```

4. Open `http://127.0.0.1:8000/docs` to try the API in a browser.

Run the automated checks with:

```powershell
python -m pytest
```

The migration command creates or updates the database safely. To change a setting, copy `.env.example` to `.env` and edit the copied file. Never commit `.env` because it may contain private settings.

## Project folders

- `app/api` receives requests and provides shared route helpers.
- `app/services` contains the category rules.
- `app/services` contains the rule-matching logic.
- `app/models` describes how transactions are stored.
- `app/schemas` describes what transaction information is accepted and returned.
- `app/db` connects the app to its database.
- `tests` will contain automated checks.
- `frontend` contains the React and TypeScript website.

## Current status

The backend foundation, database phase, and authentication backend are complete. The React frontend supports registration, login, an authenticated dashboard shell, and logout. Displaying real transaction data is next.
