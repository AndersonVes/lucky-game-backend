from fastapi import FastAPI
from app.core.database import engine
from app.models.base import Base
from app.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
