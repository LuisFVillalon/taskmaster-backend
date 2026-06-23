from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str

    # Supabase
    supabase_url: str
    supabase_key: str

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # prevents crashes if extra vars exist
    )


settings = Settings()