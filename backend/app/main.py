from fastapi import FastAPI

from .core.config import settings
from .db.session import engine
from .models.user import Base
from .api.routes.auth_router import router as auth_router
from .api.routes.billing_router import router as billing_router
from .api.routes.legalization_router import router as legalization_router
from app.core.exceptions.base import AppException
from app.core.exceptions.handlers import (
    app_exception_handler
)

app = FastAPI(
    title=settings.APP_NAME
)

Base.metadata.create_all(bind=engine)

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

app.add_exception_handler(
    AppException,
    app_exception_handler
)