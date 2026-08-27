from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    app_name: str = "EduPay Link"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://edupay:change-me@localhost:5432/edupay"
    jwt_secret: str = "dev-only-secret-change-before-production"
    admin_email: str = "admin@edupay.link"
    admin_password: str = "change-me-now"
    frontend_url: str = "http://localhost:3000"
    bank_name: str = "신한은행"
    bank_account: str = "110-000-000000"
    bank_holder: str = "에듀페이링크"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "EduPay Link <noreply@edupay.link>"

@lru_cache
def get_settings(): return Settings()
settings = get_settings()
