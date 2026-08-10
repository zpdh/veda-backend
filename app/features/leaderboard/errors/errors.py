from enum import Enum

from app.core.errors import AppError, ErrorDescription


class LeaderboardErrors(Enum):
    DUPLICATE_RANK = ErrorDescription(400, "ERR_DUPLICATE_RANK")


class LeaderboardError(AppError):
    def __init__(
        self, error_desc: LeaderboardErrors, message: str, details: dict | None = None
    ) -> None:
        super().__init__(error_desc.value, message, details)
