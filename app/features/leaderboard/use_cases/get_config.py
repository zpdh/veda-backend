from fastapi import Depends

from app.features.leaderboard.dto.response import ConfigResponse, ConfigOut


class GetConfig:
    def __init__(
        self
    ) -> None:
        pass

    async def execute(self) -> ConfigResponse:
        return ConfigResponse(config=[ConfigOut(leaderboardName="Zenith Clears", leaderboardId="Zenith", pages=50)])
