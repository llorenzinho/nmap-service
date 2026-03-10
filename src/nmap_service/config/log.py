from typing import Any

from pydantic import BaseModel

from nmap_service.core.enums import LogLevel


class LogCfg(BaseModel):
    level: LogLevel = LogLevel.INFO
    format: str = "[%(asctime)s] [%(levelname)s] [%(name)s] | %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"

    def uvicorn_log_config(self) -> dict[str, Any]:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.format,
                    "datefmt": self.datefmt,
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "handlers": ["default"],
                "level": self.level.value,
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default"],
                    "level": self.level.value,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": LogLevel.WARNING.value,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": [],
                    "level": self.level.value,
                    "propagate": False,
                },
            },
        }
