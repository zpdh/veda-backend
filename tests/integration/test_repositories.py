from unittest.mock import AsyncMock, MagicMock

from app.features.leaderboard.entities.orm import (
    Leaderboard,
    LeaderboardSnapshot,
)
from app.features.leaderboard.repositories.postgres import LeaderboardRepository


class TestLeaderboardRepositoryUnit:
    async def test_get_leaderboard_by_name(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_lb = Leaderboard(id=1, name="Global")
        mock_result.scalar_one_or_none.return_value = mock_lb
        mock_session.execute.return_value = mock_result

        repo = LeaderboardRepository(session=mock_session)
        res = await repo.get_leaderboard_by_name("global")

        assert res == mock_lb
        mock_session.execute.assert_awaited_once()

    async def test_get_latest_snapshot(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_snap = LeaderboardSnapshot(id=10, leaderboard_id=1)
        mock_result.scalar_one_or_none.return_value = mock_snap
        mock_session.execute.return_value = mock_result

        repo = LeaderboardRepository(session=mock_session)
        res = await repo.get_latest_snapshot(1)

        assert res == mock_snap
        mock_session.execute.assert_awaited_once()

    async def test_create_snapshot_flushes_session(self):
        mock_session = AsyncMock()
        snap = LeaderboardSnapshot(id=1, leaderboard_id=1)

        repo = LeaderboardRepository(session=mock_session)
        res = await repo.create_snapshot(snap)

        assert res == snap
        mock_session.add.assert_called_once_with(snap)
        mock_session.flush.assert_awaited_once()

    async def test_delete_old_snapshots(self):
        mock_session = AsyncMock()
        repo = LeaderboardRepository(session=mock_session)
        await repo.delete_old_snapshots(retention_days=7)

        mock_session.execute.assert_awaited_once()

    async def test_get_leaderboards(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [Leaderboard(id=1, name="Global")]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        repo = LeaderboardRepository(session=mock_session)
        res = await repo.get_leaderboards()

        assert len(res) == 1
        assert res[0].name == "Global"
