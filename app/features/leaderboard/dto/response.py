from pydantic import BaseModel, ConfigDict, Field


class EntryOut(BaseModel):
    entry_id: int = Field(alias="entryId")
    rank: int
    player_name: str = Field(alias="playerName")
    value: int

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
