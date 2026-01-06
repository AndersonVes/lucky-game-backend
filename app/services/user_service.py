from sqlalchemy.orm import Session

from app.models.user import User
from app.models.wallet import Wallet
from app.services.village_service import next_village

INITIAL_BALANCE = 1500


def get_or_create_user(
    db: Session,
    auth_provider: str,
    provider_user_id: str,
    full_name: str,
    email: str | None = None,
    locale: str | None = None,
    picture_url: str | None = None,
):
    user = (
        db.query(User)
        .filter(User.auth_provider == auth_provider, User.provider_user_id == provider_user_id)
        .first()
    )

    if not user:
        try:
            user = User(
                auth_provider=auth_provider,
                provider_user_id=provider_user_id,
                full_name=full_name,
                email=email,
                locale=locale,
                picture_url=picture_url,
            )
            db.add(user)
            db.flush()

            wallet = Wallet(user_id=user.id)
            db.add(wallet)

            next_village(db, village_id=1, user_id=user.id)

            db.commit()
        except Exception:
            db.rollback()
            raise
    else:
        wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    db.commit()
    return user, wallet
