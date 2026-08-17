from fastapi import APIRouter, Depends, Security

from app.core.security.auth import verify_auth_token
from app.features.leaderboard.dto.request import CreateSnapshotRequest
from app.features.leaderboard.dto.response import (
    SnapshotCreatedResponse,
    SnapshotResponse,
)
from app.features.leaderboard.use_cases.create_snapshot import CreateSnapshot
from app.features.leaderboard.use_cases.get_latest_snapshot import GetLatestSnapshot

leaderboard_router = APIRouter(prefix="/v1/api/leaderboards", tags=["leaderboards"])


@leaderboard_router.get("/{leaderboard_name}")
async def get_latest_snapshot(
    leaderboard_name: str, use_case: GetLatestSnapshot = Depends()
) -> SnapshotResponse:
    return await use_case.execute(leaderboard_name)


@leaderboard_router.post(
    "/snapshot", status_code=201, dependencies=[Security(verify_auth_token)]
)
async def post_snapshot(
    req: CreateSnapshotRequest, use_case: CreateSnapshot = Depends()
) -> SnapshotCreatedResponse:
    return await use_case.execute(req)
