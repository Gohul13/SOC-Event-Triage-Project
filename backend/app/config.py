from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_key: str = "dev-api-key-change-in-production"
    database_url: str = "sqlite:///./data/events.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    model_path: str = "../ml/models/log_classifier.joblib"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def resolved_model_path(self, backend_root: Path) -> Path:
        p = Path(self.model_path)
        if p.is_absolute():
            return p
        return (backend_root / p).resolve()


settings = Settings()
