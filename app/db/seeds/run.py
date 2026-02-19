import os

from app.core.database import SessionLocal
from app.db.seeds.content_patches_seed import seed_patches
from app.db.seeds.events_seed import seed_events
from app.db.seeds.items_seed import seed_items
from app.db.seeds.villages_buildings_seed import seed_villages_and_buildings


def run_seeds():
    db = SessionLocal()
    try:
        seed_items(db)
        seed_villages_and_buildings(db)
        seed_patches(db)
        seed_events(db)

        print("✅✅✅ All seeds executed successfully")
    finally:
        db.close()


def run_seeds_if_enabled():
    """
    Runs seeds only if RUN_SEEDS=true is set in the environment.
    Safe to be called during app startup.
    """
    if os.getenv("RUN_SEEDS", "").lower() == "true":
        print("🌱 RUN_SEEDS enabled, running seeds...")
        run_seeds()
    else:
        print("⏭️ RUN_SEEDS disabled, skipping seeds")


if __name__ == "__main__":
    # Allows manual execution:
    # python -m app.db.seeds.run
    run_seeds()
