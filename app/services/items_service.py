from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.item import Item
from app.db.models.user import User
from app.db.models.user_item import UserItem


def user_has_item(db: Session, user: User, item: Item | str) -> bool:
    if isinstance(item, str):
        item = db.query(Item).filter(Item.slug == item).scalar()

    if not item:
        raise HTTPException(400, "Item not found")

    user_item = (
        db.query(UserItem)
        .filter(UserItem.user_id == user.id, UserItem.item_id == item.id, UserItem.stack_size > 0)
        .scalar()
    )

    return user_item is not None


def add_item(
    db: Session, user: User, item: Item | str, stack_size: int = 1, no_duplicates: bool = True
) -> UserItem:
    if isinstance(item, str):
        item = db.query(Item).filter(Item.slug == item).scalar()
    if no_duplicates and user_has_item(db, user, item):
        raise HTTPException(400, "User already has item")
    user_item = UserItem(user_id=user.id, item_id=item.id, stack_size=stack_size)
    db.add(user_item)

    return {
        "reward_data": {
            "item_slug": item.slug,
            "stack_size": user_item.stack_size,
        },
        "consumable": False,
        "received_at": user_item.created_at,
        "type": "item",
    }

   