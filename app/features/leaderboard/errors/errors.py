from enum import Enum

from app.core.errors import AppError


class LeaderboardErrorType(Enum):
    DUPLICATE_RANK = (400, "ERR_DUPLICATE_RANK")

    def __init__(self, status_code: int, error_code: str) -> None:
        self.status_code = status_code
        self.error_code = error_code


class LeaderboardError(AppError):
    def __init__(
        self,
        error_type: LeaderboardErrorType,
        message: str,
        details: dict | None = None,
    ) -> None:
        self.status_code = error_type.status_code
        self.error_code = error_type.error_code
        super().__init__(message, details)
