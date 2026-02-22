import random
from datetime import datetime, timezone
import re
from typing import Literal
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.api.events_routes import active_events
from app.config.game_consts import (
    CARDS_ALLOWED_REWARD_FOCUS,
    CARDS_ALTERNATIVE_REWARDS_PROBABILITIES_JACKPOT,
    CARDS_BASE_PROBABILITIES,
    CARDS_MIN_PROBABILITIES,
)
from app.db.models.building import Building
from app.db.models.card_hash import CardHash
from app.db.models.event import Event
from app.db.models.item import Item
from app.db.models.user import User
from app.db.models.user_building import UserBuilding
from app.services.boost_service import trigger_boost
from app.services.events_service import event_is_active, get_active_events
from app.services.items_service import add_item, user_has_item
from app.services.reset_service import reset_available
from app.services.wallet_service import add_currency, apply_energy_regen, deduce_currency


def sort_card(db: Session, user: User, game_data, card_hash):
    return


def get_coins_reward(
    db: Session, user: User, reward_focus: Literal["coins_low", "coins_high", "jackpot"]
):
    user_buildings = (
        db.query(UserBuilding).filter(UserBuilding.user_id == user.id).join(Building).all()
    )
    return user_buildings


def get_game_data(db: Session, user: User, game_uuid: UUID):
    card_data = (
        db.query(CardHash).filter(CardHash.user_id == user.id, CardHash.id == game_uuid).first()
    )

    if card_data is None:
        raise HTTPException(status_code=404, detail="Card not found")

    if card_data.used:
        raise HTTPException(status_code=400, detail="Card already used")

    if card_data.canceled:
        raise HTTPException(status_code=400, detail="Card canceled")

    return {
        "reward_focus": "event_items" if card_data.item_slug else "coins_jackpot",
        "item_slug": card_data.item_slug,
    }


# HASH


def cancel_game_uuid(db: Session, user: User, game_uuid: UUID):
    db.query(CardHash).filter(CardHash.user_id == user.id, CardHash.id == game_uuid).update(
        {"canceled": True}
    )
    return


def _create_game(
    db: Session,
    user: User,
    reward_focus: str,
    event_slug: str | None,
) -> CardHash:
    secondary_reward_probability = None
    if reward_focus == "coins_jackpot":
        probability = _get_reward_probability_jackpot(
            user=user,
            reward_focus=reward_focus,
        )
    elif reward_focus == "event_items":
        probability, secondary_reward_probability = _get_reward_probability_event(
            db=db,
            user=user,
            event=db.query(Event).filter(Event.slug == event_slug).first(),
        )

    card = CardHash(
        id=uuid4(),
        user_id=user.id,
        reward_focus=reward_focus,
        reward_probability=probability,
        secondary_reward_probability=secondary_reward_probability,
        event_slug=event_slug,
    )

    db.add(card)

    return card


def _search_active_card_hash(
    db: Session, user_id: int, reward_focus: str, event_slug: str | None
) -> CardHash | None:
    return (
        db.query(CardHash)
        .filter(
            CardHash.user_id == user_id,
            CardHash.reward_focus == reward_focus,
            CardHash.event_slug == event_slug,
            CardHash.used.is_(False),
            CardHash.canceled.is_(False),
        )
        .first()
    )


def get_valid_event_items(db,user, event):
    slugs = [event.target_item_slug]

    if event.secondary_target_item_slug:
        slugs.append(event.secondary_target_item_slug)

    items = db.query(Item).filter(Item.slug.in_(slugs)).all()
    items_by_slug = {item.slug: item for item in items}

    missing = [slug for slug in slugs if slug not in items_by_slug]
    if missing:
        raise HTTPException(404, f"Item(s) not found: {', '.join(missing)}")

    if not any(item.drawn_available for item in items_by_slug.values()):
        raise HTTPException(400, "Item(s) not available")
    
    has_all_items = all(user_has_item(db, user, item=slug) for slug in slugs)
    if has_all_items:
        raise HTTPException(400, "User already has all event items")

    return {
        item.slug: {
            "id": item.id,
            "slug": item.slug,
            "name": item.name,
            "rarity": item.rarity,
            "drawn_available": item.drawn_available,
        }
        for item in items_by_slug.values()
    }


def _get_reward_probability_event(
    db: Session,
    user: User,
    event: Event,
) -> float:
    """
    Retorna probabilidade FINAL em %
    Ex: 0.01 = 1%
    """
    items = get_valid_event_items(db, user, event)

    reward_probability = 0.2
    second_item_probability = 0.2 if event.secondary_target_item_slug else None

    # arredondamento seguro (ex: 0.0075 → 0.75%)
    return round(reward_probability, 4), (
        round(second_item_probability, 4) if second_item_probability else None
    )


def _get_reward_probability_jackpot(
    user: User,
    reward_focus: str,
) -> float:
    """
    Retorna probabilidade FINAL em %
    Ex: 0.01 = 1%
    """

    if reward_focus not in CARDS_ALLOWED_REWARD_FOCUS:
        raise HTTPException(400, "Invalid reward focus")

    base = CARDS_BASE_PROBABILITIES[reward_focus]
    probability = base

    # --------------------
    # JACKPOT COOLDOWN (sem bloqueio)
    # --------------------
    if reward_focus == "coins_jackpot" and user.last_jackpot_at:
        now = datetime.now(timezone.utc)
        minutes = (now - user.last_jackpot_at).total_seconds() / 60

        if minutes < 30:
            # penalidade máxima = base - mínimo
            max_penalty = base - CARDS_MIN_PROBABILITIES["coins_jackpot"]

            # decaimento linear
            cooldown_penalty = max_penalty * ((30 - minutes) / 30)
            probability -= cooldown_penalty

    # --------------------
    # Garantia de mínimo
    # --------------------
    probability = max(probability, CARDS_MIN_PROBABILITIES[reward_focus])

    # arredondamento seguro (ex: 0.0075 → 0.75%)
    return round(probability, 4)


