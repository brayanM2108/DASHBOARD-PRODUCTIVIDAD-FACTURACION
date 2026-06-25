from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import logging.handlers
import os
from pathlib import Path

from .core.config import settings
from .db.session import engine, SessionLocal
from .models import Base
from sqlalchemy import text
from .api.routes.auth_router import router as auth_router
from .api.routes.billing_router import router as billing_router
from .api.routes.legalization_router import router as legalization_router
from .api.routes.administrative_process_router import router as administrative_process_router
from .api.routes.rips_router import router as rips_router
from .api.routes.radicacion_router import router as radicacion_router
from .api.routes.home_router import router as home_router
from .api.routes.export_router import router as export_router
from .api.routes.users_router import router as users_router
from .api.routes.admin_router import router as admin_router
from .api.routes.data_router import router as data_router
from .api.routes.billers_admin_router import router as billers_admin_router
from .core.exceptions.base import AppException
from .core.exceptions.handlers import (
    app_exception_handler
)

app = FastAPI(
    title=settings.APP_NAME
)

_LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            _LOG_DIR / "app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/api/health")
def health_check():
    status = {"database": "down", "status": "unhealthy"}

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["database"] = "up"
    except Exception as e:
        status["database_error"] = str(e)
        logger.error("Health check: database unreachable: %s", e)

    status["status"] = "healthy" if status["database"] == "up" else "degraded"
    return status


@app.get("/")
def root():
    return {
        "message": "API funcionando"
    }

app.include_router(
    auth_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    billing_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    legalization_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    administrative_process_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    rips_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    radicacion_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    home_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    export_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    users_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    admin_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    data_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    billers_admin_router,
    prefix=settings.API_PREFIX
)

app.add_exception_handler(
    AppException,
    app_exception_handler
)