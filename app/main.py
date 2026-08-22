from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.errors import (
    AppError,
    app_error_handler,
    error_handler,
    rate_limit_handler,
)
from app.core.security import rate_limiter
from app.features.leaderboard.api.router import leaderboard_router

app = FastAPI(title="Veda", version="1.0")

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
