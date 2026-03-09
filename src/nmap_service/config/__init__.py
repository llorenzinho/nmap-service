from pydantic_settings import BaseSettings

from .runner import RunnerCfg


class AppConfig(BaseSettings):
    runner: RunnerCfg


__all__ = ["AppConfig"]
