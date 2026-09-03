from dataclasses import dataclass
from enum import Enum
from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.dto import ErrorResponse


@dataclass(frozen=True)
class ErrorDescription:
    status_code: int
    error_code: str


class CommonErrors(Enum):
    INTERNAL_SERVER_ERROR = ErrorDescription(500, "ERR_INTERNAL")
    UNAUTHORIZED = ErrorDescription(401, "ERR_UNAUTHORIZED")
    RATE_LIMIT = ErrorDescription(429, "ERR_RATE_LIMITED")


class AppError(Exception):
    status_code: int
    error_code: str
    message: str
    details: dict[str, object] | None

    def __init__(
        self,
        error_desc: ErrorDescription,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        self.status_code = error_desc.status_code
        self.error_code = error_desc.error_code
        self.message = message
        self.details = details

        super().__init__(message)


async def app_error_handler(req: Request, exc: Exception) -> JSONResponse:  # pyright: ignore[reportUnusedParameter]
    exc = cast(AppError, exc)
    res = ErrorResponse(
        errorCode=exc.error_code, message=exc.message, details=exc.details
    )

    return JSONResponse(
        status_code=exc.status_code, content=res.model_dump(mode="json")
    )


async def rate_limit_handler(req: Request, exc: Exception) -> JSONResponse:
    err_desc: ErrorDescription = CommonErrors.RATE_LIMIT.value
    res = ErrorResponse(errorCode=err_desc.error_code, message="Rate limit exceeded.")

    return JSONResponse(
        status_code=err_desc.status_code, content=res.model_dump(mode="json")
    )


async def error_handler(req: Request, exc: Exception) -> JSONResponse:  # pyright: ignore[reportUnusedParameter]
    err_desc: ErrorDescription = CommonErrors.INTERNAL_SERVER_ERROR.value
    res = ErrorResponse(errorCode=err_desc.error_code, message="Internal Server Error.")

    return JSONResponse(
        status_code=err_desc.status_code, content=res.model_dump(mode="json")
    )
