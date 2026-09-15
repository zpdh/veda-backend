from typing import Any

import httpx
from fastapi import Depends

from app.core.http import get_http_client
from app.features.player.errors.errors import PlayerError, PlayerErrors

MONUMENTA_API_URL = "https://api.playmonumenta.com/advancement/{username}"


class MonumentaClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self.http: httpx.AsyncClient = http_client

    async def get_player_achievements(self, username: str) -> Any:  # pyright: ignore[reportAny, reportExplicitAny]
        response = await self.http.get(MONUMENTA_API_URL.format(username=username))

        if response.status_code != 200:
            raise PlayerError(
                PlayerErrors.ACHIEVEMENTS_UNAVAILABLE,
                f"Monumenta API returned {response.status_code} for username {username}",
            )

        return response.json()  # pyright: ignore[reportAny]


def get_monumenta_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> MonumentaClient:
    return MonumentaClient(http_client)
