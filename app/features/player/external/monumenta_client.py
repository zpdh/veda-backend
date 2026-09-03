from typing import Any

import httpx

from app.features.player.errors.errors import PlayerError, PlayerErrors

MONUMENTA_API_URL = "https://api.playmonumenta.com/advancement/{username}"


class MonumentaClient:
    async def get_player_achievements(self, username: str) -> Any:  # pyright: ignore[reportAny]
        async with httpx.AsyncClient(
            timeout=15.0
        ) as client:  # refactor to shared client if we use this any more
            response = await client.get(MONUMENTA_API_URL.format(username=username))

        if response.status_code != 200:
            raise PlayerError(
                PlayerErrors.ACHIEVEMENTS_UNAVAILABLE,
                f"Monumenta API returned {response.status_code} for username {username}",
            )

        return response.json()  # pyright: ignore[reportAny]


def get_monumenta_client() -> MonumentaClient:
    return MonumentaClient()
