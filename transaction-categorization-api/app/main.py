from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.transactions import router as transactions_router
from app.db.base import Base
from app.db.session import engine

# FastAPI application instance is created
app = FastAPI(
    title="Transaction Categorization API",
    description="Backend service for categorizing and summarizing financial transactions",
    version="0.1.0"
)

# Database tables are created if they do not already exist
Base.metadata.create_all(bind=engine)

# Health routes are registered
app.include_router(health_router)

# Transaction routes are registered
app.include_router(transactions_router)


# Root endpoint is defined
@app.get("/")
def root():
    # Basic status response is returned
    return {"status": "ok"}
