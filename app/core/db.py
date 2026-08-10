from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine: AsyncEngine = create_async_engine(settings.database_url)
async_session_factory: async_sessionmaker = async_sessionmaker(
    engine, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


class UnitOfWork:
    __session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def commit(self) -> None:
        await self.__session.commit()

    async def rollback(self) -> None:
        await self.__session.rollback()


async def get_unit_of_work(session: AsyncSession = Depends(get_db)) -> UnitOfWork:  # noqa: B008
    return UnitOfWork(session)
