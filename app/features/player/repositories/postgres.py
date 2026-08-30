from dataclasses import dataclass

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.leaderboard.entities.orm import (
    Leaderboard,
    LeaderboardEntry,
    LeaderboardSnapshot,
)


@dataclass
class PlayerEntryRow:
    leaderboard_name: str
    rank: int
    value: int


class PlayerRepository:
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_player_entries(self, player_name: str) -> list[PlayerEntryRow]:
        query = (
            select(
                Leaderboard.name.label("leaderboard_name"),
                LeaderboardEntry.rank,
                LeaderboardEntry.value,
            )
            .distinct(Leaderboard.name)
            .select_from(LeaderboardEntry)
            .join(Leaderboard, Leaderboard.id == LeaderboardSnapshot.leaderboard_id)
            .where(func.lower(LeaderboardEntry.player_name) == func.lower(player_name))
            .order_by(Leaderboard.name, LeaderboardSnapshot.fetched_at.desc())
        )

        result = await self._session.execute(query)

        return [PlayerEntryRow(**entry) for entry in result.mappings()]
