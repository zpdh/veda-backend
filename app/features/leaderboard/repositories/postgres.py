from datetime import UTC, datetime, timedelta

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.features.leaderboard.entities.orm import Leaderboard, LeaderboardSnapshot


class LeaderboardRepository:
    __session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def get_leaderboard_by_name(self, name: str) -> Leaderboard | None:
        query = select(Leaderboard).where(Leaderboard.name == name)
        result = await self.__session.execute(query)

        return result.scalar_one_or_none()

    async def get_latest_snapshot(
        self, leaderboard_id: int
    ) -> LeaderboardSnapshot | None:
        query = (
            select(LeaderboardSnapshot)
            .where(LeaderboardSnapshot.leaderboard_id == leaderboard_id)
            .options(selectinload(LeaderboardSnapshot.entries))
            .order_by(LeaderboardSnapshot.fetched_at.desc())
            .limit(1)
        )
        result = await self.__session.execute(query)

        return result.scalar_one_or_none()

    async def create_snapshot(
        self, snapshot: LeaderboardSnapshot
    ) -> LeaderboardSnapshot:
        self.__session.add(snapshot)

        await self.__session.flush()

        return snapshot

    async def delete_old_snapshots(self, retention_days: int = 7) -> None:
        cutoff_time = datetime.now(UTC) - timedelta(days=retention_days)
        command = delete(LeaderboardSnapshot).where(
            LeaderboardSnapshot.fetched_at < cutoff_time
        )

        await self.__session.execute(command)


async def get_leaderboard_repository(
    session: AsyncSession = Depends(get_db),  # noqa: B008
) -> LeaderboardRepository:
    return LeaderboardRepository(session)
