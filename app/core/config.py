from pydantic_settings import BaseSettings

from app.services.auth_google import GOOGLE_CLIENT_ID

class Settings(BaseSettings):
    ENV: str = "dev"
    
    DB_URL: str
    
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSL: bool = False

    FB_APP_ID: str
    FB_APP_SECRET: str

    GOOGLE_CLIENT_ID: str

    class Config:
        env_file = ".env"

settings = Settings()
