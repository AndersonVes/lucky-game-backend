from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def get_database_url():
    ssl = "?sslmode=require" if settings.DB_SSL else ""
    return (
        f"postgresql+psycopg2://"
        f"{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}"
        f"/{settings.DB_NAME}{ssl}"
    )

engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)
