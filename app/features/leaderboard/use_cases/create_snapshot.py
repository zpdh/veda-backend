from datetime import UTC, datetime

from fastapi import Depends
from redis.asyncio import Redis

from app.core.db.cache import get_redis
from app.core.db.unit_of_work import UnitOfWork, get_unit_of_work
from app.features.leaderboard.dto.request import (
    CreateSnapshotRequest,
)
from app.features.leaderboard.dto.response import SnapshotCreatedResponse
from app.features.leaderboard.entities.orm import LeaderboardEntry, LeaderboardSnapshot
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)
from app.features.player.repositories.postgres import (
    PlayerRepository,
    get_player_repository,
)


class CreateSnapshot:
    _unit_of_work: UnitOfWork
    _lb_repo: LeaderboardRepository

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_unit_of_work),
        redis: Redis = Depends(get_redis),
        lb_repo: LeaderboardRepository = Depends(get_leaderboard_repository),
        player_repo: PlayerRepository = Depends(get_player_repository),
    ) -> None:
        self._unit_of_work = uow
        self._redis = redis
        self._lb_repo = lb_repo
        self._player_repo = player_repo

    async def execute(self, req: CreateSnapshotRequest) -> SnapshotCreatedResponse:
        snapshot_ids: list[int] = []
        fetched_at = datetime.now(UTC)

        for snapshot_in in req.snapshots:
            lb = await self._lb_repo.upsert_leaderboard(snapshot_in.leaderboard_name)
            snapshot_entity = LeaderboardSnapshot(
                leaderboard_id=lb.id,
                fetched_at=fetched_at,
                entries=[
                    LeaderboardEntry(
                        rank=entry_in.rank,
                        player_name=entry_in.player_name,
                        value=entry_in.value,
                    )
                    for entry_in in snapshot_in.entries
                ],
            )
            created_snapshot: LeaderboardSnapshot = await self._lb_repo.create_snapshot(
                snapshot_entity
            )
            snapshot_ids.append(created_snapshot.id)

        unique_names = {
            entry.player_name
            for snapshot_in in req.snapshots
            for entry in snapshot_in.entries
        }

        for player_name in unique_names:
            _ = await self._player_repo.upsert_player(player_name)

        await self._unit_of_work.commit()

        for player_name in unique_names:
            _ = await self._redis.delete(f"player:{player_name.lower()}")

        return SnapshotCreatedResponse(
            snapshotIds=snapshot_ids,
            fetchedAt=fetched_at,
            message="Snapshots created successfully.",
        )
