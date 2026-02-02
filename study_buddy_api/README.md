## Study Buddy API

A RESTful backend API for managing study topics, flashcards, and quiz sessions.
Built with FastAPI, SQLAlchemy, and SQLite, with automatic OpenAPI documentation.

## Features

## Topics
Create and list study topics
Enforces unique topic names
Proper HTTP status handling (201, 409, 404)

## Flashcards
Create flashcards linked to topics
List all flashcards or flashcards scoped to a topic

## Quiz Mode
Retrieve randomized flashcards for a topic
Configurable quiz size with validation
Graceful handling of empty topics

## API Documentation
Auto-generated Swagger UI via FastAPI
Fully typed request and response schemas

## Tech Stack
Python 3.14
FastAPI
SQLAlchemy ORM
SQLite
Uvicorn
Pydantic

## Project Structure
study_buddy_api/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── deps.py
│   ├── models/
│   │   ├── topic.py
│   │   └── flashcard.py
│   ├── schemas/
│   │   ├── topic.py
│   │   └── flashcard.py
│   └── routers/
│       ├── topic.py
│       ├── flashcard.py
│       └── quiz.py
├── scripts/
│   └── init_db.py
├── study_buddy.db
└── README.md

## Running the Project Locally
1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

2. Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic-settings

3. Initialize the database
python -m scripts.init_db

4. Start the server
python -m uvicorn app.main:app

5. Open API documentation
http://127.0.0.1:8000/docs

## Example Endpoints
## Create a Topic
POST /topics

{
  "name": "Biology"
}

## Create a Flashcard
POST /flashcards

{
  "topic_id": 1,
  "front": "What does DNA stand for?",
  "back": "Deoxyribonucleic acid"
}

## Quiz a Topic
GET /topics/1/quiz?count=2

## Design Highlights
Dependency-injected database sessions per request
Explicit data validation using Pydantic schemas
Relational integrity enforced at both application and database levels
Randomized quiz logic with bounds checking
Clear separation of concerns between routers, schemas, and models

## Future Improvements
Authentication for write endpoints
Pagination and filtering
Automated tests with pytest
Persistent user quiz attempts and scoring