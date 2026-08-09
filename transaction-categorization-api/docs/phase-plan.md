# Development Phase Plan and Progress Log

This document explains how the project will grow from an early backend into a complete application. It also records progress so readers can see what was planned, built, and tested.

## How to use this log

- `[ ]` means the work has not started.
- `[~]` means the work is in progress.
- `[x]` means the work is complete and tested.

When a phase is completed, add the completion date and a short note about important decisions or problems solved.

## Current starting point

The project can save transactions, apply a few merchant rules, list transactions, and calculate a monthly summary using SQLite. Setup information and meaningful tests are still missing.

---

## Phase 1 — Reliable backend foundation

**Goal:** Make the existing backend easy to install, understand, run, and test.

Implementation:

- [x] List required Python packages and supported Python version.
- [x] Add simple setup and run instructions.
- [x] Create a useful example environment file.
- [x] Check amounts, merchant names, dates, and month values.
- [x] Store money without floating-point rounding errors.
- [x] Return clear and consistent error messages.
- [x] Move database startup work into a safer application startup process.

Testing:

- [x] Test the health check.
- [x] Test creating valid and invalid transactions.
- [x] Test every existing category rule.
- [x] Test date filtering and monthly summaries.
- [x] Test empty results and incorrect inputs.

**Skills shown:** Python, FastAPI, clean code, debugging, requirements, unit testing, API testing, Git.

Completion date: **August 8, 2026**

Notes: Money is stored as an exact decimal rather than an approximate floating-point number. API amounts are returned as strings such as `"8.50"` so their precision is preserved. Tests use a separate temporary database and cannot change real app data. Phase 1 has 15 passing tests.

---

## Phase 2 — Complete data and API features

**Goal:** Give users full control of their transactions and use a production-style database.

Implementation:

- [ ] Move from SQLite to PostgreSQL while keeping SQLite available for simple tests.
- [x] Add database migrations so changes can be applied safely.
- [~] Design tables for transactions, categories, and category rules.
- [x] Add edit and delete operations.
- [x] Add searching, filtering, sorting, and pages.
- [~] Add useful database indexes and explain why they help.
- [ ] Keep grouped spending calculations inside the database.

Testing:

- [x] Test create, read, edit, and delete journeys.
- [x] Test searches, filters, sorting, and page boundaries.
- [x] Test database changes and relationships.
- [ ] Compare an important query before and after adding an index.

**Skills shown:** SQL, PostgreSQL, data modelling, joins, grouping, indexing, transactions, REST API design.

Completion date: _Not started_

Notes: Three migrations are verified on SQLite, with Alembic at revision `20260808_03 (head)`. Transaction and category behavior is covered by 35 passing tests. Categories now have their own table, but configurable merchant rules are still future work. Built-in categories are protected, and categories attached to transactions cannot be deleted. Date and category indexes support common filters; their performance still needs to be measured.

---

## Phase 3 — Accounts and security

**Goal:** Allow multiple users while keeping each person's financial information private.

Implementation:

- [ ] Add registration, login, and logout.
- [ ] Store passwords safely using password hashing.
- [ ] Protect transaction routes.
- [ ] Ensure users can access only their own data.
- [ ] Add request limits and safer handling of secrets.

Testing:

- [ ] Test successful and unsuccessful login attempts.
- [ ] Test access without signing in.
- [ ] Prove that one user cannot read or change another user's data.
- [ ] Test expired or invalid login credentials.

**Skills shown:** authentication, authorization, HTTP, API security, database relationships, privacy.

Completion date: _Not started_

Notes: _Add decisions and lessons here._

---

## Phase 4 — Frontend application

**Goal:** Let people use the product through a clear website rather than direct API requests.

Implementation:

