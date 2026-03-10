from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseCfg
from .log import LogCfg
from .runner import RunnerCfg


class AppConfig(BaseSettings):
    runner: RunnerCfg
    db: DatabaseCfg
    log: LogCfg

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
    )


@lru_cache
def cfg() -> AppConfig:
    return AppConfig()  # type: ignore (populated by BaseSettings)


__all__ = ["AppConfig"]
