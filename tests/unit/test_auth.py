import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.errors import AppError
from app.core.security.auth import verify_auth_token


class TestAuthSecurity:
    async def test_verify_auth_token_success(self):
        valid_creds = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=settings.shared_secret
        )
        # Should not raise
        await verify_auth_token(credentials=valid_creds)

    async def test_verify_auth_token_invalid_secret_raises_unauthorized(self):
        invalid_creds = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="wrong-secret"
        )
        with pytest.raises(AppError) as exc_info:
            await verify_auth_token(credentials=invalid_creds)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "ERR_UNAUTHORIZED"

    async def test_verify_auth_token_empty_secret_raises_unauthorized(self):
        empty_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        with pytest.raises(AppError) as exc_info:
            await verify_auth_token(credentials=empty_creds)

        assert exc_info.value.status_code == 401
        assert exc_info.value.error_code == "ERR_UNAUTHORIZED"
