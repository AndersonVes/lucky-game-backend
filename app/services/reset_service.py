from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.user_building import UserBuilding
from app.db.models.user_village import UserVillage
from app.db.models.villages import Villages
from app.services.village_service import (check_village_completion,
                                          get_next_village, next_village)


def reset_available(db: Session, user: User):
    current_village = db.query(Villages).filter(Villages.id == user.actual_village).first()
    next_village = get_next_village(db, current_village)
    if next_village:
        return False

    village_completion = check_village_completion(db, user)
    if village_completion:
        return True

    return False


def do_reset(db: Session, user: User):
    if not reset_available(db, user):
        return False

    user.wallet.coins = 0
    user.wallet.energy = 0

    user.actual_village = 1
    user.resets = user.resets + 1
    db.query(UserBuilding).filter(UserBuilding.user_id == user.id).delete(synchronize_session=False)
    db.query(UserVillage).filter(UserVillage.user_id == user.id).delete(synchronize_session=False)

    next_village(db, user=user)
    return True


def get_reset_coins_multiplier(db: Session, user: User):
    reset_count = user.resets
    return (reset_count + 1) ** 0.4


def get_reset_data(db: Session, user: User):
    multiplier = get_reset_coins_multiplier(db, user)
    return {"resets": user.resets, "coins_multiplier": multiplier}
