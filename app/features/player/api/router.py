from fastapi import APIRouter, Depends, Request

from app.core.constants import LIMITER_HTTP_GET
from app.core.security.rate_limiter import limiter
from app.features.player.dto.response import PlayerResponse
from app.features.player.use_cases.get_player import GetPlayer


player_router = APIRouter(prefix="/api/v1/players", tags=["players"])


@player_router.get("/{player_name}")
@limiter.limit(LIMITER_HTTP_GET)
async def get_player(
    request: Request, player_name: str, use_case: GetPlayer = Depends()
) -> PlayerResponse:
    return await use_case.execute(player_name)
