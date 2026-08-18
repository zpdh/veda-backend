from fastapi import APIRouter, Depends, Request, Security

from app.core.security.auth import verify_auth_token
from app.core.security.rate_limiter import limiter
from app.features.leaderboard.dto.request import CreateSnapshotRequest
from app.features.leaderboard.dto.response import (
    SnapshotCreatedResponse,
    SnapshotResponse,
)
from app.features.leaderboard.use_cases.create_snapshot import CreateSnapshot
from app.features.leaderboard.use_cases.get_latest_snapshot import GetLatestSnapshot

leaderboard_router = APIRouter(prefix="/v1/api/leaderboards", tags=["leaderboards"])


@leaderboard_router.get("/{leaderboard_name}")
@limiter.limit(limit_value="60/minute")
async def get_latest_snapshot(
    request: Request,
    leaderboard_name: str, use_case: GetLatestSnapshot = Depends()
) -> SnapshotResponse:
    return await use_case.execute(leaderboard_name)


@leaderboard_router.post(
    "/snapshot", status_code=201, dependencies=[Security(verify_auth_token)]
)
@limiter.limit(limit_value="5/minute")
async def post_snapshot(
    request: Request,
    req: CreateSnapshotRequest, use_case: CreateSnapshot = Depends()
) -> SnapshotCreatedResponse:
    return await use_case.execute(req)
