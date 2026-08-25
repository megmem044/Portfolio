"""Create the FastAPI application and connect all API route groups."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.categories import router as categories_router
from app.api.routes.category_rules import router as category_rules_router
from app.api.routes.health import router as health_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.transaction_imports import router as transaction_imports_router
from app.core.config import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title="Transaction Categorization API",
        description="Backend service for categorizing and summarizing financial transactions",
        version="0.1.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(auth_router)
    application.include_router(analytics_router)
    application.include_router(categories_router)
    application.include_router(category_rules_router)
    application.include_router(health_router)
    application.include_router(transactions_router)
    application.include_router(transaction_imports_router)

    @application.get("/")
    def root():
        return {"status": "ok"}

    return application


app = create_app()
