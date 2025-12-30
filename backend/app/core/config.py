from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]  # repo root (avito-assist/)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "avito-assist"
    ENV: str = "dev"
    BASE_URL: str = "http://localhost:8000"

    DATABASE_URL: str = "sqlite:///./avito_assist.db"

    JWT_SECRET: str
    JWT_EXPIRE_MIN: int = 43200  # 30 days

    CORS_ORIGINS: str = "http://localhost:5173"

    # future
    AVITO_CLIENT_ID: str = ""
    AVITO_CLIENT_SECRET: str = ""
    AVITO_REDIRECT_URI: str = "https://ai-dialog-bot.ru/avito/oauth/callback"
    AVITO_AUTH_URL: str = "https://avito.ru/oauth"
    AVITO_TOKEN_URL: str = "https://api.avito.ru/token"
    AVITO_SCOPES: str = "items:info messenger:read messenger:write short_term_rent:read stats:read user:read"

    PERPLEXITY_API_KEY: str | None = None
    PERPLEXITY_BASE_URL: str = "https://api.perplexity.ai"

    def cors_origins_list(self) -> list[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

    def normalized_database_url(self) -> str:
        # normalize sqlite relative path to repo root to avoid "cwd surprises"
        if self.DATABASE_URL.startswith("sqlite:///./"):
            rel = self.DATABASE_URL.replace("sqlite:///./", "", 1)
            db_path = (BASE_DIR / rel).resolve()
            return f"sqlite:///{db_path.as_posix()}"
        return self.DATABASE_URL

settings = Settings()

def get_settings() -> Settings:
    return settings

