from datetime import UTC, datetime

from fastapi import Depends

from app.core.db import UnitOfWork, get_unit_of_work
from app.features.leaderboard.dto.request import (
    CreateSnapshotRequest,
    LeaderboardSnapshotIn,
)
from app.features.leaderboard.dto.response import SnapshotCreatedResponse
from app.features.leaderboard.entities.orm import LeaderboardEntry, LeaderboardSnapshot
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)


class CreateSnapshot:
    _unit_of_work: UnitOfWork
    _lb_repo: LeaderboardRepository

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_unit_of_work),  # noqa: B008
        lb_repo: LeaderboardRepository = Depends(get_leaderboard_repository),  # noqa: B008
    ) -> None:
        self._unit_of_work = uow
        self._lb_repo = lb_repo

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

        await self._unit_of_work.commit()
        return SnapshotCreatedResponse(
            snapshotIds=snapshot_ids,
            fetchedAt=fetched_at,
            message="Snapshots created successfully.",
        )
