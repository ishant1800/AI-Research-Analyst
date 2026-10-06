from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

# Look for .env in current directory or parent directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    OPENAI_API_KEY: Optional[str] = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: Optional[str] = None

    # Search Provider: 'duckduckgo', 'tavily', or 'mock'
    SEARCH_PROVIDER: str = "duckduckgo"
    TAVILY_API_KEY: Optional[str] = None

    DATABASE_URL: str = "sqlite:///./research.db"

    MAX_RESEARCH_LOOPS: int = 4
    MAX_SEARCH_RESULTS_PER_QUERY: int = 5
    MAX_PAGE_EXTRACT_CHARS: int = 4500
    ENABLE_REFLECTION_VERIFICATION: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

settings = Settings()
