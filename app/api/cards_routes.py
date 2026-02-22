from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.deps import get_db
from app.db.models.user import User
from app.schemas.card_schema import NewGameIn, NewGameOut, RevealCardIn
from app.services.cards_service import cancel_game_uuid, create_or_get_game, draw_card_weighted

router = APIRouter(prefix="/cards", tags=["cards"])


@router.delete("/cancel/{game_uuid}")
def cancel_game(
    game_uuid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    try:
        cancel_game_uuid(db, current_user, game_uuid)
        db.commit()
        return {"message": "Game canceled", "game_uuid": game_uuid}
    except HTTPException as e:
        db.rollback()
        raise


@router.get("/new-game")
def new_game(
    query: NewGameIn = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):# -> NewGameOut:
    try:
        game, items = create_or_get_game(
            db=db,
            user=current_user,
            event_slug=query.event_slug,
        )
        card_data =  {
            "game_uuid": game.id,
            "reward_focus": game.reward_focus,
            "reward_probability": game.reward_probability,
            "event_slug": game.event_slug,
        }
        if items:
            card_data["items"] = items
            card_data.pop("reward_probability", None)
        db.commit()
        return card_data


    except HTTPException as e:
        db.rollback()
        raise


@router.post("/reveal-card")
def reveal_card(
    payload: RevealCardIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        drawn_card = draw_card_weighted(db, current_user, payload.game_uuid)
        db.commit()
        return drawn_card

    except HTTPException as e:
        db.rollback()
        raise
