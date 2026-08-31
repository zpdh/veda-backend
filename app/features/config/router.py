from fastapi import APIRouter, Depends, Request

from app.core.security.rate_limiter import limiter
from app.features.config.get_config import GetConfig
from app.features.config.response import ConfigResponse
from app.features.leaderboard.api.router import _LIMITER_VALUE_GET

config_router = APIRouter(prefix="/v1/api/config", tags=["configs"])


@config_router.get("/")
@limiter.limit(_LIMITER_VALUE_GET)
async def get_config(
    request: Request, use_case: GetConfig = Depends()
) -> ConfigResponse:
    return await use_case.execute()
