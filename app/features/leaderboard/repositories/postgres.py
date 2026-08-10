from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.leaderboard.entities.orm import Leaderboard


class LeaderboardRepository:
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_leaderboard_by_name(self, name: str) -> Leaderboard | None:
        query = select(Leaderboard).where(Leaderboard.name == name)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()


class SnapshotRepository:
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_latest_snapshot(self): ...

    async def create_snapshot(self): ...

    async def delete_old_snapshots(self): ...
