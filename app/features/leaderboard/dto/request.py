from collections import Counter
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.features.leaderboard.errors.errors import (
    LeaderboardError,
    LeaderboardErrors,
)


class EntryIn(BaseModel):
    rank: int = Field(gt=0)
    player_name: str = Field(alias="playerName", min_length=1, max_length=16, pattern=r"^[a-zA-Z0-9_]+$")
    value: int = Field(ge=0)

    model_config: ClassVar[ConfigDict]  = ConfigDict(validate_by_name=True, validate_by_alias=True)


class LeaderboardSnapshotIn(BaseModel):
    leaderboard_name: str = Field(alias="leaderboardName", min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9 _.-]+$" )
    entries: list[EntryIn] = Field(alias="entries", min_length=1)

    model_config: ClassVar[ConfigDict] = ConfigDict(validate_by_name=True, validate_by_alias=True)

    @field_validator("entries")
    @classmethod
    def entries_ranks_must_be_unique(cls, entries: list[EntryIn]) -> list[EntryIn]:
        ranks = [e.rank for e in entries]
        counts = Counter(ranks)
        duplicates = [rank for rank, count in counts.items() if count > 1]

        if duplicates:
            raise LeaderboardError(
                LeaderboardErrors.DUPLICATE_RANK,
                f"Duplicate rank(s): {duplicates}",
                {"ranks": ranks, "duplicates": duplicates},
            )
        return entries


class CreateSnapshotRequest(BaseModel):
    snapshots: list[LeaderboardSnapshotIn] = Field(alias="snapshots", min_length=1)
