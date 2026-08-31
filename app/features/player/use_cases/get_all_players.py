from fastapi import Depends

from app.features.player.dto.response import AllPlayersResponse, AllPlayersResponseOut
from app.features.player.repositories.postgres import (
    PlayerRepository,
    get_player_repository,
)


class GetAllPlayers:
    def __init__(
        self, player_repo: PlayerRepository = Depends(get_player_repository)
    ) -> None:
        self._player_repo: PlayerRepository = player_repo

    async def execute(self) -> AllPlayersResponse:
        res = await self._player_repo.get_all()

        return AllPlayersResponse(
            players=[AllPlayersResponseOut(username=player.name) for player in res]
        )
