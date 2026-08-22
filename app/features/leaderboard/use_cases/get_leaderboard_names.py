from fastapi import Depends

from app.features.leaderboard.dto.response import LeaderboardNamesResponse
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)


class GetLeaderboardNames:
    lb_repo: LeaderboardRepository

    def __init__(
        self, lb_repo: LeaderboardRepository = Depends(get_leaderboard_repository)
    ) -> None:
        self.lb_repo = lb_repo

    async def execute(self) -> LeaderboardNamesResponse:
        lbs = await self.lb_repo.get_leaderboards()
        return LeaderboardNamesResponse(leaderboardNames=[lb.name for lb in lbs])
