from app.core.database import SessionLocal
from app.models.content_patches import ContentPatch


def seed_patches(db):
    db = SessionLocal()

    try:

        # Create content patches for different app versions
        patches = [
            ContentPatch(
                id=1,
                app_version_min="1.5.0",
                app_version_max="1.5.0",
                content_version="1.0.0",
                catalog_url="https://example.com/catalog_v1.json",
                base_url="https://example.com/content/v1/",
                size_mb=150,
                mandatory=True,
                checksum="abc123def456ghi789jkl012mno345pq",
                active=True,
            )
        ]

        # SQL equivalent:
        # INSERT INTO content_patches (id, app_version_min, app_version_max, content_version,
        #   catalog_url, base_url, size_mb, mandatory, checksum, active)
        # VALUES (1, '1.0.0', '1.5.0', '1.0.0', 'https://example.com/catalog_v1.json',
        #   'https://example.com/content/v1/', 150, true, 'abc123def456ghi789jkl012mno345pq', true);

        db.bulk_save_objects(patches)
        db.flush()
        db.commit()

        print("✅ Content Patches seeded successfully")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()
    seed_patches(db)
