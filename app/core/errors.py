class AppError(Exception):
    status_code: int = 500
    error_code: str = "ERR_INTERNAL"
    message: str
    details: dict | None

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DuplicateRankError(AppError):
    status_code = 400
    error_code = "ERR_DUPLICATE_RANK"
