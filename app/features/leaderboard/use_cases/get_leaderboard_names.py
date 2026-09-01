from fastapi import Depends

from app.features.leaderboard.dto.response import LeaderboardOut, LeaderboardsResponse
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)


class GetLeaderboards:
    def __init__(
        self, lb_repo: LeaderboardRepository = Depends(get_leaderboard_repository)
    ) -> None:
        self._lb_repo: LeaderboardRepository = lb_repo

    async def execute(self) -> LeaderboardsResponse:
        lbs = await self._lb_repo.get_leaderboards()
        return LeaderboardsResponse(
            leaderboards=[
                LeaderboardOut(
                    leaderboardName=lb.name,
                    leaderboardId=lb.external_leaderboard_id,
                    estimatedTimePerCompletionMinutes=lb.estimated_time_per_completion_minutes,
                )
                for lb in lbs
            ]
        )
