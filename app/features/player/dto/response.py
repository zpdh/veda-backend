from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class PlayerEntryOut(BaseModel):
    leaderboard_name: str = Field(alias="LeaderboardName")
    rank: int
    value: int

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class PlayerResponse(BaseModel):
    username: str
    total_completions: int = Field(alias="totalCompletions")
    entries: list[PlayerEntryOut]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )
