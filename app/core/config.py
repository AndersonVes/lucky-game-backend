from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    ENV: str = "dev"

    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSL: bool = False

    FB_APP_ID: str
    FB_APP_SECRET: str
    GOOGLE_CLIENT_ID: str

    @computed_field
    @property
    def DB_URL(self) -> str:
        ssl = "?sslmode=require" if self.DB_SSL else ""
        return (
            f"postgresql+psycopg2://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}{ssl}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
