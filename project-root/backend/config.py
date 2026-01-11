from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        env="ALLOWED_ORIGINS",
    )
    cache_ttl_seconds: int = Field(300, env="CACHE_TTL_SECONDS")
    data_dir: str = Field("data", env="DATA_DIR")

    @validator("allowed_origins", pre=True)
    def split_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        case_sensitive = False


settings = Settings()
