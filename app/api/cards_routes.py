from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.card_schema import CardOut
from app.services.cards_service import generate_new_game_cards

router = APIRouter(prefix="/cards", tags=["cards"])

@router.post("/new-game")
def new_game(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # TODO: logica para gerar cartas baseado no usuario, historico, etc.
    # TODO: criar um objeto de card para retornar ao invés de strings simples
    cards_array = generate_new_game_cards(
        user=current_user,
        rare_item=payload.get("rare_item", None),
        total_cards=payload.get("total_cards", 8)
    )

    new_game =  {"cards": cards_array}

    if payload.get("rare_item", None):
        new_game["rare_item_probability"] = 1 / payload.get("total_cards", 8)
    
    return new_game

@router.post("/reveal-card")
def reveal_card(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CardOut:
    card = payload.get("revealed_card")

    if not card:
        raise HTTPException(400, "Card is required")
    
    # TODO: add to inventory/wallet
    return {"revealed_card": card}