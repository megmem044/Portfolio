# app/main.py

from fastapi import FastAPI

from app.routers.flashcard import router as flashcard_router
from app.routers.topic import router as topic_router
from app.routers.quiz import router as quiz_router



# A FastAPI application object is created here.
app = FastAPI(
    title="Study Buddy API",
    version="0.1.0",
    description="A small API for topics, flashcards, and quiz attempts.",
)


# Routers are registered here AFTER app is created.
app.include_router(topic_router)
app.include_router(flashcard_router)
app.include_router(quiz_router)



# A basic health check route is defined here.
@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
