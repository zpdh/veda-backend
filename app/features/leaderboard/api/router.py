from fastapi import APIRouter, Depends, Path, Request, Security

from app.core.security.auth import verify_auth_token
from app.core.security.rate_limiter import limiter
from app.features.leaderboard.dto.request import CreateSnapshotRequest
from app.features.leaderboard.dto.response import (
    LeaderboardsResponse,
    SnapshotCreatedResponse,
    SnapshotResponse,
)
from app.features.leaderboard.use_cases.create_snapshot import CreateSnapshot
from app.features.leaderboard.use_cases.get_latest_snapshot import GetLatestSnapshot
from app.features.leaderboard.use_cases.get_leaderboard_names import GetLeaderboards
from app.core.constants import API_ROUTE_PREFIX, LIMITER_HTTP_GET, LIMITER_HTTP_POST

leaderboard_router = APIRouter(
    prefix=f"{API_ROUTE_PREFIX}/leaderboards", tags=["leaderboards"]
)


@leaderboard_router.get("")
@limiter.limit(LIMITER_HTTP_GET)
async def get_leaderboards(
    request: Request, use_case: GetLeaderboards = Depends()
) -> LeaderboardsResponse:
    return await use_case.execute()


@leaderboard_router.get("/{leaderboard_name}")
@limiter.limit(LIMITER_HTTP_GET)
async def get_latest_snapshot(
    request: Request,
    leaderboard_name: str,
    use_case: GetLatestSnapshot = Depends(),
) -> SnapshotResponse:
    return await use_case.execute(leaderboard_name)


@leaderboard_router.post(
    "/snapshot", status_code=201, dependencies=[Security(verify_auth_token)]
)
@limiter.limit(LIMITER_HTTP_POST)
async def post_snapshot(
    request: Request, req: CreateSnapshotRequest, use_case: CreateSnapshot = Depends()
) -> SnapshotCreatedResponse:
    return await use_case.execute(req)
