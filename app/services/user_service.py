from datetime import datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.config.game_consts import DAILY_REWARD
from app.db.models.user import User
from app.db.models.wallet import Wallet
from app.helpers.time_helper import utcnow
from app.services.village_service import next_village
from app.services.wallet_service import add_currency


def grant_daily_reward(user: User, day: int):
    # TODO notifiação com popup
    reward = next(item for item in DAILY_REWARD if item["day"] == day)

    for currency, amount in reward.items():
        if currency == "day":
            continue

        if amount and amount > 0:
            add_currency(
                db=user._sa_instance_state.session,
                user=user,
                currency=currency,
                amount=amount,
            )


def process_daily_login(db: Session, user: User):
    now = utcnow()

    if not DAILY_REWARD:
        raise Exception("DAILY_REWARD configuration is empty")

    # Descobre dinamicamente menor e maior dia configurado
    available_days = sorted(item["day"] for item in DAILY_REWARD)
    min_day = available_days[0]
    max_day = available_days[-1]

    last_reward_at = user.last_daily_reward_won_at

    # PRIMEIRO LOGIN DA VIDA
    if not last_reward_at:
        user.consecutive_days_logged_in = min_day
        user.last_daily_reward_won_at = now

        grant_daily_reward(user, min_day)
        return min_day

    # --- NORMALIZAÇÃO FORÇADA PARA UTC ---
    now_utc = now.astimezone(timezone.utc)
    last_reward_at_utc = last_reward_at.astimezone(timezone.utc)

    # Calcula diferença em dias por data (ignora hora)
    days_difference = (now_utc.date() - last_reward_at_utc.date()).days

    # Já ganhou hoje
    if days_difference == 0:
        tomorrow_date = now_utc.date() + timedelta(days=1)
        next_claim_at = datetime.combine(tomorrow_date, time.min, tzinfo=timezone.utc)

        seconds_remaining = max(0, int((next_claim_at - now_utc).total_seconds()))

        return None

    # Login no dia seguinte → mantém streak
    if days_difference == 1:
        new_streak = user.consecutive_days_logged_in + 1
    else:
        # Perdeu streak
        new_streak = min_day

    # Garante limites válidos dinamicamente
    if new_streak > max_day:
        new_streak = min_day

    # Atualiza usuário
    user.consecutive_days_logged_in = new_streak
    user.last_daily_reward_won_at = now_utc

    # Concede recompensa
    grant_daily_reward(user, new_streak)

    return new_streak


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
        user = User(
            auth_provider=auth_provider,
            provider_user_id=provider_user_id,
            full_name=full_name,
            email=email,
            locale=locale,
            picture_url=picture_url,
        )
        db.add(user)

        wallet = Wallet(user_id=user.id)
        db.add(wallet)

        user.wallet = wallet
        db.flush()

        next_village(db, user=user)

    else:
        wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    process_daily_login(db, user)

    return user, wallet


def delete_current_user(db: Session, user: User):
    db.delete(user)
