from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.database import SessionLocal
from app.services.content_patch_service import get_active_patch
from packaging.version import Version, InvalidVersion


PUBLIC_PATHS = (
    "/patch/latest",
    "/login",
    "/docs",
    "/openapi.json",
    "/redoc",
)


class VersionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 🔓 endpoints públicos ignoram validação
        if path.startswith(PUBLIC_PATHS):
            return await call_next(request)
        
        db = SessionLocal()
        try:
            patch = get_active_patch(db)
        finally:
            db.close()

        # Se não existe patch ativo, deixa passar
        if not patch:
            return await call_next(request)
        
        if patch["mandatory"]:
            # Validação do header X-App-Version
            app_version = request.headers.get("X-App-Version")
            if not app_version:
                return JSONResponse(
                    status_code=401,
                    content={"error": "APP_VERSION_REQUIRED"},
                )

            try:
                client_version = Version(app_version)
            except InvalidVersion:
                return JSONResponse(
                    status_code=400,
                    content={"error": "INVALID_APP_VERSION"},
                )

            

            try:
                min_version = Version(patch["appVersionMin"])
            except InvalidVersion:
                return await call_next(request)

            if client_version < min_version:
                return JSONResponse(
                    status_code=426,
                    content={
                        "error": "APP_UPDATE_REQUIRED",
                        "appVersionMin": patch["appVersionMin"],
                        "latestPatch":"/patch/latest    "
                    },
                )
            
            # content version
            
            content_version = request.headers.get("X-Content-Version")
            if not content_version:
                return JSONResponse(
                    status_code=401,
                    content={"error": "CONTENT_VERSION_REQUIRED"},
                )
            
            try:
                Version(content_version)
            except InvalidVersion:
                return JSONResponse(
                    status_code=400,
                    content={"error": "INVALID_CONTENT_VERSION"},
                )

            if Version(content_version) < Version(patch["contentVersion"]):
                return JSONResponse(
                    status_code=426,
                    content={
                        "error": "CONTENT_UPDATE_REQUIRED",
                        "contentVersion": patch["contentVersion"], "latestPatch":"/patch/latest ",
                        "contentact":content_version
                    },
                )

        return await call_next(request)
