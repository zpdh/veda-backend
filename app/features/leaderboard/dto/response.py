from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class EntryOut(BaseModel):
    entry_id: int = Field(alias="entryId")
    rank: int
    player_name: str = Field(alias="playerName")
    value: int

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class SnapshotResponse(BaseModel):
    snapshot_id: int = Field(alias="snapshotId")
    leaderboard_name: str = Field(alias="leaderboardName")
    fetched_at: datetime = Field(alias="fetchedAt")
    entries: list[EntryOut]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class SnapshotCreatedResponse(BaseModel):
    snapshot_ids: list[int] = Field(alias="snapshotIds")
    fetched_at: datetime = Field(alias="fetchedAt")
    message: str

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class LeaderboardOut(BaseModel):
    leaderboard_id: str = Field(alias="leaderboardId")
    leaderboard_name: str = Field(alias="leaderboardName")
    estimated_time_per_completion_minutes: int = Field(
        alias="estimatedTimePerCompletionMinutes"
    )

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class LeaderboardsResponse(BaseModel):
    leaderboards: list[LeaderboardOut]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )
