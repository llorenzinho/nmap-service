from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseCfg
from .log import LogCfg
from .runner import NmapCfg
from .scan_strategy import StrategyCfg
from .server import ServerCfg


class AppConfig(BaseSettings):
    runner: NmapCfg
    db: DatabaseCfg
    log: LogCfg
    server: ServerCfg
    scan_strategy: StrategyCfg

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
        env_nested_delimiter="__",
    )


@lru_cache
def cfg() -> AppConfig:
    return AppConfig()  # type: ignore


ConfigDep = Annotated[AppConfig, Depends(cfg)]
