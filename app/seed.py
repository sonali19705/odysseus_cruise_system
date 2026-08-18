from datetime import date

from app.database import Base, SessionLocal, engine
from app.models import Cruise, PromotionalCode


def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Avoid duplicate seed data
        if db.query(Cruise).count() > 0:
            print("Database already contains cruise data.")
            return

        cruises = [
            Cruise(
                cruise_line="Royal Caribbean",
                ship="Wonder of the Seas",
                destination="Caribbean",
                nights=7,
                adult_fare=1200,
                capacity=12,
            ),
            Cruise(
                cruise_line="Celebrity Cruises",
                ship="Celebrity Beyond",
                destination="Mediterranean",
                nights=10,
                adult_fare=1850,
                capacity=4,
            ),
            Cruise(
                cruise_line="Norwegian Cruise Line",
                ship="Norwegian Prima",
                destination="Alaska",
                nights=5,
                adult_fare=950,
                capacity=20,
            ),
            Cruise(
                cruise_line="Princess Cruises",
                ship="Sky Princess",
                destination="Northern Europe",
                nights=12,
                adult_fare=2100,
                capacity=2,
            ),
            Cruise(
                cruise_line="MSC Cruises",
                ship="MSC Seascape",
                destination="Bahamas",
                nights=4,
                adult_fare=700,
                capacity=0,
            ),
        ]

        promo_codes = [
            PromotionalCode(
                code="SUMMER10",
                discount_type="percentage",
                discount_value=10,
                valid_from=date(2026, 6, 1),
                valid_to=date(2026, 8, 31),
                max_total_uses=100,
                max_uses_per_customer=1,
                minimum_spend=1000,
            ),
            PromotionalCode(
                code="FIRST150",
                discount_type="fixed",
                discount_value=150,
                valid_from=date(2026, 1, 1),
                valid_to=date(2026, 12, 31),
                max_total_uses=500,
                max_uses_per_customer=1,
                minimum_spend=2000,
            ),
            PromotionalCode(
                code="CREW25",
                discount_type="percentage",
                discount_value=25,
                valid_from=date(2026, 1, 1),
                valid_to=date(2026, 12, 31),
                max_total_uses=3,
                max_uses_per_customer=3,
                minimum_spend=0,
            ),
            PromotionalCode(
                code="WINTER5",
                discount_type="percentage",
                discount_value=5,
                valid_from=date(2025, 1, 1),
                valid_to=date(2025, 3, 31),
                max_total_uses=None,
                max_uses_per_customer=None,
                minimum_spend=0,
            ),
        ]

        db.add_all(cruises)
        db.add_all(promo_codes)
        db.commit()

        print("Database seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()