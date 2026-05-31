from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    redis_url: str = "redis://localhost:6379"
    football_api_key: str = ""
    football_api_host: str = "api-football-v1.p.rapidapi.com"
    wc26_api_key: str = ""
    wc26_api_host: str = "wc26-live-football-api.p.rapidapi.com"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
