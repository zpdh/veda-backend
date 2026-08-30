from enum import Enum

from app.core.errors import AppError, ErrorDescription


class PlayerErrors(Enum):
    PLAYER_NOT_FOUND = ErrorDescription(404, "ERR_PLAYER_NOT_FOUND")


class PlayerError(AppError):
    def __init__(
        self, error_desc: PlayerErrors, message: str, details: dict | None = None
    ) -> None:
        super().__init__(error_desc.value, message, details)
