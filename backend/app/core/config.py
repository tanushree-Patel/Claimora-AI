from functools import lru_cache
from pydantic_settings import BaseSettings ,SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/claimora_db"
    app_env:str="development"
    log_level:str="INFO"
  
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-2.5-flash"

    model_config=SettingsConfigDict(env_file=".env",case_sensitive=False)


@lru_cache
def get_settings()->Settings:
    return Settings()