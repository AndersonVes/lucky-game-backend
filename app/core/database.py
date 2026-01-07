from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase 
from app.core.config import settings

def get_database_url():
    db_url = ""
    if settings.DB_URL:
        db_url = settings.DB_URL
        db_url = db_url.replace("[DB_PASSWORD]", settings.DB_PASSWORD)
    else:
        ssl = "?sslmode=require" if settings.DB_SSL else ""
        db_url = (
            f"postgresql+psycopg2://"
            f"{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}"
            f"/{settings.DB_NAME}{ssl}"
        )
    return db_url

engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine)


