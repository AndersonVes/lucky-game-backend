from sqlalchemy.orm import Session
from app.models.user import User
from app.models.wallet import Wallet

INITIAL_BALANCE = 100

def get_or_create_user_with_wallet(
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
        .filter(
            User.auth_provider == auth_provider,
            User.provider_user_id == provider_user_id
        )
        .first()
    )

    if not user:
        user = User(
            auth_provider=auth_provider,
            provider_user_id=provider_user_id,
            full_name=full_name,
            email=email,
            locale=locale,
            picture_url=picture_url
        )
        db.add(user)
        db.flush()

        wallet = Wallet(
            user_id=user.id
        )
        db.add(wallet)
    else:
        wallet = (
            db.query(Wallet)
            .filter(Wallet.user_id == user.id)
            .first()
        )

    db.commit()
    return user, wallet
