from fastapi import FastAPI

from .core.config import settings
from .db.session import engine
from .models import Base
from .api.routes.auth_router import router as auth_router
from .api.routes.billing_router import router as billing_router
from .api.routes.legalization_router import router as legalization_router
from .api.routes.administrative_process_router import router as administrative_process_router
from .api.routes.rips_router import router as rips_router
from .core.exceptions.base import AppException
from .core.exceptions.handlers import (
    app_exception_handler
)

app = FastAPI(
    title=settings.APP_NAME
)

def startup():
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

app.include_router(
    administrative_process_router,
    prefix=settings.API_PREFIX
)

app.include_router(
    rips_router,
    prefix=settings.API_PREFIX
)

app.add_exception_handler(
    AppException,
    app_exception_handler
)