def validate_event_items(db, event):
    slugs = [event.target_item_slug]

    if event.secondary_target_item_slug:
        slugs.append(event.secondary_target_item_slug)

    items = db.query(Item).filter(Item.slug.in_(slugs)).all()

    if len(items) != len(slugs):
        raise HTTPException(404, "Item(s) not found")

    if not any(item.drawn_available for item in items):
        raise HTTPException(400, "Item(s) not available")


def create_or_get_game(
    db: Session,
    user: User,
    event_slug: str | None,
):
    """
    Regra:
    - event_slug != None → jogo de ITEM
    - event_slug == None → jogo de JACKPOT
    """
    if reset_available(db, user):
        raise HTTPException(400, "Reset available")
    items = None
    if event_slug:
        reward_focus = "event_items"

        event = db.query(Event).filter(Event.slug == event_slug).first()

        if not event:
            raise HTTPException(404, "Event not found")
        
        active_events = get_active_events(db, user)
        if event.slug not in [e.slug for e in active_events]:
            raise HTTPException(400, "Event not active")

        spin_currency = event.spin_currency
        cost_per_spin = event.cost_per_spin

        items = get_valid_event_items(db, user, event)
        print(items)

    else:
        reward_focus = "coins_jackpot"
        apply_energy_regen(db, user)
        spin_currency = "energy"
        cost_per_spin = 1

    if getattr(user.wallet, spin_currency) < cost_per_spin:
        raise HTTPException(status_code=400, detail=f"Not enough {spin_currency}")

    deduce_currency(db, user, spin_currency, cost_per_spin)

    card = _search_active_card_hash(
        db=db, user_id=user.id, reward_focus=reward_focus, event_slug=event_slug
    )

    if not card:
        card = _create_game(
            db=db,
            user=user,
            reward_focus=reward_focus,
            event_slug=event_slug,
        )

    
    
    return card, items





def _draw_weighted(reward_focus: Literal["coins_jackpot", "event_items"], secondary=False):
    if reward_focus == "coins_jackpot":
        total = sum(CARDS_ALTERNATIVE_REWARDS_PROBABILITIES_JACKPOT["rewards"].values())

        if not abs(total - CARDS_ALTERNATIVE_REWARDS_PROBABILITIES_JACKPOT["value_sum"]) < 1e-6:
            raise ValueError(f"Probabilities must sum to 1.0, got {total}")

        rewards = list(CARDS_ALTERNATIVE_REWARDS_PROBABILITIES_JACKPOT["rewards"].keys())
        weights = list(CARDS_ALTERNATIVE_REWARDS_PROBABILITIES_JACKPOT["rewards"].values())

        return random.choices(rewards, weights=weights, k=1)[0]
    else:
        if secondary:
            return random.choices(["energy_high", "energy_low"], weights=[1, 2], k=1)[0]
        else:
            return random.choice(["energy_low", "energy_high"])


def draw_card_weighted(
    db: Session,
    user: User,
    game_uuid: UUID,
):
    if reset_available(db, user):
        raise HTTPException(400, "Reset available")

    card_hash = db.query(CardHash).filter(CardHash.id == game_uuid).first()

    if not card_hash:
        raise HTTPException(404, "Card not found")

    if card_hash.used:
        raise HTTPException(400, "Card already used")

    if card_hash.canceled:
        raise HTTPException(400, "Card canceled")

    focus_reward = card_hash.reward_focus

    focus_reward_probability = card_hash.reward_probability
    secondary_reward_probability = card_hash.secondary_reward_probability

    result = None
    is_coins_jackpot = False

    if focus_reward == "coins_jackpot":
        won_focus_reward = random.random() < focus_reward_probability

        if won_focus_reward:
            result = add_currency(db, user, currency="coins", reward_slug="coins_jackpot")
            result["reward_data"]["is_jackpot"] = True

        else:
            alternative_reward = _draw_weighted("coins_jackpot")
            reward_type = alternative_reward.split("_", 1)[0]

            if reward_type == "boost":
                result = trigger_boost(db, user, alternative_reward, boost_type="xp")
            else:
                result = add_currency(db, user, reward_type, alternative_reward)
                if reward_type == "coins":
                    result["reward_data"]["is_jackpot"] = False

    elif focus_reward == "event_items":
        chance = random.random()
        if chance < focus_reward_probability:
            result = add_item(db, user, card_hash.event.target_item_slug)
        elif (
            secondary_reward_probability
            and chance < focus_reward_probability + secondary_reward_probability
        ):
            result = add_item(db, user, card_hash.event.secondary_target_item_slug)
        else:
            alternative_reward = _draw_weighted(
                "event_items", secondary=True if secondary_reward_probability else False
            )

            result = add_currency(db, user, currency="energy", reward_slug=alternative_reward)

    # card_hash.used = True #TODO

    return result
