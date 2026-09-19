from fastapi import Depends

from app.features.leaderboard.dto.response import (
    WeightEntryOut,
    WeightLeaderboardResponse,
)
from app.features.player.repositories.postgres import (
    PlayerRepository,
    get_player_repository,
)


class GetWeightLeaderboard:
    def __init__(
        self, player_repo: PlayerRepository = Depends(get_player_repository)
    ) -> None:
        self._player_repo: PlayerRepository = player_repo

    async def execute(self) -> WeightLeaderboardResponse:
        players = await self._player_repo.get_weight_leaderboard()

        return WeightLeaderboardResponse(
            entries=[
                WeightEntryOut(rank=rank, playerName=player.name, weight=player.weight)
                for rank, player in enumerate(players, start=1)
            ]
        )
