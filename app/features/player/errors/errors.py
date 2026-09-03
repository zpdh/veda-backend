from enum import Enum

from app.core.errors import AppError, ErrorDescription


class PlayerErrors(Enum):
    PLAYER_NOT_FOUND = ErrorDescription(404, "ERR_PLAYER_NOT_FOUND")
    ACHIEVEMENTS_UNAVAILABLE = ErrorDescription(502, "ERR_ACHIEVEMENTS_UNAVAILABLE")


class PlayerError(AppError):
    def __init__(
        self,
        error_desc: PlayerErrors,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(error_desc.value, message, details)
