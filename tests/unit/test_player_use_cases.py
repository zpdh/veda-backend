from unittest.mock import AsyncMock

from app.features.player.dto.response import PlayerResponse
from app.features.player.entities.orm import Player
from app.features.player.errors.errors import PlayerError, PlayerErrors
from app.features.player.repositories.postgres import PlayerEntryRow, PlayerRepository
from app.features.player.use_cases.get_player import GetPlayer


class TestGetPlayerUseCase:
    async def test_get_player_cache_hit(self):
        player_repo = AsyncMock(spec=PlayerRepository)
        redis = AsyncMock()
        cached_dto = PlayerResponse(
            username="Alice",
            totalCompletions=100,
            entries=[{"leaderboardName": "Global", "rank": 1, "value": 100}],
        )
        redis.get = AsyncMock(
            return_value=cached_dto.model_dump_json(by_alias=True)
        )

        use_case = GetPlayer(player_repo=player_repo, redis=redis)
        res = await use_case.execute("Alice")

        assert res.username == "Alice"
        assert res.total_completions == 100
        player_repo.get_by_name.assert_not_awaited()

    async def test_get_player_not_found_raises_error(self):
        player_repo = AsyncMock(spec=PlayerRepository)
        redis = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        player_repo.get_by_name.return_value = None

        use_case = GetPlayer(player_repo=player_repo, redis=redis)
        try:
            await use_case.execute("UnknownPlayer")
            assert False, "Should have raised PlayerError"
        except PlayerError as exc:
            assert exc.error_code == PlayerErrors.PLAYER_NOT_FOUND.value.error_code
            assert exc.status_code == 404

    async def test_get_player_cache_miss_builds_and_caches_response(self):
        player_repo = AsyncMock(spec=PlayerRepository)
        redis = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        redis.set = AsyncMock(return_value=True)
        player = Player(id=1, name="Alice")
        player_repo.get_by_name.return_value = player
        player_repo.get_player_entries.return_value = [
            PlayerEntryRow(leaderboard_name="Global", rank=1, value=50),
            PlayerEntryRow(leaderboard_name="Weekly", rank=3, value=25),
        ]

        use_case = GetPlayer(player_repo=player_repo, redis=redis)
        res = await use_case.execute("Alice")

        assert res.username == "Alice"
        assert res.total_completions == 75
        assert len(res.entries) == 2
        assert res.entries[0].leaderboard_name == "Global"
        assert res.entries[0].rank == 1
        assert res.entries[0].value == 50

        redis.set.assert_awaited_once()
