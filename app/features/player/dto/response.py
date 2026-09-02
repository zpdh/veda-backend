from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import PLAYER_USERNAME_PATTERN

PlayerUsername = Annotated[
    str, Field(min_length=1, max_length=16, pattern=PLAYER_USERNAME_PATTERN)
]


class PlayerEntryOut(BaseModel):
    leaderboard_name: str = Field(alias="leaderboardName")
    rank: int
    value: int
    estimated_playtime_minutes: int = Field(alias="estimatedPlaytimeMinutes")

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class PlayerResponse(BaseModel):
    username: PlayerUsername
    total_completions: int = Field(alias="totalCompletions")
    total_playtime_minutes: int = Field(alias="totalPlaytimeMinutes")
    entries: list[PlayerEntryOut]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class AllPlayersResponse(BaseModel):
    players: list[PlayerUsername]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )
