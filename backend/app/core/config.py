from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str

    API_PREFIX: str

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"


settings = Settings()