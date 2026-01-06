from fastapi import APIRouter
from requests import patch

from app.api.cards_routes import router as cards_router
from app.api.auth_routes import router as auth_router
from app.api.wallet_routes import router as wallet_router
from app.api.patch_routes import router as patch_router
from app.api.village_routes import router as village_router
from app.api.user_routes import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(wallet_router)
api_router.include_router(cards_router)
api_router.include_router(patch_router)
api_router.include_router(village_router)
api_router.include_router(user_router)