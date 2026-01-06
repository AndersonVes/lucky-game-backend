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
                copletion_reward_coins=1500,
                copletion_reward_gems=5,
                copletion_reward_xp=200,
                copletion_reward_energy=10,
                item_slug="hat_basic",
            ),
            Villages(
                id=2,
                name="Vila Mercantil",
                order=2,
                building_cost_modifier=1.15,
                copletion_reward_coins=2500,
                copletion_reward_gems=8,
                copletion_reward_xp=350,
                copletion_reward_energy=12,
                item_slug="outfit_merchant",
            ),
            Villages(
                id=3,
                name="Vila Real",
                order=3,
                building_cost_modifier=1.30,
                copletion_reward_coins=4000,
                copletion_reward_gems=12,
                copletion_reward_xp=550,
                copletion_reward_energy=15,
                item_slug="crown_bronze",
            ),
            Villages(
                id=4,
                name="Vila Imperial",
                order=4,
                building_cost_modifier=1.45,
                copletion_reward_coins=6500,
                copletion_reward_gems=18,
                copletion_reward_xp=850,
                copletion_reward_energy=18,
                item_slug="armor_imperial",
            ),
            Villages(
                id=5,
                name="Capital Lendária",
                order=5,
                building_cost_modifier=1.6,
                copletion_reward_coins=10000,
                copletion_reward_gems=25,
                copletion_reward_xp=1300,
                copletion_reward_energy=22,
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
                id=1,
                village_id=1,
                name="Casa Simples",
                building_stages=4,
                base_cost=300,
                cost_multiplier=1.25,
            ),
            Buildings(
                id=2,
                village_id=1,
                name="Poço",
                building_stages=4,
                base_cost=450,
                cost_multiplier=1.28,
            ),
            Buildings(
                id=3,
                village_id=1,
                name="Celeiro",
                building_stages=4,
                base_cost=650,
                cost_multiplier=1.30,
            ),
            Buildings(
                id=4,
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
                id=5,
                village_id=2,
                name="Mercado",
                building_stages=4,
                base_cost=900,
                cost_multiplier=1.30,
            ),
            Buildings(
                id=6,
                village_id=2,
                name="Moinho",
                building_stages=4,
                base_cost=1200,
                cost_multiplier=1.32,
            ),
            Buildings(
                id=7,
                village_id=2,
                name="Oficina",
                building_stages=4,
                base_cost=1500,
                cost_multiplier=1.35,
            ),
            Buildings(
                id=8,
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
                id=9,
                village_id=3,
                name="Guarda Real",
                building_stages=4,
                base_cost=1800,
                cost_multiplier=1.35,
            ),
            Buildings(
                id=10,
                village_id=3,
                name="Jardins Reais",
                building_stages=4,
                base_cost=2400,
                cost_multiplier=1.38,
            ),
            Buildings(
                id=11,
                village_id=3,
                name="Salão do Trono",
                building_stages=4,
                base_cost=3200,
                cost_multiplier=1.42,
            ),
            Buildings(
                id=12,
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
                id=13,
                village_id=4,
                name="Quartel Imperial",
                building_stages=4,
                base_cost=3000,
                cost_multiplier=1.38,
            ),
            Buildings(
                id=14,
                village_id=4,
                name="Aqueduto",
                building_stages=4,
                base_cost=3600,
                cost_multiplier=1.4,
            ),
            Buildings(
                id=15,
                village_id=4,
                name="Câmara Imperial",
                building_stages=4,
                base_cost=4800,
                cost_multiplier=1.42,
            ),
            Buildings(
                id=16,
                village_id=4,
                name="Palácio Imperial",
                building_stages=4,
                base_cost=6000,
                cost_multiplier=1.48,
            ),  # âncora
            # =========================
            # VILA 5 — LENDÁRIA
            # =========================
            Buildings(
                id=17,
                village_id=5,
                name="Santuário Antigo",
                building_stages=4,
                base_cost=4500,
                cost_multiplier=1.45,
            ),
            Buildings(
                id=18,
                village_id=5,
                name="Biblioteca Arcana",
                building_stages=4,
                base_cost=5500,
                cost_multiplier=1.48,
            ),
            Buildings(
                id=19,
                village_id=5,
                name="Forja Lendária",
                building_stages=4,
                base_cost=7000,
                cost_multiplier=1.5,
            ),
            Buildings(
                id=20,
                village_id=5,
                name="Trono dos Deuses",
                building_stages=4,
                base_cost=9000,
                cost_multiplier=1.55,
            ),
        ]

        db.bulk_save_objects(buildings)
        db.commit()

        print("✅ Villages and Buildings seeded successfully")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
