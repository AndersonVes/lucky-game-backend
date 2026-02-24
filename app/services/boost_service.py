from datetime import datetime, timedelta, timezone
from typing import Literal

from requests import Session

from app.config.game_consts import (BOOST_MAX_ACTIVE_MULTIPLIER,
                                    BOOST_MAX_DURATION, BOOST_XP_MULTIPLIERS)
from app.db.models.user import User
from app.db.models.user_boost import UserBoost


def _get_xp_data(reward_slug: Literal["boost_low", "boost_high", "boost_jackpot"]):

    return {
        "multiplier": BOOST_XP_MULTIPLIERS[reward_slug]["multiplier"],
        "duration_seconds": BOOST_XP_MULTIPLIERS[reward_slug]["duration_seconds"],
    }


def grant_boost(db, user, multiplier, duration_seconds, source="card", boost_type=Literal["xp"]):
    now = datetime.now(timezone.utc)

    boost = UserBoost(
        user_id=user.id,
        boost_type=boost_type,
        multiplier=multiplier,
        starts_at=now,
        ends_at=now + timedelta(seconds=duration_seconds),
        source=source,
    )

    db.add(boost)
    return boost


def _get_safe_xp_boost_accumulation_calc(
    db: Session,
    user,
    new_user_boost: UserBoost,
    is_jackpot: bool,
):
    """
    Retorna:
    - False → boost ignorado
    - UserBoost → novo boost criado
    """

    now = datetime.now(timezone.utc)

    # busca último boost ativo (para comparação)
    last_boost = (
        db.query(UserBoost)
        .filter(
            UserBoost.user_id == user.id,
            UserBoost.boost_type == "xp",
            UserBoost.ends_at > now,
        )
        .order_by(UserBoost.ends_at.desc())
        .first()
    )

    # aplica cap de multiplicador
    safe_multiplier = min(new_user_boost.multiplier, BOOST_MAX_ACTIVE_MULTIPLIER)

    # calcula duração segura
    new_user_boost_duration: timedelta = new_user_boost.ends_at - new_user_boost.starts_at
    requested_duration = new_user_boost_duration
    safe_duration = min(requested_duration, BOOST_MAX_DURATION)

    # 1️⃣ Nenhum boost ativo → cria direto
    if not last_boost:
        boost = UserBoost(
            user_id=user.id,
            boost_type="xp",
            multiplier=safe_multiplier,
            starts_at=now,
            ends_at=now + safe_duration,
            source=new_user_boost.source,
        )
        db.add(boost)

        return boost

    # 2️⃣ Boost pior ou igual e NÃO é jackpot → ignora
    if safe_multiplier <= last_boost.multiplier and not is_jackpot:
        return False

    # 3️⃣ Boost melhor → cria novo (substituição lógica)
    if safe_multiplier > last_boost.multiplier:
        boost = UserBoost(
            user_id=user.id,
            boost_type="xp",
            multiplier=safe_multiplier,
            starts_at=now,
            ends_at=now + safe_duration,
            source=new_user_boost.source,
        )
        db.add(boost)

        return boost

    # 4️⃣ Mesmo multiplicador + jackpot → estende criando NOVO
    if safe_multiplier == last_boost.multiplier and is_jackpot:
        remaining = last_boost.ends_at - now
        extended = min(remaining + safe_duration, BOOST_MAX_DURATION)

        boost = UserBoost(
            user_id=user.id,
            boost_type="xp",
            multiplier=safe_multiplier,
            starts_at=now,
            ends_at=now + extended,
            source=new_user_boost.source or "jackpot",
        )
        db.add(boost)

        return boost

    return False


def trigger_boost(
    db: Session,
    user: User,
    reward_slug: Literal["boost_low", "boost_high", "boost_jackpot"],
    boost_type=Literal["xp"],
):
    user_boost = None
    safe_user_boost = None
    if boost_type == "xp":
        xp_multiplier = _get_xp_data(reward_slug)["multiplier"]
        duration_seconds = _get_xp_data(reward_slug)["duration_seconds"]

        user_boost = grant_boost(
            db, user, xp_multiplier, duration_seconds, source="card", boost_type=boost_type
        )

        safe_user_boost = _get_safe_xp_boost_accumulation_calc(
            db, user, user_boost, is_jackpot=reward_slug == "boost_jackpot"
        )
        if not safe_user_boost:
            safe_user_boost = user_boost

    return {
        "reward_data": {
            "multiplier": safe_user_boost.multiplier,
            "duration_seconds": duration_seconds,
        },
        "received_at": safe_user_boost.created_at,
        "consumable": True,
        "type": "boost",
    }


def get_active_boost_multiplier(
    db: Session, user: User, boost_type=Literal["xp", "energy", "coins", "gems"]
):
    active_boost = (
        db.query(UserBoost)
        .filter(UserBoost.user_id == user.id, UserBoost.boost_type == boost_type)
        .order_by(UserBoost.created_at.desc())
        .first()
    )
    if active_boost and active_boost.ends_at > datetime.now(timezone.utc):
        return active_boost


def get_active_boosts(db: Session, user: User):
    boosts = (
        db.query(UserBoost)
        .filter(UserBoost.user_id == user.id, UserBoost.ends_at > datetime.now(timezone.utc))
        .order_by(UserBoost.created_at.desc())
        .all()
    )

    return [
        {
            "boost_type": b.boost_type,
            "multiplier": b.multiplier,
            "starts_at": b.starts_at,
            "ends_at": b.ends_at,
            "source": b.source,
        }
        for b in boosts
    ]
