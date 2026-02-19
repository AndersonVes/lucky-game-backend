from fastapi import APIRouter
from requests import patch

from app.api.cards_routes import router as cards_router
from app.api.auth_routes import router as auth_router
from app.api.patch_routes import router as patch_router
from app.api.village_routes import router as village_router
from app.api.user_routes import router as user_router
from app.api.system_routes import router as system_router
from app.api.items_routes import router as items_router
from app.api.dev_routes import router as dev_router
from app.api.events_routes import router as events_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(cards_router)
api_router.include_router(patch_router)
api_router.include_router(village_router)
api_router.include_router(user_router)
api_router.include_router(system_router)
api_router.include_router(items_router)
api_router.include_router(dev_router)
api_router.include_router(events_router)