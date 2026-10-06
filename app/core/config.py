"""
Application-wide configuration via pydantic-settings.
Reads from environment variables and an optional .env file.
"""
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:  # fallback for environments without pydantic-settings
    from pydantic import BaseSettings  # type: ignore[no-redef]

# Resolve project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoSec TARA Assistant"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'tara.db'}"
    CHROMA_PERSIST_DIR: str = str(PROJECT_ROOT / "vectorstore")
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
