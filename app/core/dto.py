from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    error_code: str = Field(alias="errorCode")
    message: str
    details: dict | None = None

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
    )
