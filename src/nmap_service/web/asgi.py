import logging.config
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from nmap_service.config.app import cfg
from nmap_service.core import constants
from nmap_service.database.engine import init_db
from nmap_service.web.middlewares.logging import RouterLoggingMiddleware
from .router import router

logging.config.dictConfig(cfg().log.uvicorn_log_config())


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    root_logger = logging.getLogger("root")
    root_logger.debug("APP STARTING")
    root_logger.debug(f"{'Service Version:'.ljust(18)} {constants.APP_VERSION}")
    init_db()
    yield
    root_logger.debug("APP STOPPED")


app = FastAPI(
    title=constants.APP_NAME,
    version=constants.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(RouterLoggingMiddleware)


@app.get("/healthz", status_code=status.HTTP_204_NO_CONTENT)
def health_check():
    return None


app.include_router(router, prefix="/api/v1")
