from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseCfg
from .log import LogCfg
from .runner import RunnerCfg
from .server import ServerCfg


class AppConfig(BaseSettings):
    runner: RunnerCfg
    db: DatabaseCfg
    log: LogCfg
    server: ServerCfg

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
        env_nested_delimiter="__",
    )


@lru_cache
def cfg() -> AppConfig:
    return AppConfig()  # type: ignore (populated by BaseSettings)


__all__ = ["AppConfig"]
