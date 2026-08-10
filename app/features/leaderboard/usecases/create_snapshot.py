from fastapi import Depends

from app.core.db import UnitOfWork, get_unit_of_work
from app.features.leaderboard.dto.request import CreateSnapshotRequest
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)


class CreateSnapshot:
    _unit_of_work: UnitOfWork
    _lb_repo: LeaderboardRepository

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_unit_of_work),  # noqa: B008
        lb_repo: LeaderboardRepository = Depends(get_leaderboard_repository),  # noqa: B008
    ) -> None:
        self._unit_of_work = uow
        self._lb_repo = lb_repo

    async def execute(self, req: CreateSnapshotRequest) -> None: ...
