from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import User
from app.services.auth_facebook import (
    validate_facebook_token,
    get_facebook_user,
)
from app.services.wallet_service import add_coins

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login/dev")
def dev_login(db: Session = Depends(get_db)):
    user = User(
        facebook_id="DEV_USER",
        name="Dev User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id}

@router.post("/login/facebook")
def login(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("access_token")
    if not token:
        raise HTTPException(400, "Token ausente")

    if not validate_facebook_token(token):
        raise HTTPException(401, "Token inválido")

    fb = get_facebook_user(token)

    user = db.query(User).filter_by(facebook_id=fb["id"]).first()
    if not user:
        user = User(
            facebook_id=fb["id"],
            name=fb["name"],
            coins=100
        )
        db.add(user)

    db.commit()
    return {"id": user.id, "coins": user.coins}
