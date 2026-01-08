from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.village_schema import VillageOut
from app.services.village_service import get_actual_village

router = APIRouter(prefix="/village", tags=["village"])


@router.get("")
def get_village(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> VillageOut:

    return get_actual_village(db, current_user)
