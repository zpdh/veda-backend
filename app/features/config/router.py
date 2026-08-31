from fastapi import APIRouter, Depends, Request

from app.core.constants import API_ROUTE_PREFIX, LIMITER_HTTP_GET
from app.core.security.rate_limiter import limiter
from app.features.config.get_config import GetConfig
from app.features.config.response import ConfigResponse

config_router = APIRouter(prefix=f"{API_ROUTE_PREFIX}/config", tags=["config"])


@config_router.get("/")
@limiter.limit(LIMITER_HTTP_GET)
async def get_config(
    request: Request, use_case: GetConfig = Depends()
) -> ConfigResponse:
    return await use_case.execute()
