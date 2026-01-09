from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.card_schema import CardOut
from app.services.cards_service import (
    get_rare_item_probability,
    get_game_hash,
    get_jackpot_probability,
)

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("/new-game")
def new_game(
    goal_card: Optional[str] = Query(
        None
    ),  # goal_card eh o item_slug por enquanto, mas pode ser adicionado mais coisas
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: logica para gerar cartas baseado no usuario, historico, etc.
    # TODO evitar ganhar item repetido

    new_game = {
        "hash": get_game_hash(current_user, goal_card),
        "rare_item_probability": (
            0 if not goal_card else get_rare_item_probability(current_user, goal_card)
        ),
        "jackpot_probability": (
            0 if goal_card else get_jackpot_probability(current_user, goal_card)
        ),
    }

    return new_game


@router.post("/reveal-card")
def reveal_card(
    payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> CardOut:
    card = payload.get("revealed_card")

    if not card:
        raise HTTPException(400, "Card is required")

    # TODO: add to inventory/wallet
    # TODO evitar ganhar item repetido
    return {"revealed_card": card}
