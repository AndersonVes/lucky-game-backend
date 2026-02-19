from app.db.models import Event
from app.core.database import SessionLocal


def seed_events(db):
    db = SessionLocal()

    try:

        events = [
            # ==========================
            # seasonal events
            # ==========================
            Event(
                slug="valentines_2027",
                type="seasonal",
                name="Valentine’s Festival",
                description="",
                start_at="2027-02-01",
                end_at="2027-03-05",
                target_item_slug="valentines_dress",
            ),
            Event(
                slug="st_patricks_2027",
                type="seasonal",
                name="Green Blessing Campaign",
                description="",
                start_at="2027-03-15",
                end_at="2027-04-16",
                target_item_slug="st_patrick_kimono",
            ),
            Event(
                slug="beachside_2026",
                type="seasonal",
                name="Beachside Festival",
                description="",
                start_at="2026-06-01",
                end_at="2026-07-05",
                target_item_slug="summer_bikini",
            ),
            Event(
                slug="eclipse_2026",
                type="seasonal",
                name="Eclipse Festival",
                description="",
                start_at="2026-08-10",
                end_at="2026-08-25",
                target_item_slug="moon_hat",
            ),
            Event(
                slug="winter_2026",
                type="seasonal",
                name="Winter Festival",
                description="",
                start_at="2026-12-01",
                end_at="2027-01-07",
                target_item_slug="santa_claus_dress",
                secondary_target_item_slug="santa_claus_hat",
            ),
            # ==========================
            # progression_line_id = 1
            # ==========================
            Event(
                slug="back_to_school",
                type="progression",
                name="Back to School",
                progression_line_id=1,
                order_in_line=1,
                target_item_slug="school_uniform",
            ),
            Event(
                slug="pajama_party",
                type="progression",
                name="Pajama Party",
                progression_line_id=1,
                order_in_line=2,
                target_item_slug="pajamas",
            ),
            Event(
                slug="farm_day",
                type="progression",
                name="Farm Day",
                progression_line_id=1,
                order_in_line=3,
                target_item_slug="straw_hat",
            ),
            Event(
                slug="part_time_work_place",
                type="progression",
                name="Part-Time Work Place",
                progression_line_id=1,
                order_in_line=4,
                target_item_slug="maid_uniform",
            ),
            Event(
                slug="on_duty",
                type="progression",
                name="On Duty!!",
                progression_line_id=1,
                order_in_line=5,
                target_item_slug="police_uniform",
                secondary_target_item_slug="police_hat",
            ),
            # ==========================
            # progression_line_id = 2
            # ==========================
            Event(
                slug="a_day_in_the_office",
                type="progression",
                name="A Day in the Office",
                progression_line_id=2,
                order_in_line=1,
                target_item_slug="office_shirt",
            ),
            Event(
                slug="groundhog_day",
                type="progression",
                name="Groundhog Day",
                progression_line_id=2,
                order_in_line=2,
                target_item_slug="army_armor",
                secondary_target_item_slug="army_hat",
            ),
            Event(
                slug="crimson_kingdom_gala",
                type="progression",
                name="Crimson Kingdom Gala",
                progression_line_id=2,
                order_in_line=3,
                target_item_slug="medieval_dress",
            ),
            Event(
                slug="oath_of_the_silver_leaves",
                type="progression",
                name="Oath of the Silver Leaves",
                progression_line_id=2,
                order_in_line=4,
                target_item_slug="elf_dress",
            ),
            Event(
                slug="witch_of_the_blazing_sky",
                type="progression",
                name="Witch of the Blazing Sky",
                progression_line_id=2,
                order_in_line=5,
                target_item_slug="witch_hat",
            ),
        ]

        db.bulk_save_objects(events)
        db.flush()
        db.commit()

        print("✅ Events seeded successfully")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()
    seed_events(db)
