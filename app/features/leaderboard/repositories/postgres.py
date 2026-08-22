from datetime import UTC, datetime, timedelta

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.session import get_db
from app.features.leaderboard.entities.orm import Leaderboard, LeaderboardSnapshot


class LeaderboardRepository:
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_leaderboard_by_name(self, name: str) -> Leaderboard | None:
        query = select(Leaderboard).where(Leaderboard.name == name)
        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def upsert_leaderboard(self, name: str) -> Leaderboard:
        lb = await self.get_leaderboard_by_name(name)
        if lb:
            return lb

        command = (
            pg_insert(Leaderboard)
            .values(name=name)
            .on_conflict_do_nothing(index_elements=["name"])
            .returning(Leaderboard)
        )

        result = await self._session.execute(command)

        lb = result.scalar_one_or_none()
        if lb:
            return lb

        lb = await self.get_leaderboard_by_name(name)
        assert lb is not None, "leaderboard still missing after race resolution"

        return lb

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
        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def create_snapshot(
        self, snapshot: LeaderboardSnapshot
    ) -> LeaderboardSnapshot:
        self._session.add(snapshot)

        await self._session.flush()

        return snapshot

    async def delete_old_snapshots(self, retention_days: int = 7) -> None:
        cutoff_time = datetime.now(UTC) - timedelta(days=retention_days)
        command = delete(LeaderboardSnapshot).where(
            LeaderboardSnapshot.fetched_at < cutoff_time
        )

        _ = await self._session.execute(command)

    async def get_leaderboards(self) -> list[Leaderboard]:
        query = select(Leaderboard)
        result = await self._session.execute(query)

        return list(result.scalars().all())


async def get_leaderboard_repository(
    session: AsyncSession = Depends(get_db),
) -> LeaderboardRepository:
    return LeaderboardRepository(session)
