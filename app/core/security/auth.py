import secrets

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.errors import AppError, CommonErrors

bearer_scheme = HTTPBearer()


async def verify_auth_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> None:
    if secrets.compare_digest(credentials.credentials, settings.shared_secret):
        raise AppError(CommonErrors.UNAUTHORIZED.value, "Unauthorized")
