from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):

    APP_NAME: str = Field(...)
    API_PREFIX: str = Field(...)

    DATABASE_URL: str = Field(...)

    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(...)
    JWT_EXPIRE_MINUTES: int = Field(...)

    LEGALIZATIONS_PARQUET: str = Field(...)
    ELECTRONIC_BILLING_PARQUET: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )

settings = Settings()