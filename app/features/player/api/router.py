from fastapi import APIRouter, Depends, Path, Request

from app.core.constants import API_ROUTE_PREFIX, LIMITER_HTTP_GET
from app.core.security.rate_limiter import limiter
from app.features.player.dto.response import PlayerResponse
from app.features.player.use_cases.get_player import GetPlayer


player_router = APIRouter(prefix=f"{API_ROUTE_PREFIX}/players", tags=["players"])


@player_router.get("/{player_name}")
@limiter.limit(LIMITER_HTTP_GET)
async def get_player(
    request: Request,
    player_name: str = Path(
        ..., min_length=1, max_length=16, pattern=r"^[a-zA-Z0-9_]+$"
    ),  # regex reads out as any alphanum string
    use_case: GetPlayer = Depends(),
) -> PlayerResponse:
    return await use_case.execute(player_name)
