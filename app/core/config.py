from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import Optional


class Settings(BaseSettings):
    ENV: str = "dev"

    DB_URL: Optional[str] = None

    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_SSL: bool = False

    FB_APP_ID: str
    FB_APP_SECRET: str
    GOOGLE_CLIENT_ID: str

    @computed_field
    @property
    def database_url(self) -> str:
        # 1️⃣ DB_URL explícita (Render / Supabase pooler)
        if self.DB_URL:
            if "[YOUR-PASSWORD]" in self.DB_URL:
                return self.DB_URL.replace("[YOUR-PASSWORD]", self.DB_PASSWORD or "")
            return self.DB_URL

        # 2️⃣ Fallback (local / docker / testes)
        ssl = "?sslmode=require" if self.DB_SSL else ""
        return (
            f"postgresql+psycopg2://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}{ssl}"
        )

    class Config:
        env_file = ".env"
