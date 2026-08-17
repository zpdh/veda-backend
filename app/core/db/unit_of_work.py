from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db


class UnitOfWork:
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()


async def get_unit_of_work(session: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(session)
