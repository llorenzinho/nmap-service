# TODO: fix pylance hints
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from nmap_service.core.log import get_logger


class RouterLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        self.logger = get_logger("access")
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        if not (
            request.url.path == "/"
            or request.url.path.endswith("/docs")
            or request.url.path.endswith("/redoc")
            or request.url.path.endswith("/openapi.json")
        ):

            duration = time.time() - start_time
            method = request.method
            path = request.url.path
            status_code = response.status_code
            query_params = (
                "&".join(f"{k}={v}" for k, v in request.query_params.items())
                if request.query_params
                else ""
            )
            path = f"{path}?{query_params}" if query_params else path
            log_message = f"Request[method ({method} {path}); status ({status_code}); time ({duration:.2f}s);"
            self.logger.info(log_message)

        return response
