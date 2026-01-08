from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user_schema import UserOut

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/health")
def health():
    return {"ok": True}
