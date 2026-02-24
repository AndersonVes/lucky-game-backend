from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy.orm import Session

from app.config.game_consts import WALLET_MAX_ENERGY_COUNT, WALLET_MAX_ENERGY_SECONDS
from app.db.models.user import User
from app.db.models.villages import Villages
from app.db.models.wallet import Wallet
from app.db.models.wallet_transaction import WalletTransaction
from app.helpers.calc_helper import get_building_cost_modifier
from app.helpers.time_helper import utcnow
from app.services.boost_service import get_active_boost_multiplier
from app.services.reset_service import get_reset_coins_multiplier
from app.services.building_service import get_building_stage_cost_by_cost_rank


def _get_coins_from_reward_slug(
    db: Session,
    user: User,
    reward_slug: Literal["coins_low", "coins_high", "coins_jackpot"],
) -> int:

    cheapest_cost = get_building_stage_cost_by_cost_rank(db, user)

    if not cheapest_cost:
        return 0

    village = db.query(Villages).get(user.actual_village)

    building_cost_modifier = get_building_cost_modifier(village.id)

    raw_cost_without_modifier = round(cheapest_cost / building_cost_modifier)

    base_earn = raw_cost_without_modifier * 0.6

    if "low" in reward_slug:
        return int(base_earn * 0.3)
    elif "high" in reward_slug:
        return int(base_earn * 0.5)
    elif "jackpot" in reward_slug:
        return int(base_earn * 0.9)

    return 0


def _get_energy_from_reward_slug(
    db: Session, user: User, reward_slug: Literal["energy_low", "energy_high"]
) -> int:

    if "low" in reward_slug:
        return 1
    elif "high" in reward_slug:
        return 3


def add_currency(
    db: Session,
    user: User,
    currency: Literal["xp", "coins", "gems", "energy", "tickets"] | None = None,
    amount: int = None,
    reward_slug: str = None,
):

    # validations
    if not amount and not reward_slug:
        if amount == 0:
            return
        raise Exception("Amount or reward_slug must be provided")
    if amount and reward_slug:
        raise Exception("Amount and reward_slug cannot be provided together")

    if amount and not currency:
        raise Exception("Currency must be provided if amount is provided")
    # ---
    multiplier = 1

    active_boost = get_active_boost_multiplier(db, user, boost_type=currency)
    if active_boost:
        multiplier = active_boost.multiplier

    allowed_currencies = {"coins", "xp", "gems", "energy", "tickets"}

    if reward_slug:
        prefix = reward_slug.split("_", 1)[0]

        if prefix not in allowed_currencies:
            raise ValueError(f"Invalid reward_slug: {reward_slug}")

        currency = prefix

        if prefix == "coins":
            amount = _get_coins_from_reward_slug(db=db, user=user, reward_slug=reward_slug)
        elif prefix == "energy":
            amount = _get_energy_from_reward_slug(db=db, user=user, reward_slug=reward_slug)
    if currency == "coins":
        reset_multiplier = get_reset_coins_multiplier(db, user)
        amount = amount * multiplier * reset_multiplier

    if currency == "energy":
        amount = min(amount, WALLET_MAX_ENERGY_COUNT)

    amount = int(amount)

    setattr(user.wallet, currency, getattr(user.wallet, currency) + (amount))

    wallet_transaction = WalletTransaction(
        user_id=user.id,
        type="earn",
        amount=amount,
        balance_after=getattr(user.wallet, currency),
        currency=currency,
    )
    db.add(wallet_transaction)

    return {
        "reward_data": {"amount": amount, "currency": currency, "multiplier": multiplier},
        "received_at": user.wallet.updated_at,
        "consumable": True,
        "type": "currency",
    }


def deduce_currency(
    db: Session,
    user: User,
    currency: Literal["xp", "coins", "gems", "energy", "tickets"],
    amount: int,
):
    amount = int(amount)
    setattr(user.wallet, currency, getattr(user.wallet, currency) - (amount))
    wallet_transaction = WalletTransaction(
        user_id=user.id,
        type="spend",
        amount=amount,
        balance_after=getattr(user.wallet, currency),
        currency=currency,
    )
    db.add(wallet_transaction)


def get_wallet_by_user(db: Session, user: User) -> Wallet:
    return


def _calculate_energy_gain(last_energy_at: datetime) -> int:
    elapsed_seconds = (utcnow() - last_energy_at).total_seconds()
    energy_gain = max(0, int(elapsed_seconds // WALLET_MAX_ENERGY_SECONDS))
    return energy_gain


def apply_energy_regen(db: Session, user: User) -> None:
    gained = _calculate_energy_gain(user.wallet.last_energy_at)

    if gained <= 0:
        return

    missing = WALLET_MAX_ENERGY_COUNT - user.wallet.energy
    to_add = min(gained, missing)

    if to_add <= 0:
        return

    add_currency(db, user, "energy", amount=to_add)

    user.wallet.last_energy_at = utcnow()


def get_energy_data(db: Session, user: User) -> dict:
    apply_energy_regen(db, user)

    now = utcnow()
    last_energy_at = user.wallet.last_energy_at

    elapsed = (now - last_energy_at).total_seconds()
    seconds_to_next = max(0, WALLET_MAX_ENERGY_SECONDS - elapsed)

    will_complete_at = (
        last_energy_at + timedelta(seconds=WALLET_MAX_ENERGY_SECONDS)
        if user.wallet.energy < WALLET_MAX_ENERGY_COUNT
        else None
    )

    return {
        "current_enernegy_count": user.wallet.energy,
        "next_enernegy_count": (
            (user.wallet.energy + 1)
            if user.wallet.energy < WALLET_MAX_ENERGY_COUNT
            else WALLET_MAX_ENERGY_COUNT
        ),
        "last_energy_at": last_energy_at,
        "will_complete_at": will_complete_at,
        "max": user.wallet.energy >= WALLET_MAX_ENERGY_COUNT,
    }
