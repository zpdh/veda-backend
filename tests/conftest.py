from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.session import get_db
from app.core.db.unit_of_work import UnitOfWork, get_unit_of_work
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
    get_leaderboard_repository,
)
from app.main import app


@pytest.fixture
def mock_async_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.add = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_uow(mock_async_session: AsyncMock) -> UnitOfWork:
    return UnitOfWork(session=mock_async_session)


@pytest.fixture
def mock_leaderboard_repo(mock_async_session: AsyncMock) -> AsyncMock:
    repo = AsyncMock(spec=LeaderboardRepository)
    return repo


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.shared_secret}"}


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def client_with_mock_db(
    mock_async_session: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_async_session

    async def override_get_uow() -> UnitOfWork:
        return UnitOfWork(session=mock_async_session)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_unit_of_work] = override_get_uow

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
