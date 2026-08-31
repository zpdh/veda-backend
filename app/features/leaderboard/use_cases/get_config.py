from fastapi import Depends

from app.features.leaderboard.dto.response import ConfigResponse, ConfigOut


class GetConfig:
    def __init__(
        self
    ) -> None:
        pass

    async def execute(self) -> ConfigResponse:
        return ConfigResponse(config=[
            ConfigOut(leaderboardName="Zenith Clears",
                      leaderboardId="Zenith", pages=50),
            ConfigOut(leaderboardName="Silver Knights Tomb",
                      leaderboardId="SKT", pages=50),
            ConfigOut(leaderboardName="P.O.R.T.A.L. Strike",
                      leaderboardId="Portal", pages=50),
        ])
