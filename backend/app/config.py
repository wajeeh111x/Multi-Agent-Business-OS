from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SETTINGS
# ============================================================

class Settings(BaseSettings):

    DATABASE_URL: str

    SECRET_KEY: str

    OLLAMA_MODEL: str = "qwen3:4b"

    OLLAMA_TIMEOUT: int = 60

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


# ============================================================
# SETTINGS INSTANCE
# ============================================================

settings = Settings()