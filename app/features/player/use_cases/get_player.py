from fastapi import Depends
from redis.asyncio import Redis

from app.core.constants import CACHE_TTL_SECONDS
from app.core.db.cache import get_redis
from app.features.player.dto.response import PlayerEntryOut, PlayerResponse
from app.features.player.entities.orm import Player
from app.features.player.errors.errors import PlayerError, PlayerErrors
from app.features.player.repositories.postgres import (
    PlayerRepository,
    get_player_repository,
)


class GetPlayer:
    def __init__(
        self,
        player_repo: PlayerRepository = Depends(get_player_repository),
        redis: Redis = Depends(get_redis),
    ) -> None:
        self._player_repo: PlayerRepository = player_repo
        self._redis: Redis = redis

    async def execute(self, player_name: str) -> PlayerResponse:
        cache_key = f"player:{player_name.lower()}"
        cached_player = await self._redis.get(cache_key)

        if cached_player is not None:
            return PlayerResponse.model_validate_json(cached_player)

        player = await self._player_repo.get_by_name(player_name)
        if player is None:
            raise PlayerError(
                PlayerErrors.PLAYER_NOT_FOUND,
                f"Player {player_name} does not exist.",
                {"playerName": player_name},
            )

        response = await self._build_player_response(player)

        _ = await self._redis.set(
            cache_key, response.model_dump_json(by_alias=True), ex=CACHE_TTL_SECONDS
        )

        return response

    async def _build_player_response(self, player: Player) -> PlayerResponse:
        entry_rows = await self._player_repo.get_player_entries(player.name)
        entries = [
            PlayerEntryOut(
                leaderboardName=entry.leaderboard_name,
                rank=entry.rank,
                value=entry.value,
                estimatedPlaytimeMinutes=entry.value
                * entry.estimated_time_per_completion_minutes,
            )
            for entry in entry_rows
        ]

        total_comps = sum(entry.value for entry in entries)
        total_playtime_minutes = sum(
            entry.estimated_playtime_minutes for entry in entries
        )

        return  PlayerResponse(
                  username=player.name,
                  totalCompletions=total_comps,
                  totalPlaytimeMinutes=total_playtime_minutes,
                  entries=entries,
              )
