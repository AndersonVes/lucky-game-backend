from app.core.database import SessionLocal
from app.seeds.villages_buildings_seed import seed_villages_and_buildings

def run_seeds():
    db = SessionLocal()
    try:
        seed_villages_and_buildings(db)
    finally:
        db.close()

if __name__ == "__main__":
    run_seeds()

# python -m app.seeds.run
