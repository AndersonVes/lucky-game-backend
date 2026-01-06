from app.core.database import SessionLocal
from app.seeds.villages_buildings_seed import seed_villages_and_buildings
from app.seeds.content_patches_seed import seed_patches

def run_seeds():
    db = SessionLocal()
    try:
        seed_villages_and_buildings(db)
        seed_patches(db)
        print("✅ All seeds executed successfully")
    finally:
        db.close()

if __name__ == "__main__":
    run_seeds()

# python -m app.seeds.run
# to run separately: 
# python -m app.seeds.villages_buildings_seed.run()
# python -m app.seeds.content_patches_seed
# ...
