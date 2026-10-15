"""
Unit tests for application configuration settings.
"""
from pathlib import Path
from app.core.config import settings, PROJECT_ROOT


def test_settings_project_name():
    assert settings.PROJECT_NAME == "AutoSec TARA Assistant"


def test_settings_api_prefix():
    assert settings.API_V1_STR == "/api/v1"


def test_settings_database_url():
    assert "sqlite:///" in settings.DATABASE_URL
    assert "tara.db" in settings.DATABASE_URL


def test_settings_chroma_persist_dir():
    assert settings.CHROMA_PERSIST_DIR is not None
    assert "vectorstore" in settings.CHROMA_PERSIST_DIR


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()
    assert (PROJECT_ROOT / "app").exists()
