import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:

        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            duration_ms = round((time.perf_counter() - start_time) * 1000)

            client_ip = (request.client.host if request.client else "-")

            logger.info(
                "%s %s %s %s %dms",
                client_ip,
                request.method,
                request.url.path,
                response.status_code,
                duration_ms
            )

            return response

        except Exception:

            duration_ms = round(
                (time.perf_counter() - start_time) * 1000
            )

            client_ip = (
                request.client.host
                if request.client
                else "-"
            )

            logger.exception(
                "%s %s %s FAILED %dms",
                client_ip,
                request.method,
                request.url.path,
                duration_ms
            )

            raise