from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class ConfigOut(BaseModel):
    leaderboard_name: str = Field(alias="leaderboardName")
    leaderboard_id: str = Field(alias="leaderboardId")
    pages: int

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )


class ConfigResponse(BaseModel):
    config: list[ConfigOut]

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, validate_by_alias=True, serialize_by_alias=True
    )
