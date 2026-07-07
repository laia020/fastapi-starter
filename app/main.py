from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes import auth_routes, document_routes
from app.core.config import get_settings
from app.db.database import SessionLocal
from app.models import document_model, user_model


_ = (document_model, user_model)


@asynccontextmanager
async def lifespan(api: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    api = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    @api.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        current_settings = get_settings()
        return {
            "status": "healthy",
            "app": current_settings.app_name,
            "version": current_settings.app_version,
        }

    @api.get("/health/db", tags=["health"])
    async def database_health_check() -> dict[str, str]:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

        return {"status": "healthy", "database": "connected"}

    api.include_router(auth_routes.router)
    api.include_router(document_routes.router)

    return api


app = create_app()
