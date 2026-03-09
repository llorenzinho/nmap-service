from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseCfg
from .runner import RunnerCfg


class AppConfig(BaseSettings):
    runner: RunnerCfg
    db: DatabaseCfg
    
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
    )


@lru_cache
def cfg() -> AppConfig:
    return AppConfig()


__all__ = ["AppConfig"]
