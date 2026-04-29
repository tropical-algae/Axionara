from datetime import datetime
from typing import Union

import pytz
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


def resp_http_error(exc: HTTPException, data: Union[list, dict, str] = "") -> Response:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "message": str(exc.detail),
            "timestamp": str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))),
            "is_exception": True,
            "data": data,
        },
    )


def resp_validation_error(exc: RequestValidationError) -> Response:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": str(exc.errors()),
            "timestamp": str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))),
            "is_exception": True,
            "data": exc.body,
        },
    )


def resp_error() -> Response:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Something is wrong with the server...",
            "timestamp": str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))),
            "is_exception": True,
            "data": "",
        },
    )


def add_exception_handler(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):  # noqa: ARG001
        return resp_http_error(exc=exc)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request, exc):  # noqa: ARG001
        return resp_validation_error(exc=exc)

    @app.exception_handler(Exception)
    async def exception_handler(request, exc):  # noqa: ARG001
        return resp_error()
