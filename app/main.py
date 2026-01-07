from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import engine
from app.core.version_middleware import VersionMiddleware
from app.models.base import Base
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB init failed:", e)

    yield

    # Shutdown (se precisar)
    # engine.dispose()


app = FastAPI(
    title="Lucky Game Backend",
    lifespan=lifespan
)

app.add_middleware(VersionMiddleware)
app.include_router(api_router)
