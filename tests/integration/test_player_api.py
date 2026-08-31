from unittest.mock import AsyncMock

from httpx import AsyncClient

from app.core.constants import API_ROUTE_PREFIX
from app.features.player.entities.orm import Player
from app.features.player.repositories.postgres import (
    PlayerEntryRow,
    PlayerRepository,
    get_player_repository,
)
from app.main import app


class TestPlayerEndpoints:
    async def test_get_player_success(self, client: AsyncClient):
        mock_repo = AsyncMock(spec=PlayerRepository)
        player = Player(id=1, name="Alice")
        mock_repo.get_by_name.return_value = player
        mock_repo.get_player_entries.return_value = [
            PlayerEntryRow(leaderboard_name="Global", rank=1, value=100)
        ]

        app.dependency_overrides[get_player_repository] = lambda: mock_repo
        try:
            res = await client.get(f"{API_ROUTE_PREFIX}/players/Alice")
            assert res.status_code == 200
            data = res.json()
            assert data["username"] == "Alice"
            assert data["totalCompletions"] == 100
            assert len(data["entries"]) == 1
            assert data["entries"][0]["leaderboardName"] == "Global"
            assert data["entries"][0]["rank"] == 1
            assert data["entries"][0]["value"] == 100
        finally:
            app.dependency_overrides.clear()

    async def test_get_player_not_found(self, client: AsyncClient):
        mock_repo = AsyncMock(spec=PlayerRepository)
        mock_repo.get_by_name.return_value = None

        app.dependency_overrides[get_player_repository] = lambda: mock_repo
        try:
            res = await client.get(f"{API_ROUTE_PREFIX}/players/NonExistent")
            assert res.status_code == 404
            data = res.json()
            assert data["errorCode"] == "ERR_PLAYER_NOT_FOUND"
        finally:
            app.dependency_overrides.clear()