- [ ] Create a React and JavaScript or TypeScript frontend.
- [ ] Build registration and login screens.
- [ ] Build a monthly dashboard with accessible charts.
- [ ] Build a searchable transaction table.
- [ ] Add forms for creating, editing, and deleting transactions.
- [ ] Show clear loading, empty, success, and error messages.
- [ ] Support keyboards and smaller screens.

Testing:

- [ ] Test forms, filters, buttons, and error messages.
- [ ] Test communication between the frontend and backend.
- [ ] Test a full journey from login to viewing a monthly report.
- [ ] Check keyboard use and common screen sizes.

**Skills shown:** JavaScript or TypeScript, React, client-server design, JSON, usability, accessibility, frontend testing.

Completion date: _Not started_

Notes: _Add decisions and lessons here._

---

## Phase 5 — CSV import and background work

**Goal:** Let users import many bank transactions safely and efficiently.

Implementation:

- [ ] Upload and validate CSV files.
- [ ] Let users match bank columns to app fields.
- [ ] Preview valid rows and explain incorrect rows.
- [ ] Detect likely duplicates using a transaction fingerprint.
- [ ] Process large imports in the background.
- [ ] Report progress and final import results.

Testing:

- [ ] Test correct, incorrect, empty, and oversized files.
- [ ] Test different date and amount formats.
- [ ] Test duplicate detection with realistic examples.
- [ ] Test failed jobs and safe retries.
- [ ] Measure import time with larger sample files.

**Skills shown:** file processing, hash-based algorithms, time and space complexity, concurrency, error handling, performance testing.

Completion date: _Not started_

Notes: _Add decisions and lessons here._

---

## Phase 6 — Machine-learning categorization

**Goal:** Improve suggestions using real corrections while keeping users in control.

Implementation:

- [ ] Record the original suggestion and the user's correction.
- [ ] Prepare anonymous training examples without unnecessary personal data.
- [ ] Create a simple text-classification model as a baseline.
- [ ] Return a suggested category and confidence score.
- [ ] Ask users to review uncertain suggestions.
- [ ] Keep simple merchant rules as a reliable fallback.
- [ ] Save model versions so results can be reproduced or rolled back.

Testing:

- [ ] Keep training examples separate from evaluation examples.
- [ ] Measure accuracy, precision, recall, and F1 for each category.
- [ ] Compare the model with the existing rule-based approach.
- [ ] Test unfamiliar merchants and low-confidence results.
- [ ] Confirm the app still works when the model is unavailable.

**Skills shown:** machine learning, text processing, model evaluation, data privacy, versioning, system integration.

Completion date: _Not started_

Notes: _Add decisions, results, and model measurements here._

---

## Phase 7 — Automation, deployment, and monitoring

**Goal:** Run the application consistently and detect problems quickly.

Implementation:

- [ ] Package the frontend, backend, and database with Docker.
- [ ] Add Linux and Bash commands for setup, backup, and maintenance.
- [ ] Run tests automatically through GitHub Actions.
- [ ] Deploy the application using a repeatable process.
- [ ] Add health checks, useful logs, and request IDs.
- [ ] Document common failures and troubleshooting steps.

Testing:

- [ ] Build and run the application from a clean environment.
- [ ] Block changes when automated checks fail.
- [ ] Test database backup and recovery.
- [ ] Test health checks and failure reporting.
- [ ] Run a small performance and security review.

**Skills shown:** Linux, Bash, Docker, GitHub, CI/CD, networking, logging, debugging, system testing.

Completion date: _Not started_

Notes: _Add deployment links, decisions, and lessons here._

---

## Final demonstration

The finished project should let a reviewer follow this journey:

1. Create an account and sign in.
2. Import a bank CSV file.
3. Review automatic categories and correct an uncertain suggestion.
4. Search or edit a transaction.
5. View the updated monthly dashboard.
6. See automated tests and deployment checks pass.
7. Read how database speed and model quality were measured.

This journey provides connected evidence of full-stack development, databases, algorithms, testing, security, machine learning, and software delivery without adding unrelated technology.
