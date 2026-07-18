from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Prototipo de chequeo de dominios"
    app_env: str = "development"
    frontend_origins: str = "http://localhost:5173"
    scan_max_seconds: float = 180.0
    port_scan_timeout_seconds: float = 0.25
    port_scan_concurrency: int = 200
    rate_limit_scans: int = 5
    rate_limit_window_seconds: int = 300
    database_url: str = "sqlite+aiosqlite:///../data/domaincheck.db"
    history_retention_days: int = 90
    subdomain_result_limit: int = 100
    virustotal_api_key: str | None = None
    securitytrails_api_key: str | None = None
    google_safe_browsing_api_key: str | None = None
    mdn_observatory_enabled: bool = False

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
