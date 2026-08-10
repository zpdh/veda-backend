from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EntryOut(BaseModel):
    entry_id: int = Field(alias="entryId")
    rank: int
    player_name: str = Field(alias="playerName")
    value: int

    model_config = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class SnapshotResponse(BaseModel):
    snapshot_id: int = Field(alias="snapshotId")
    leaderboard_name: str = Field(alias="leaderboardName")
    fetched_at: datetime = Field(alias="fetchedAt")
    entries: list[EntryOut]

    model_config = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class SnapshotCreatedResponse(BaseModel):
    snapshot_ids: list[int] = Field(alias="snapshotIds")
    fetched_at: datetime = Field(alias="fetchedAt")
    message: str

    model_config = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )
