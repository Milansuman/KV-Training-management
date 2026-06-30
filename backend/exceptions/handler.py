import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from exceptions.exceptions import AppException

logger = logging.getLogger(__name__)


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    logger.warning(
        "Application exception: %s",
        exc.detail
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        "HTTP exception: %s",
        exc.detail
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "Validation error: %s",
        exc.errors()
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
