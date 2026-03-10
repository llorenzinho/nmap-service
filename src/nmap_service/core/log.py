import logging
from functools import lru_cache
from typing import Any

import pythonjsonlogger.jsonlogger as jsonlogger

from nmap_service.config import cfg
from nmap_service.core.constants import APP_VERSION


class VersionFilter(logging.Filter):
    def filter(self, record: Any) -> bool:
        record.version = APP_VERSION
        return True


@lru_cache()
def get_logger(name: str = __name__) -> logging.Logger:
    cfg_ = cfg()
    logger = logging.getLogger(name)
    logger.setLevel(cfg_.log.level.value)
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(  # type: ignore (actually exported from python-json-logger)
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(version)s"
        )
        console_handler.setFormatter(formatter)
        console_handler.addFilter(VersionFilter())
        logger.addHandler(console_handler)
    logger.propagate = False
    return logger


app_logger = get_logger()
