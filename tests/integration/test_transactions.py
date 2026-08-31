from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.db.unit_of_work import UnitOfWork
from app.features.leaderboard.dto.request import (
    CreateSnapshotRequest,
    EntryIn,
    LeaderboardSnapshotIn,
)
from app.features.leaderboard.entities.orm import Leaderboard, LeaderboardSnapshot
from app.features.leaderboard.repositories.postgres import LeaderboardRepository
from app.features.leaderboard.use_cases.create_snapshot import CreateSnapshot


class TestBatchAtomicity:
    async def test_batch_snapshot_atomic_rollback_on_failure(self):
        uow = AsyncMock(spec=UnitOfWork)
        repo = AsyncMock(spec=LeaderboardRepository)
        now = datetime.now(UTC)

        lb1 = Leaderboard(id=1, name="Global", created_at=now, updated_at=now)
        snap1 = LeaderboardSnapshot(id=10, leaderboard_id=1, fetched_at=now, entries=[])

        repo.upsert_leaderboard.side_effect = [lb1, RuntimeError("DB error during 2nd leaderboard")]
        repo.create_snapshot.side_effect = [snap1]

        use_case = CreateSnapshot(uow=uow, lb_repo=repo)
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
