from datetime import UTC, datetime
from unittest.mock import AsyncMock

from httpx import AsyncClient

from app.core.config import settings
from app.core.constants import API_ROUTE_PREFIX
from app.core.db.unit_of_work import UnitOfWork, get_unit_of_work
from app.features.leaderboard.entities.orm import (
    Leaderboard,
    LeaderboardEntry,
    LeaderboardSnapshot,
)
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)
from app.features.player.entities.orm import Player
from app.features.player.repositories.postgres import (
    PlayerRepository,
    get_player_repository,
)
from app.main import app


class TestLeaderboardEndpoints:
    async def test_get_leaderboards_empty(self, client: AsyncClient):
        mock_repo = AsyncMock(spec=LeaderboardRepository)
        mock_repo.get_leaderboards.return_value = []

        app.dependency_overrides[get_leaderboard_repository] = lambda: mock_repo
        try:
            res = await client.get(f"{API_ROUTE_PREFIX}/leaderboards")
            assert res.status_code == 200
            data = res.json()
            assert data["leaderboards"] == []
        finally:
            app.dependency_overrides.clear()

    async def test_get_leaderboards_success(self, client: AsyncClient):
        mock_repo = AsyncMock(spec=LeaderboardRepository)
        mock_repo.get_leaderboards.return_value = [
            Leaderboard(
                id=1,
                external_leaderboard_id="global-id",
                name="Global",
                estimated_time_per_completion_minutes=30,
                group_size=1,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            Leaderboard(
                id=2,
                external_leaderboard_id="weekly-id",
                name="Weekly",
                estimated_time_per_completion_minutes=45,
                group_size=1,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]

        app.dependency_overrides[get_leaderboard_repository] = lambda: mock_repo
        try:
            res = await client.get(f"{API_ROUTE_PREFIX}/leaderboards")
            assert res.status_code == 200
            data = res.json()
            assert data["leaderboards"] == [
                {
                    "leaderboardId": "global-id",
                    "leaderboardName": "Global",
                    "estimatedTimePerCompletionMinutes": 30,
                },
                {
                    "leaderboardId": "weekly-id",
                    "leaderboardName": "Weekly",
                    "estimatedTimePerCompletionMinutes": 45,
                },
            ]
        finally:
            app.dependency_overrides.clear()

    async def test_get_latest_snapshot_success(self, client: AsyncClient):
        mock_repo = AsyncMock(spec=LeaderboardRepository)
        now = datetime.now(UTC)
        lb = Leaderboard(id=1, name="Global", created_at=now, updated_at=now)
        snapshot = LeaderboardSnapshot(
            id=10,
            leaderboard_id=1,
            fetched_at=now,
            entries=[
                LeaderboardEntry(
                    id=101, snapshot_id=10, rank=1, player_name="Alice", value=100
                ),
                LeaderboardEntry(
                    id=102, snapshot_id=10, rank=2, player_name="Bob", value=75
                ),
            ],
        )
        mock_repo.get_leaderboard_by_name.return_value = lb
        mock_repo.get_latest_snapshot.return_value = snapshot

        app.dependency_overrides[get_leaderboard_repository] = lambda: mock_repo
        try:
            res = await client.get(f"{API_ROUTE_PREFIX}/leaderboards/Global")
            assert res.status_code == 200
            data = res.json()
            assert data["snapshotId"] == 10
            assert data["leaderboardName"] == "Global"
            assert len(data["entries"]) == 2
            assert data["entries"][0]["rank"] == 1
            assert data["entries"][0]["playerName"] == "Alice"
            assert data["entries"][0]["value"] == 100
        finally:
            app.dependency_overrides.clear()

    async def test_get_latest_snapshot_not_found_leaderboard(self, client: AsyncClient):
        mock_repo = AsyncMock(spec=LeaderboardRepository)
        mock_repo.get_leaderboard_by_name.return_value = None

        app.dependency_overrides[get_leaderboard_repository] = lambda: mock_repo
        try:
            res = await client.get(f"{API_ROUTE_PREFIX}/leaderboards/unknown_board")
            assert res.status_code == 404
            data = res.json()
            assert data["errorCode"] == "ERR_LEADERBOARD_NOT_FOUND"
        finally:
            app.dependency_overrides.clear()

    async def test_get_latest_snapshot_not_found_snapshot(self, client: AsyncClient):
        mock_repo = AsyncMock(spec=LeaderboardRepository)
        now = datetime.now(UTC)
        lb = Leaderboard(id=1, name="EmptyBoard", created_at=now, updated_at=now)
        mock_repo.get_leaderboard_by_name.return_value = lb
        mock_repo.get_latest_snapshot.return_value = None

        app.dependency_overrides[get_leaderboard_repository] = lambda: mock_repo
        try:
            res = await client.get(f"{API_ROUTE_PREFIX}/leaderboards/EmptyBoard")
            assert res.status_code == 404
            data = res.json()
            assert data["errorCode"] == "ERR_SNAPSHOT_NOT_FOUND"
        finally:
            app.dependency_overrides.clear()

    async def test_post_snapshot_success(self, client: AsyncClient):
        mock_lb_repo = AsyncMock(spec=LeaderboardRepository)
        mock_player_repo = AsyncMock(spec=PlayerRepository)
        mock_uow = AsyncMock(spec=UnitOfWork)
        now = datetime.now(UTC)

        lb = Leaderboard(id=1, name="Global", created_at=now, updated_at=now)
        created_snap = LeaderboardSnapshot(
            id=124, leaderboard_id=1, fetched_at=now, entries=[]
        )
        player = Player(id=1, name="Alice")

        mock_lb_repo.upsert_leaderboard.return_value = lb
        mock_lb_repo.create_snapshot.return_value = created_snap
        mock_player_repo.upsert_player.return_value = player

        app.dependency_overrides[get_leaderboard_repository] = lambda: mock_lb_repo
        app.dependency_overrides[get_player_repository] = lambda: mock_player_repo
        app.dependency_overrides[get_unit_of_work] = lambda: mock_uow
        try:
            payload = {
                "snapshots": [
                    {
                        "leaderboardName": "Global",
                        "entries": [
                            {"rank": 1, "playerName": "Alice", "value": 50},
                            {"rank": 2, "playerName": "Bob", "value": 30},
                        ],
                    }
                ]
            }
            res = await client.post(
                f"{API_ROUTE_PREFIX}/leaderboards/snapshot",
                json=payload,
                headers={"Authorization": f"Bearer {settings.shared_secret}"},
            )
            assert res.status_code == 201
            data = res.json()
            assert data["snapshotIds"] == [124]
            assert "fetchedAt" in data
            assert data["message"] == "Snapshots created successfully."
            mock_uow.commit.assert_awaited_once()
        finally:
            app.dependency_overrides.clear()

    async def test_post_snapshot_unauthorized_missing_token(self, client: AsyncClient):
        payload = {
            "snapshots": [
                {
                    "leaderboardName": "Global",
                    "entries": [{"rank": 1, "playerName": "Alice", "value": 50}],
                }
            ]
        }
        res = await client.post(
            f"{API_ROUTE_PREFIX}/leaderboards/snapshot", json=payload
        )
        assert res.status_code == 401 or res.status_code == 403

    async def test_post_snapshot_unauthorized_invalid_token(self, client: AsyncClient):
        payload = {
            "snapshots": [
                {
                    "leaderboardName": "Global",
                    "entries": [{"rank": 1, "playerName": "Alice", "value": 50}],
                }
            ]
        }
        res = await client.post(
            f"{API_ROUTE_PREFIX}/leaderboards/snapshot",
            json=payload,
            headers={"Authorization": "Bearer bad-token"},
        )
        assert res.status_code == 401
        data = res.json()
        assert data["errorCode"] == "ERR_UNAUTHORIZED"

    async def test_post_snapshot_duplicate_rank_returns_400(self, client: AsyncClient):
        payload = {
            "snapshots": [
                {
                    "leaderboardName": "Global",
                    "entries": [
                        {"rank": 1, "playerName": "Alice", "value": 50},
                        {"rank": 1, "playerName": "Bob", "value": 30},
                    ],
                }
            ]
        }
        res = await client.post(
            f"{API_ROUTE_PREFIX}/leaderboards/snapshot",
            json=payload,
            headers={"Authorization": f"Bearer {settings.shared_secret}"},
        )
        assert res.status_code == 400
        data = res.json()
        assert data["errorCode"] == "ERR_DUPLICATE_RANK"
