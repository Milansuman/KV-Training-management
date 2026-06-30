from fastapi import FastAPI

from middleware.logger import RequestLoggingMiddleware


def configure_middleware(app: FastAPI) -> None:

    app.add_middleware(
        RequestLoggingMiddleware
    )