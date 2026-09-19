from datetime import UTC, datetime
from unittest.mock import AsyncMock

from app.core.db.unit_of_work import UnitOfWork
from app.core.util.weight import EntryRow, calculate_weight_for_rows
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
from app.features.leaderboard.use_cases.get_leaderboard_names import GetLeaderboards
from app.features.leaderboard.use_cases.get_weight_leaderboard import (
    GetWeightLeaderboard,
)
from app.features.player.entities.orm import Player
from app.features.player.repositories.postgres import (
    PlayerEntryRow,
    PlayerRepository,
)


class TestGetLeaderboardNamesUseCase:
    async def test_get_leaderboard_names_empty(self):
        repo = AsyncMock(spec=LeaderboardRepository)
        repo.get_leaderboards.return_value = []

        use_case = GetLeaderboards(lb_repo=repo)
        response = await use_case.execute()

        assert response.leaderboards == []
        repo.get_leaderboards.assert_awaited_once()

    async def test_get_leaderboard_names_returns_list(self):
        repo = AsyncMock(spec=LeaderboardRepository)
        lb1 = Leaderboard(
            id=1,
            external_leaderboard_id="global-id",
            name="Global",
            estimated_time_per_completion_minutes=30,
            group_size=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        lb2 = Leaderboard(
            id=2,
            external_leaderboard_id="weekly-id",
            name="Weekly",
            estimated_time_per_completion_minutes=45,
            group_size=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repo.get_leaderboards.return_value = [lb1, lb2]

        use_case = GetLeaderboards(lb_repo=repo)
        response = await use_case.execute()

        assert [lb.leaderboard_name for lb in response.leaderboards] == [
            "Global", "Weekly"
        ]
        assert [lb.leaderboard_id for lb in response.leaderboards] == [
            "global-id", "weekly-id"
        ]


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
        lb = Leaderboard(
            id=1,
            external_leaderboard_id="global-id",
            name="Global",
            estimated_time_per_completion_minutes=30,
            group_size=1,
            created_at=now,
            updated_at=now,
        )
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


class TestGetWeightLeaderboardUseCase:
    async def test_returns_entries_ranked_in_order(self):
        player_repo = AsyncMock(spec=PlayerRepository)
        player_repo.get_weight_leaderboard.return_value = [
            Player(id=1, name="Alice", weight=99.5),
            Player(id=2, name="Bob", weight=80.0),
            Player(id=3, name="Carol", weight=12.25),
        ]

        use_case = GetWeightLeaderboard(player_repo=player_repo)
        res = await use_case.execute()

        assert [entry.rank for entry in res.entries] == [1, 2, 3]
        assert [entry.player_name for entry in res.entries] == [
            "Alice",
            "Bob",
            "Carol",
        ]
        assert [entry.weight for entry in res.entries] == [99.5, 80.0, 12.25]
        player_repo.get_weight_leaderboard.assert_awaited_once()

    async def test_returns_empty_entries_when_no_players(self):
        player_repo = AsyncMock(spec=PlayerRepository)
        player_repo.get_weight_leaderboard.return_value = []

        use_case = GetWeightLeaderboard(player_repo=player_repo)
        res = await use_case.execute()

        assert res.entries == []
        player_repo.get_weight_leaderboard.assert_awaited_once()


class TestCreateSnapshotUseCase:
    async def test_create_snapshot_persists_and_commits(self):
        uow = AsyncMock(spec=UnitOfWork)
        redis = AsyncMock()
        redis.delete = AsyncMock(return_value=True)
        lb_repo = AsyncMock(spec=LeaderboardRepository)
        player_repo = AsyncMock(spec=PlayerRepository)
        now = datetime.now(UTC)
        lb = Leaderboard(
            id=1,
            external_leaderboard_id="global-id",
            name="Global",
            estimated_time_per_completion_minutes=30,
            group_size=1,
            created_at=now,
            updated_at=now,
        )
        created_snap = LeaderboardSnapshot(
            id=42,
            leaderboard_id=1,
            fetched_at=now,
            entries=[
                LeaderboardEntry(rank=1, player_name="Alice", value=100),
                LeaderboardEntry(rank=2, player_name="Bob", value=80),
            ],
        )
        player = Player(id=1, name="Alice")

        lb_repo.get_leaderboard_by_name.return_value = lb
        lb_repo.create_snapshot.return_value = created_snap
        player_repo.upsert_many.return_value = None

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
        lb_repo.get_leaderboard_by_name.assert_awaited_once_with("Global")
        lb_repo.create_snapshot.assert_awaited_once()
        player_repo.upsert_many.assert_awaited_once_with({"Alice", "Bob"})
        uow.commit.assert_awaited_once()
        redis.delete.assert_awaited_once()


class TestCreateSnapshotWeightWritePath:
    async def test_computes_and_persists_weights_for_affected_players(self):
        uow = AsyncMock(spec=UnitOfWork)
        redis = AsyncMock()
        redis.delete = AsyncMock(return_value=True)
        lb_repo = AsyncMock(spec=LeaderboardRepository)
        player_repo = AsyncMock(spec=PlayerRepository)
        now = datetime.now(UTC)

        lb = Leaderboard(
            id=1,
            external_leaderboard_id="global-id",
            name="Global",
            estimated_time_per_completion_minutes=30,
            group_size=1,
            created_at=now,
            updated_at=now,
        )
        created_snap = LeaderboardSnapshot(
            id=42,
            leaderboard_id=1,
            fetched_at=now,
            entries=[
                LeaderboardEntry(rank=1, player_name="Alice", value=100),
                LeaderboardEntry(rank=2, player_name="Bob", value=80),
            ],
        )

        lb_repo.get_leaderboard_by_name.return_value = lb
        lb_repo.create_snapshot.return_value = created_snap
        player_repo.upsert_many.return_value = None
        player_repo.get_entries_for_many.return_value = [
            PlayerEntryRow(
                leaderboard_name="Global",
                player_name="Alice",
                rank=1,
                value=100,
                estimated_time_per_completion_minutes=30,
                group_size=1,
            ),
            PlayerEntryRow(
                leaderboard_name="Global",
                player_name="Bob",
                rank=2,
                value=80,
                estimated_time_per_completion_minutes=30,
                group_size=1,
            ),
        ]

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

        await use_case.execute(req)

        player_repo.get_entries_for_many.assert_awaited_once_with({"Alice", "Bob"})

        expected_weights = {
            "Alice": calculate_weight_for_rows([EntryRow(1, 100, 30, 1)]),
            "Bob": calculate_weight_for_rows([EntryRow(2, 80, 30, 1)]),
        }
        player_repo.update_weights_for_many.assert_awaited_once_with(expected_weights)

    async def test_groups_multiple_boards_per_player_into_single_weight(self):
        uow = AsyncMock(spec=UnitOfWork)
        redis = AsyncMock()
        redis.delete = AsyncMock(return_value=True)
        lb_repo = AsyncMock(spec=LeaderboardRepository)
        player_repo = AsyncMock(spec=PlayerRepository)
        now = datetime.now(UTC)

        lb = Leaderboard(
            id=1,
            external_leaderboard_id="global-id",
            name="Global",
            estimated_time_per_completion_minutes=30,
            group_size=1,
            created_at=now,
            updated_at=now,
        )
        created_snap = LeaderboardSnapshot(
            id=42,
            leaderboard_id=1,
            fetched_at=now,
            entries=[LeaderboardEntry(rank=1, player_name="Alice", value=100)],
        )

        lb_repo.get_leaderboard_by_name.return_value = lb
        lb_repo.create_snapshot.return_value = created_snap
        player_repo.upsert_many.return_value = None
        # Alice appears on two different boards; both rows must be grouped
        # into a single weight entry (diversification spans all her boards).
        player_repo.get_entries_for_many.return_value = [
            PlayerEntryRow(
                leaderboard_name="Global",
                player_name="Alice",
                rank=1,
                value=100,
                estimated_time_per_completion_minutes=30,
                group_size=1,
            ),
            PlayerEntryRow(
                leaderboard_name="Zenith",
                player_name="Alice",
                rank=3,
                value=40,
                estimated_time_per_completion_minutes=15,
                group_size=4,
            ),
        ]

        use_case = CreateSnapshot(
            uow=uow, redis=redis, lb_repo=lb_repo, player_repo=player_repo
        )
        req = CreateSnapshotRequest(
            snapshots=[
                LeaderboardSnapshotIn(
                    leaderboardName="Global",
                    entries=[EntryIn(rank=1, playerName="Alice", value=100)],
                )
            ]
        )

        await use_case.execute(req)

        player_repo.update_weights_for_many.assert_awaited_once()
        weights = player_repo.update_weights_for_many.await_args.args[0]

        assert set(weights.keys()) == {"Alice"}
        assert weights["Alice"] == calculate_weight_for_rows(
            [EntryRow(1, 100, 30, 1), EntryRow(3, 40, 15, 4)]
        )
