from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SATELLITE_TOKEN: str
    PLATFORM_URL: AnyHttpUrl = "https://dev-api.dataforce.studio"
    BASE_URL: str = "http://localhost"
    MODEL_IMAGE: str = "df-random-svc:latest"
    POLL_INTERVAL_SEC: float = 2.0
    CONTAINER_PORT: int = 8080
    CONDA_PORT: int = 8081
    AUTH_PORT: int = 7000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_config() -> Settings:
    return Settings()


config = get_config()
