from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import PLAYER_USERNAME_PATTERN


class PlayerEntryOut(BaseModel):
    leaderboard_name: str = Field(alias="leaderboardName")
    rank: int
    value: int

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class PlayerResponse(BaseModel):
    username: str = Field(min_length=1, max_length=16, pattern=PLAYER_USERNAME_PATTERN)
    total_completions: int = Field(alias="totalCompletions")
    entries: list[PlayerEntryOut]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class AllPlayersResponseOut(BaseModel):
    username: str = Field(min_length=1, max_length=16, pattern=PLAYER_USERNAME_PATTERN)


class AllPlayersResponse(BaseModel):
    players: list[AllPlayersResponseOut]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )
