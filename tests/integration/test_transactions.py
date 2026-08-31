from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis

from app.core.db.unit_of_work import UnitOfWork
from app.features.leaderboard.dto.request import (
    CreateSnapshotRequest,
    EntryIn,
    LeaderboardSnapshotIn,
)
from app.features.leaderboard.entities.orm import Leaderboard, LeaderboardSnapshot
from app.features.leaderboard.repositories.postgres import LeaderboardRepository
from app.features.leaderboard.use_cases.create_snapshot import CreateSnapshot
from app.features.player.entities.orm import Player
from app.features.player.repositories.postgres import PlayerRepository


class TestBatchAtomicity:
    async def test_batch_snapshot_atomic_rollback_on_failure(self):
        uow = AsyncMock(spec=UnitOfWork)
        redis = AsyncMock(spec=Redis)
        lb_repo = AsyncMock(spec=LeaderboardRepository)
        player_repo = AsyncMock(spec=PlayerRepository)
        now = datetime.now(UTC)

        lb1 = Leaderboard(id=1, name="Global", created_at=now, updated_at=now)
        snap1 = LeaderboardSnapshot(
            id=10, leaderboard_id=1, fetched_at=now, entries=[]
        )
        player = Player(id=1, name="Alice")

        lb_repo.upsert_leaderboard.side_effect = [
            lb1,
            RuntimeError("DB error during 2nd leaderboard"),
        ]
        lb_repo.create_snapshot.side_effect = [snap1]
        player_repo.upsert_player.return_value = player

        use_case = CreateSnapshot(
            uow=uow, redis=redis, lb_repo=lb_repo, player_repo=player_repo
        )
        req = CreateSnapshotRequest(
            snapshots=[
                LeaderboardSnapshotIn(
                    leaderboardName="Global",
                    entries=[EntryIn(rank=1, playerName="Alice", value=10)],
                ),
                LeaderboardSnapshotIn(
                    leaderboardName="Weekly",
                    entries=[EntryIn(rank=1, playerName="Bob", value=20)],
                ),
            ]
        )

        with pytest.raises(RuntimeError, match="DB error during 2nd leaderboard"):
            await use_case.execute(req)

        # Confirm commit was never called
        uow.commit.assert_not_awaited()
