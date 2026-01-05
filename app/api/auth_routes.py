from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token
from app.services.auth_facebook import get_facebook_user, validate_facebook_token
from app.services.auth_google import validate_google_token
from app.services.auth_service import get_or_create_user_with_wallet

router = APIRouter(prefix="/login", tags=["auth"])


# ⚠️ DEV ONLY – remover em produção
@router.post("/dev")
def dev_login(db: Session = Depends(get_db)):
    user, wallet = get_or_create_user_with_wallet(
        db=db,
        auth_provider="dev",
        provider_user_id="DEV_USER",
        full_name="Dev User",
        email=None,
        locale="pt-BR",
    )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.full_name},
    }


@router.post("/facebook")
def facebook_login(payload: dict, db: Session = Depends(get_db)):
    access_token = payload.get("access_token")
    if not access_token:
        raise HTTPException(400, "Token ausente")

    if not validate_facebook_token(access_token):
        raise HTTPException(401, "Token inválido")

    fb = get_facebook_user(access_token)

    user, wallet = get_or_create_user_with_wallet(
        db=db,
        auth_provider="facebook",
        provider_user_id=fb["id"],
        full_name=fb["name"],
        email=fb.get("email"),
        picture_url=fb.get("picture", {}).get("data", {}).get("url"),
        locale=None,
    )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.full_name, },
    }


@router.post("/google")
def google_login(payload: dict, db: Session = Depends(get_db)):
    id_token = payload.get("id_token")
    if not id_token:
        raise HTTPException(400, "Token ausente")

    google_user = validate_google_token(id_token)

    user, wallet = get_or_create_user_with_wallet(
        db=db,
        auth_provider="google",
        provider_user_id=google_user["sub"],
        full_name=google_user["name"],
        email=google_user.get("email"),
        picture_url=google_user.get("picture"),
        locale=google_user.get("locale"),
    )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.full_name, },
    }
