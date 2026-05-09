from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    debug: bool = False

    database_url: str
    redis_url: str
    secret_key: str

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_bucket: str
    aws_region: str

    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env.local",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()