from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

from limits.storage import storage_from_string
from limits.strategies import MovingWindowRateLimiter
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.cache import get_redis
from app.core.db.session import get_db
from app.core.db.unit_of_work import UnitOfWork, get_unit_of_work
from app.core.security import rate_limiter
from app.features.leaderboard.repositories.postgres import (
    LeaderboardRepository,
)
from app.features.player.repositories.postgres import (
    PlayerRepository,
)
from app.main import app

# Ensure slowapi uses in-memory backend during tests
_mem_storage = storage_from_string("memory://")
rate_limiter.limiter._storage = _mem_storage
rate_limiter.limiter._limiter = MovingWindowRateLimiter(_mem_storage)


@pytest.fixture(autouse=True)
def reset_rate_limiter_before_each_test():
    """Reset the in-memory rate limiter before each test execution to ensure isolation."""
    rate_limiter.limiter.reset()
    yield
    rate_limiter.limiter.reset()


@pytest.fixture
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.aclose = AsyncMock()
    return redis


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
def mock_player_repo(mock_async_session: AsyncMock) -> AsyncMock:
    repo = AsyncMock(spec=PlayerRepository)
    return repo


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.shared_secret}"}


@pytest.fixture
async def client(mock_redis: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_redis] = lambda: mock_redis
    async with AsyncClient(
        transport=ASGITransport(app=app, client=("127.0.0.1", 50000)),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.pop(get_redis, None)


@pytest.fixture
async def client_with_mock_db(
    mock_async_session: AsyncMock,
    mock_redis: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_async_session

    async def override_get_uow() -> UnitOfWork:
        return UnitOfWork(session=mock_async_session)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_unit_of_work] = override_get_uow
    app.dependency_overrides[get_redis] = lambda: mock_redis

    async with AsyncClient(
        transport=ASGITransport(app=app, client=("127.0.0.1", 50000)),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
