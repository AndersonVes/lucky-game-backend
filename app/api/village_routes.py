from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.village_service import get_building_stage_cost

router = APIRouter(prefix="/village", tags=["village"])

@router.post("")
# TODO: depois, mudar para get e apenas passar o order da vila e retornar o progresso do usuario nela
def new_game(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    building_stage_cost = get_building_stage_cost(db, payload.get("village_id"), payload.get("building_id"), payload.get("stage"))

    building_cost =  {"building_stage_cost": building_stage_cost}    
    
    return building_cost

