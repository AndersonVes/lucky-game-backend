from app.core.database import SessionLocal
from app.models.item import Item


def seed_items(db):
    db = SessionLocal()

    try:

        items = [
            Item(
                id=1,
                slug="item1",
                image_url="https://example.com/item1.png",
                model_url="https://example.com/item1.obj",
                name="Item 1",
                rarity=1.0,
            ),
            Item(
                id=2,
                slug="item2",
                image_url="https://example.com/item2.png",
                model_url="https://example.com/item2.obj",
                name="Item 2",
                rarity=0.5,
            ),
            Item(
                id=3,
                slug="item3",
                image_url="https://example.com/item3.png",
                model_url="https://example.com/item3.obj",
                name="Item 3",
                rarity=0.25,
            )
        ]

        

        db.bulk_save_objects(items)
        db.flush()
        db.commit()

        print("✅ Items seeded successfully")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()
    seed_items(db)
