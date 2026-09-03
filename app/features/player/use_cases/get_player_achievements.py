from fastapi import Depends
from redis.asyncio.client import Redis

from app.core.constants import CACHE_TTL_SECONDS_LONG, CACHE_TTL_SECONDS_SHORT
from app.core.db.cache import get_redis
from app.features.player.dto.response import PlayerAchievementsResponse
from app.features.player.external.monumenta_client import (
    MonumentaClient,
    get_monumenta_client,
)


class GetPlayerAchievements:
    def __init__(
        self,
        monu_client: MonumentaClient = Depends(get_monumenta_client),
        redis: Redis = Depends(get_redis),
    ) -> None:
        self._monu_client: MonumentaClient = monu_client
        self._redis: Redis = redis

    async def execute(self, username: str) -> PlayerAchievementsResponse:
        cache_key = f"achievements:{username.lower()}"

        cached_res = await self._redis.get(cache_key)
        if cached_res is not None:
            return PlayerAchievementsResponse.model_validate_json(cached_res)

        # Quick explanation,
        # This is the expected monumenta api format:
        # "<ach OR ach group>": {
        #     "criteria": {
        #         <achievement criteria>
        #         <achievement criteria>
        #         <achievement criteria>
        #         ...
        #     },
        #     "done": boolean
        # }
        # So this is doing:
        # For each achievement criteria in an achievement group that is marked as done, increment by 1.
        data = await self._monu_client.get_player_achievements(username)

        ach_count = sum(
            1
            for entry in data.values()
            if isinstance(entry, dict) and entry.get("done") is True
        )
        total_ach_count = sum(1 for entry in data.values() if isinstance(entry, dict))

        response = PlayerAchievementsResponse(
            username=username,
            achievementCount=ach_count,
            achievementCountTotal=total_ach_count,
        )

        _ = await self._redis.set(
            cache_key, response.model_dump_json(by_alias=True), CACHE_TTL_SECONDS_SHORT
        )

        return response
