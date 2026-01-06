from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/user", tags=["user"])

@router.get("")
def get_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "locale": current_user.locale,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "wallet": {
            "coins": current_user.wallet.coins,
            "gems": current_user.wallet.gems,
            "energy": current_user.wallet.energy,
        } if current_user.wallet else None
    }