from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.db.cache import close_redis
from app.core.errors import (
    AppError,
    app_error_handler,
    error_handler,
    rate_limit_handler,
)
from app.core.security import rate_limiter
from app.features.config.router import config_router
from app.features.leaderboard.api.router import leaderboard_router
from app.features.player.api.router import player_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(title="Veda", version="1.0", lifespan=lifespan)

app.state.limiter = rate_limiter.limiter

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_exception_handler(Exception, error_handler)


app.include_router(leaderboard_router)
app.include_router(player_router)
app.include_router(config_router)
