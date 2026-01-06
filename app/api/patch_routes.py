from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.patch_schema import PatchLatestOut
from app.services.content_patch_service import get_active_patch

router = APIRouter(prefix="/patch", tags=["patch"])

@router.get("/latest")
def get_latest_patch(db: Session = Depends(get_db)) -> PatchLatestOut | None:
    """
    Endpoint público.
    Retorna informações do último patch ativo.
    """
    return get_active_patch(db)