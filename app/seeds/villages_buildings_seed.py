from app.models.villages import Villages
from app.models.buildings import Buildings
from app.core.database import SessionLocal


def seed_villages_and_buildings(db):
    db = SessionLocal()

    try:
        # =========================
        # VILLAGES
        # =========================
        villages = [
            Villages(
                id=1,
                name="Vila Inicial",
                order=1,
                building_cost_modifier=1.00,
                coins=1500,
                gems=5,
                xp=200,
                energy=10,
                item_slug="hat_basic",
            ),
            Villages(
                id=2,
                name="Vila Mercantil",
                order=2,
                building_cost_modifier=1.15,
                coins=2500,
                gems=8,
                xp=350,
                energy=12,
                item_slug="outfit_merchant",
            ),
            Villages(
                id=3,
                name="Vila Real",
                order=3,
                building_cost_modifier=1.30,
                coins=4000,
                gems=12,
                xp=550,
                energy=15,
                item_slug="crown_bronze",
            ),
            Villages(
                id=4,
                name="Vila Imperial",
                order=4,
                building_cost_modifier=1.50,
                coins=6500,
                gems=18,
                xp=850,
                energy=18,
                item_slug="armor_imperial",
            ),
            Villages(
                id=5,
                name="Capital Lendária",
                order=5,
                building_cost_modifier=1.75,
                coins=10000,
                gems=25,
                xp=1300,
                energy=22,
                item_slug="relic_legendary",
            ),
        ]

        db.bulk_save_objects(villages)
        db.flush()

        # =========================
        # BUILDINGS
        # =========================
        buildings = [
            # =========================
            # VILA 1 — INICIAL
            # =========================
            Buildings(
                village_id=1,
                name="Casa Simples",
                building_stages=4,
                base_cost=300,
                cost_multiplier=1.25,
            ),
            Buildings(
                village_id=1, name="Poço", building_stages=4, base_cost=450, cost_multiplier=1.28
            ),
            Buildings(
                village_id=1, name="Celeiro", building_stages=4, base_cost=650, cost_multiplier=1.30
            ),
            Buildings(
                village_id=1,
                name="Prefeitura",
                building_stages=4,
                base_cost=900,
                cost_multiplier=1.35,
            ),  # âncora
            # =========================
            # VILA 2 — MERCANTIL
            # =========================
            Buildings(
                village_id=2, name="Mercado", building_stages=4, base_cost=900, cost_multiplier=1.30
            ),
            Buildings(
                village_id=2, name="Moinho", building_stages=4, base_cost=1200, cost_multiplier=1.32
            ),
            Buildings(
                village_id=2,
                name="Oficina",
                building_stages=4,
                base_cost=1500,
                cost_multiplier=1.35,
            ),
            Buildings(
                village_id=2,
                name="Banco Mercantil",
                building_stages=4,
                base_cost=2000,
                cost_multiplier=1.40,
            ),  # âncora
            # =========================
            # VILA 3 — REAL
            # =========================
            Buildings(
                village_id=3,
                name="Guarda Real",
                building_stages=4,
                base_cost=1800,
                cost_multiplier=1.35,
            ),
            Buildings(
                village_id=3,
                name="Jardins Reais",
                building_stages=4,
                base_cost=2400,
                cost_multiplier=1.38,
            ),
            Buildings(
                village_id=3,
                name="Salão do Trono",
                building_stages=4,
                base_cost=3200,
                cost_multiplier=1.42,
            ),
            Buildings(
                village_id=3,
                name="Castelo",
                building_stages=4,
                base_cost=4200,
                cost_multiplier=1.45,
            ),  # âncora
            # =========================
            # VILA 4 — IMPERIAL
            # =========================
            Buildings(
                village_id=4,
                name="Quartel Imperial",
                building_stages=4,
                base_cost=5200,
                cost_multiplier=1.45,
            ),
            Buildings(
                village_id=4,
                name="Aqueduto",
                building_stages=4,
                base_cost=6800,
                cost_multiplier=1.48,
            ),
            Buildings(
                village_id=4,
                name="Câmara Imperial",
                building_stages=4,
                base_cost=8800,
                cost_multiplier=1.52,
            ),
            Buildings(
                village_id=4,
                name="Palácio Imperial",
                building_stages=4,
                base_cost=11500,
                cost_multiplier=1.55,
            ),  # âncora
            # =========================
            # VILA 5 — LENDÁRIA
            # =========================
            Buildings(
                village_id=5,
                name="Santuário Antigo",
                building_stages=4,
                base_cost=14500,
                cost_multiplier=1.55,
            ),
            Buildings(
                village_id=5,
                name="Biblioteca Arcana",
                building_stages=4,
                base_cost=19000,
                cost_multiplier=1.58,
            ),
            Buildings(
                village_id=5,
                name="Forja Lendária",
                building_stages=4,
                base_cost=24500,
                cost_multiplier=1.62,
            ),
            Buildings(
                village_id=5,
                name="Trono dos Deuses",
                building_stages=4,
                base_cost=32000,
                cost_multiplier=1.65,
            ),  # âncora
        ]

        db.bulk_save_objects(buildings)
        db.commit()

        print("✅ Villages and Buildings seeded successfully")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
