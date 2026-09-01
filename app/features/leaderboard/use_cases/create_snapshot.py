from datetime import UTC, datetime

from fastapi import Depends
from redis.asyncio import Redis

from app.core.db.cache import get_redis
from app.core.db.unit_of_work import UnitOfWork, get_unit_of_work
from app.features.leaderboard.dto.request import (
    CreateSnapshotRequest,
    LeaderboardSnapshotIn,
)
from app.features.leaderboard.dto.response import SnapshotCreatedResponse
from app.features.leaderboard.entities.orm import LeaderboardEntry, LeaderboardSnapshot
from app.features.leaderboard.errors.errors import LeaderboardError, LeaderboardErrors
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)
from app.features.player.repositories.postgres import (
    PlayerRepository,
    get_player_repository,
)


class CreateSnapshot:
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_unit_of_work),
        redis: Redis = Depends(get_redis),
        lb_repo: LeaderboardRepository = Depends(get_leaderboard_repository),
        player_repo: PlayerRepository = Depends(get_player_repository),
    ) -> None:
        self._unit_of_work: UnitOfWork = uow
        self._redis: Redis = redis
        self._lb_repo: LeaderboardRepository = lb_repo
        self._player_repo: PlayerRepository = player_repo

    async def execute(self, req: CreateSnapshotRequest) -> SnapshotCreatedResponse:
        created_snapshot_ids: list[int] = []
        fetched_at = datetime.now(UTC)
        unique_names: set[str] = set()

        for snapshot_in in req.snapshots:
            created_snapshot = await self._create_snapshot(snapshot_in, fetched_at)
            created_snapshot_ids.append(created_snapshot.id)

            created_players = await self._upsert_players(created_snapshot)
            unique_names.update(created_players)

        await self._unit_of_work.commit()

        for name in unique_names:
            _ = await self._redis.delete(f"player:{name.lower()}")

        return SnapshotCreatedResponse(
            snapshotIds=created_snapshot_ids,
            fetchedAt=fetched_at,
            message="Snapshots created successfully.",
        )

    async def _create_snapshot(
        self,
        snapshot_req: LeaderboardSnapshotIn,
        fetched_at: datetime,
    ) -> LeaderboardSnapshot:
        lb_name = snapshot_req.leaderboard_name
        lb = await self._lb_repo.get_leaderboard_by_name(lb_name)
        if lb is None:
            raise LeaderboardError(
                LeaderboardErrors.LEADERBOARD_NOT_FOUND,
                f"Leaderboard {lb_name} does not exist.",
                {"leaderboardName": lb_name},
            )

        snapshot_entity = LeaderboardSnapshot(
            leaderboard_id=lb.id,
            fetched_at=fetched_at,
            entries=[
                LeaderboardEntry(
                    rank=entry_in.rank,
                    player_name=entry_in.player_name,
                    value=entry_in.value,
                )
                for entry_in in snapshot_req.entries
            ],
        )
        created_snapshot: LeaderboardSnapshot = await self._lb_repo.create_snapshot(
            snapshot_entity
        )

        return created_snapshot

    async def _upsert_players(self, snapshot: LeaderboardSnapshot) -> set[str]:
        unique_names = set(entry.player_name for entry in snapshot.entries)

        for name in unique_names:
            _ = await self._player_repo.upsert_player(name)

        return unique_names
