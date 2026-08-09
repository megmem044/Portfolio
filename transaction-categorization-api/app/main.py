from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.transactions import router as transactions_router
from app.db.base import Base
from app.db.session import engine

def create_app(create_tables: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if create_tables:
            Base.metadata.create_all(bind=engine)
        yield

    application = FastAPI(
        title="Transaction Categorization API",
        description="Backend service for categorizing and summarizing financial transactions",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(health_router)
    application.include_router(transactions_router)

    @application.get("/")
    def root():
        return {"status": "ok"}

    return application


app = create_app()
