from pydantic import BaseSettings


class Settings(BaseSettings):
    allowed_origins: list[str] = ["*"]
    data_dir: str = "data_cache"
    cache_ttl_seconds: int = 3600

    class Config:
        env_prefix = "STOCKTIMUM_"
        case_sensitive = False


settings = Settings()
