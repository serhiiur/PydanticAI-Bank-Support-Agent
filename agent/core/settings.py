from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# load environment variables from the .env file.
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database settings."""

    model_config = SettingsConfigDict(env_prefix="DB_")

    url: str = "sqlite+aiosqlite:///./bank.db"


class CurrencyAPISettings(BaseSettings):
    """Settings for the currency exchange rate API."""

    model_config = SettingsConfigDict(env_prefix="CURRENCY_")
    api_url: HttpUrl = HttpUrl("http://www.example.com")


class Settings(BaseSettings):
    """General project settings."""

    # General settings
    debug: bool = False

    # Database settings
    database: DatabaseSettings = DatabaseSettings()

    # Currency API settings
    currency: CurrencyAPISettings = CurrencyAPISettings()

    # Agent settings
    agent_spec_filepath: Path = Path(__file__).parents[2] / "agent.yml"


@lru_cache
def get_settings() -> Settings:
    """Cache and return project settings."""
    return Settings()


settings = Settings()
