from datetime import UTC, datetime
from unittest.mock import AsyncMock

from app.core.db.unit_of_work import UnitOfWork
from app.features.leaderboard.dto.request import (
    CreateSnapshotRequest,
    EntryIn,
    LeaderboardSnapshotIn,
)
from app.features.leaderboard.entities.orm import (
    Leaderboard,
    LeaderboardEntry,
    LeaderboardSnapshot,
)
from app.features.leaderboard.errors.errors import LeaderboardError, LeaderboardErrors
from app.features.leaderboard.repositories.postgres import LeaderboardRepository
from app.features.leaderboard.use_cases.create_snapshot import CreateSnapshot
from app.features.leaderboard.use_cases.get_latest_snapshot import GetLatestSnapshot
from app.features.leaderboard.use_cases.get_leaderboard_names import GetLeaderboardNames
from app.features.player.entities.orm import Player
from app.features.player.repositories.postgres import PlayerRepository


class TestGetLeaderboardNamesUseCase:
    async def test_get_leaderboard_names_empty(self):
        repo = AsyncMock(spec=LeaderboardRepository)
        repo.get_leaderboards.return_value = []

        use_case = GetLeaderboardNames(lb_repo=repo)
        response = await use_case.execute()

        assert response.leaderboard_names == []
        repo.get_leaderboards.assert_awaited_once()

    async def test_get_leaderboard_names_returns_list(self):
        repo = AsyncMock(spec=LeaderboardRepository)
        lb1 = Leaderboard(
            id=1,
            name="Global",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        lb2 = Leaderboard(
            id=2,
            name="Weekly",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repo.get_leaderboards.return_value = [lb1, lb2]

        use_case = GetLeaderboardNames(lb_repo=repo)
        response = await use_case.execute()

        assert response.leaderboard_names == ["Global", "Weekly"]


class TestGetLatestSnapshotUseCase:
    async def test_leaderboard_not_found_raises_error(self):
        repo = AsyncMock(spec=LeaderboardRepository)
        repo.get_leaderboard_by_name.return_value = None

        use_case = GetLatestSnapshot(lb_repo=repo)
        try:
            await use_case.execute("NonExistent")
            assert False, "Should have raised LeaderboardError"
        except LeaderboardError as exc:
            assert (
                exc.error_code
                == LeaderboardErrors.LEADERBOARD_NOT_FOUND.value.error_code
            )
            assert exc.status_code == 404

    async def test_snapshot_not_found_raises_error(self):
        repo = AsyncMock(spec=LeaderboardRepository)
        lb = Leaderboard(
            id=1,
            name="Global",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repo.get_leaderboard_by_name.return_value = lb
        repo.get_latest_snapshot.return_value = None

        use_case = GetLatestSnapshot(lb_repo=repo)
        try:
            await use_case.execute("Global")
            assert False, "Should have raised LeaderboardError"
        except LeaderboardError as exc:
            assert (
                exc.error_code == LeaderboardErrors.SNAPSHOT_NOT_FOUND.value.error_code
            )
            assert exc.status_code == 404

    async def test_get_latest_snapshot_success(self):
        repo = AsyncMock(spec=LeaderboardRepository)
        now = datetime.now(UTC)
        lb = Leaderboard(id=1, name="Global", created_at=now, updated_at=now)
        snapshot = LeaderboardSnapshot(
            id=10,
            leaderboard_id=1,
            fetched_at=now,
            entries=[
                LeaderboardEntry(
                    id=100,
                    snapshot_id=10,
                    rank=1,
                    player_name="Alice",
                    value=50,
                ),
                LeaderboardEntry(
                    id=101,
                    snapshot_id=10,
                    rank=2,
                    player_name="Bob",
                    value=30,
                ),
            ],
        )
        repo.get_leaderboard_by_name.return_value = lb
        repo.get_latest_snapshot.return_value = snapshot

        use_case = GetLatestSnapshot(lb_repo=repo)
        res = await use_case.execute("Global")

        assert res.snapshot_id == 10
        assert res.leaderboard_name == "Global"
        assert len(res.entries) == 2
        assert res.entries[0].entry_id == 100
        assert res.entries[0].player_name == "Alice"
        assert res.entries[0].rank == 1
        assert res.entries[0].value == 50


class TestCreateSnapshotUseCase:
    async def test_create_snapshot_persists_and_commits(self):
        uow = AsyncMock(spec=UnitOfWork)
        redis = AsyncMock()
        redis.delete = AsyncMock(return_value=True)
        lb_repo = AsyncMock(spec=LeaderboardRepository)
        player_repo = AsyncMock(spec=PlayerRepository)
        now = datetime.now(UTC)
        lb = Leaderboard(id=1, name="Global", created_at=now, updated_at=now)
        created_snap = LeaderboardSnapshot(
            id=42, leaderboard_id=1, fetched_at=now, entries=[]
        )
        player = Player(id=1, name="Alice")

        lb_repo.upsert_leaderboard.return_value = lb
        lb_repo.create_snapshot.return_value = created_snap
        player_repo.upsert_player.return_value = player

        use_case = CreateSnapshot(
            uow=uow, redis=redis, lb_repo=lb_repo, player_repo=player_repo
        )
        req = CreateSnapshotRequest(
            snapshots=[
                LeaderboardSnapshotIn(
                    leaderboardName="Global",
                    entries=[
                        EntryIn(rank=1, playerName="Alice", value=100),
                        EntryIn(rank=2, playerName="Bob", value=80),
                    ],
                )
            ]
        )

        res = await use_case.execute(req)

        assert res.snapshot_ids == [42]
        lb_repo.upsert_leaderboard.assert_awaited_once_with("Global")
        lb_repo.create_snapshot.assert_awaited_once()
        assert player_repo.upsert_player.await_count == 2
        uow.commit.assert_awaited_once()
        assert redis.delete.await_count == 2
