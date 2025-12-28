from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSL: bool = False

    FB_APP_ID: str
    FB_APP_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()
