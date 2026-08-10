from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ErrorDescription:
    status_code: int
    error_code: str


class CommonErrors(Enum):
    INTERNAL_SERVER_ERROR = ErrorDescription(500, "ERR_INTERNAL")


class AppError(Exception):
    status_code: int
    error_code: str
    message: str
    details: dict | None

    def __init__(
        self, error_desc: ErrorDescription, message: str, details: dict | None = None
    ) -> None:
        self.status_code = error_desc.status_code
        self.error_code = error_desc.error_code
        self.message = message
        self.details = details

        super().__init__(message)
