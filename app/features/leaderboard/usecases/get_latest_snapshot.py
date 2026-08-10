from fastapi import Depends

from app.features.leaderboard.dto.response import EntryOut, SnapshotResponse
from app.features.leaderboard.errors.errors import LeaderboardError, LeaderboardErrors
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)


class GetLatestSnapshot:
    _lb_repo: LeaderboardRepository

    def __init__(
        self,
        lb_repo: LeaderboardRepository = Depends(get_leaderboard_repository),  # noqa: B008
    ) -> None:
        self._lb_repo = lb_repo

    async def execute(self, leaderboard_name: str) -> SnapshotResponse:
        leaderboard = await self._lb_repo.get_leaderboard_by_name(leaderboard_name)

        if leaderboard is None:
            raise LeaderboardError(
                LeaderboardErrors.LEADERBOARD_NOT_FOUND,
                "Leaderboard not found.",
                {"leaderboardName": leaderboard_name},
            )

        snapshot = await self._lb_repo.get_latest_snapshot(leaderboard.id)

        if snapshot is None:
            raise LeaderboardError(
                LeaderboardErrors.SNAPSHOT_NOT_FOUND,
                f"Snapshot not found for the leaderboard '{leaderboard_name}'.",
                {"leaderboardName": leaderboard_name},
            )

        return SnapshotResponse(
            snapshotId=snapshot.id,
            leaderboardName=leaderboard.name,
            fetchedAt=snapshot.fetched_at,
            entries=[
                EntryOut(
                    entryId=entry.id,
                    rank=entry.rank,
                    playerName=entry.player_name,
                    value=entry.value,
                )
                for entry in snapshot.entries
            ],
        )
