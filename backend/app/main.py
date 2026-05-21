from fastapi import FastAPI

from app.core.config import settings
from app.db.session import engine
from app.models.user import Base
from app.api.routes.auth_router import router as auth_router

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