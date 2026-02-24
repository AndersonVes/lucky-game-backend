from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "dev"

    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_SSL: bool = False

    DB_URL: str | None = None

    FB_APP_ID: str
    FB_APP_SECRET: str
    GOOGLE_CLIENT_ID: str

    @computed_field
    @property
    def database_url(self) -> str:
        if self.DB_URL:
            return self.DB_URL.replace(
                "[YOUR-PASSWORD]",
                self.DB_PASSWORD or ""
            )

        ssl = "?sslmode=require" if self.DB_SSL else ""
        return (
            f"postgresql+psycopg2://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}{ssl}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
