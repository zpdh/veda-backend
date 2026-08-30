from dataclasses import dataclass

from fastapi import Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.features.leaderboard.entities.orm import (
    Leaderboard,
    LeaderboardEntry,
    LeaderboardSnapshot,
)
from app.features.leaderboard.repositories.postgres import pg_insert
from app.features.player.entities.orm import Player


@dataclass
class PlayerEntryRow:
    leaderboard_name: str
    rank: int
    value: int


class PlayerRepository:
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_name(self, player_name: str) -> Player | None:
        query = select(Player).where(func.lower(Player.name) == func.lower(player_name))
        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def upsert_player(self, player_name: str) -> Player:
        player = await self.get_by_name(player_name)

        if player:
            return player

        command = (
            pg_insert(Player)
            .values(name=player_name)
            .on_conflict_do_nothing(index_elements="name")
            .returning(Player)
        )

        result = await self._session.execute(command)
        player = result.scalar_one_or_none()
        if player:
            return player

        player = await self.get_by_name(player_name)
        assert player is not None, "player still missing after race resolution"

        return player

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


def get_player_repository(
    session: AsyncSession = Depends(get_db),
) -> PlayerRepository:
    return PlayerRepository(session)
