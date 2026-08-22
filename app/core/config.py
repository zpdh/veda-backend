from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    frontend_url: str
    shared_secret: str
    app_name: str = "Veda API"

    model_config = SettingsConfigDict(env_file=".env")  # pyright: ignore[reportUnannotatedClassAttribute]


settings = Settings()  # pyright: ignore[reportCallIssue]
