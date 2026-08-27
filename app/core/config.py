"""Application configuration settings using pydantic-settings."""

from enum import Enum
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataProviderType(str, Enum):
    MOCK = "mock"
    LIVE = "live"
    CANDIDATE = "candidate"


class Settings(BaseSettings):
    APP_NAME: str = "Tross LinkedIn Profile API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "production", "test"] = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Provider abstraction setting: default to 'mock'
    DATA_PROVIDER: DataProviderType = DataProviderType.MOCK

    # Live Provider Credentials (optional, loaded purely via environment variables)
    LINKEDIN_LI_AT: Optional[str] = None
    LINKEDIN_JSESSIONID: Optional[str] = None
    LINKEDIN_BASE_URL: str = "https://www.linkedin.com"
    REQUEST_TIMEOUT_SECONDS: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
