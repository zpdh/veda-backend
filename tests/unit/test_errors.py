import json
from unittest.mock import MagicMock

from app.core.errors import (
    AppError,
    CommonErrors,
    ErrorDescription,
    app_error_handler,
    error_handler,
    rate_limit_handler,
)


class TestErrorHandlers:
    async def test_app_error_handler(self):
        req = MagicMock()
        exc = AppError(
            ErrorDescription(404, "ERR_NOT_FOUND"),
            "Item not found",
            {"itemId": 42},
        )
        response = await app_error_handler(req, exc)
        assert response.status_code == 404
        data = json.loads(response.body.decode("utf-8"))
        assert data["errorCode"] == "ERR_NOT_FOUND"
        assert data["message"] == "Item not found"
        assert data["details"] == {"itemId": 42}

    async def test_rate_limit_handler(self):
        req = MagicMock()
        exc = Exception("rate limit exceeded")
        response = await rate_limit_handler(req, exc)
        assert response.status_code == 429
        data = json.loads(response.body.decode("utf-8"))
        assert data["errorCode"] == CommonErrors.RATE_LIMIT.value.error_code
        assert data["message"] == "Rate limit exceeded."

    async def test_unhandled_error_handler_masks_internals(self):
        req = MagicMock()
        exc = RuntimeError("Database connection string postgres://secret:pwd@db leaked")
        response = await error_handler(req, exc)
        assert response.status_code == 500
        data = json.loads(response.body.decode("utf-8"))
        assert data["errorCode"] == CommonErrors.INTERNAL_SERVER_ERROR.value.error_code
        assert data["message"] == "Internal Server Error."
        # Verify internal secret is never leaked
        assert "secret" not in json.dumps(data)
