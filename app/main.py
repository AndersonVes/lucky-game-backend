from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.database import engine  # ou onde o engine está hoje
from app.core.version_middleware import VersionMiddleware
from app.models.base import Base
import app.models
from app.db.seeds.run import run_seeds_if_enabled

# TODO separar branchs dev,staging e main. só upar staging e main com pr
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)  # 👈 AQUI
        run_seeds_if_enabled()
    except Exception as e:
        print("Startup failed:", e)

    yield


app = FastAPI(
    title="Lucky Game Backend",
    lifespan=lifespan
)

app.add_middleware(VersionMiddleware)
app.include_router(api_router)
