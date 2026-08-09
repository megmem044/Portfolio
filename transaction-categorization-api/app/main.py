from fastapi import FastAPI

from app.api.routes.categories import router as categories_router
from app.api.routes.health import router as health_router
from app.api.routes.transactions import router as transactions_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Transaction Categorization API",
        description="Backend service for categorizing and summarizing financial transactions",
        version="0.1.0",
    )
    application.include_router(categories_router)
    application.include_router(health_router)
    application.include_router(transactions_router)

    @application.get("/")
    def root():
        return {"status": "ok"}

    return application


app = create_app()
