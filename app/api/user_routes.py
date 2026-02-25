from app.config.game_consts import DAILY_REWARD

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.deps import get_db
from app.db.models.user import User
from app.helpers.time_helper import utcnow
from app.schemas.user_schema import EnergyDataOut, MultipliersOut, UserOut
from app.services.boost_service import get_active_boosts
from app.services.reset_service import get_reset_data
from app.services.user_service import delete_current_user
from app.services.wallet_service import get_energy_data
from app.services.xp_service import get_xp_data

router = APIRouter(prefix="/user", tags=["user"])


@router.get("")
def get_user(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> UserOut:
    xp_data = get_xp_data(db, current_user)
    return {
        "full_name": current_user.full_name,
        "rank": current_user.rank,
        "email": current_user.email,
        "locale": current_user.locale,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "wallet": {
            "coins": current_user.wallet.coins,
            "gems": current_user.wallet.gems,
            "energy": current_user.wallet.energy,
        },
        "xp": xp_data,
        "utcnow": utcnow(),
        "resets": current_user.resets,
    }


@router.get("/energy")
def get_energy(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> EnergyDataOut:
    try:
        energy_data = get_energy_data(db, current_user)
        db.commit()
        return energy_data
    except HTTPException as e:
        db.rollback()
        raise


@router.get("/multipliers")
def get_multipliers(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> MultipliersOut:
    try:
        boosts_data = get_active_boosts(db, current_user)
        reset_data = get_reset_data(db, current_user)
        db.commit()
        return {"resets": reset_data, "boosts": boosts_data}
    except HTTPException as e:
        db.rollback()
        raise


@router.delete("")
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        delete_current_user(db, current_user)
        db.commit()
        return {"message": "User deleted"}
    except HTTPException as e:
        db.rollback()
        raise

@router.get("/daily-reward")
def get_daily_reward():
    return DAILY_REWARD
