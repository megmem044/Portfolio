# Transaction Categorization API

A lightweight backend service for ingesting, categorizing, storing, and summarizing financial transactions.  
The API exposes RESTful endpoints to create transactions, list them with optional filtering, and generate monthly summaries similar to basic accounting workflows.

This project is designed as a small, production style backend system demonstrating clean architecture, database modeling, and performance aware API design.

---

## Features

- Create financial transactions via a REST API
- Automatic transaction categorization using deterministic rule based logic
- Persistent storage using a relational database
- List transactions with optional date range filtering
- Monthly summary endpoint with category level aggregation
- Database level aggregation using SQL GROUP BY via SQLAlchemy
- Interactive API documentation via Swagger UI

---

## Tech Stack

- **Language:** Python  
- **Web Framework:** FastAPI  
- **Database:** SQLite  
- **ORM:** SQLAlchemy  
- **Data Validation:** Pydantic  
- **ASGI Server:** Uvicorn  

---

## Architecture Overview

The application follows a layered architecture to separate responsibilities and keep the codebase extensible.

- The API layer handles HTTP routing and request validation
- The schema layer defines request and response data shapes
- The service layer contains business logic such as transaction categorization
- The model layer defines database tables using SQLAlchemy ORM
- The database layer manages engine and session lifecycle
- The core layer centralizes configuration and environment handling

This separation ensures that business logic, persistence, and transport concerns remain independent.

---

## Project Structure

transaction-categorization-api/
│
├── app/
│ ├── main.py
│ ├── core/
│ ├── db/
│ ├── models/
│ ├── schemas/
│ ├── services/
│ └── api/
│
├── tests/
├── pyproject.toml
├── .env.example
└── README.md

---

## API Endpoints

### Create Transaction

POST /transactions


Creates a new transaction and applies automatic categorization based on merchant name.

---

### List Transactions

GET /transactions


Optional query parameters:

- `start` – filter by start date
- `end` – filter by end date

---

### Monthly Summary

GET /transactions/summary?month=YYYY-MM


Returns a monthly financial summary including:

- Total number of transactions
- Overall total amount
- Totals grouped by category

#### Aggregation Strategy

Monthly summaries are computed at the database level using SQL aggregation functions through SQLAlchemy.

- Aggregation uses SQL `GROUP BY` on transaction categories
- Totals are computed directly in the database
- This avoids loading all transactions into application memory
- This approach improves performance and scalability as data volume grows

---

### Health Check

GET /health


Used to verify application availability.

---

## Running the Application

Start the server using:


python -m uvicorn app.main:app
Swagger UI will be available at:

http://127.0.0.1:8000/docs

### Design Goals

Clear separation of concerns

Predictable and deterministic business logic

Database as the source of truth

Performance aware data aggregation

Clean and extensible project structure

### Future Enhancements

Pagination for transaction listing

Update and delete transaction endpoints

Expanded automated test coverage

Containerized deployment

