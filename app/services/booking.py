import json
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import (
    Booking,
    BookingPassenger,
    BookingService,
    Cruise,
    Customer,
    PromotionRedemption,
)
from app.services.pricing import calculate_price
from app.services.promotions import (
    validate_promotion,
    PromotionError,
)


def generate_booking_reference() -> str:
    """Generate a unique customer-facing booking reference."""
    return f"CRZ-{uuid4().hex[:10].upper()}"


def create_booking(
    db: Session,
    customer: Customer,
    cruise: Cruise,
    passenger_ages: list[int],
    services: dict[str, bool],
    promo_code: str | None = None,
) -> Booking:

    passenger_count = len(passenger_ages)

    # Calculate base price first.
    price = calculate_price(
        ages=passenger_ages,
        adult_fare=cruise.adult_fare,
        nights=cruise.nights,
        services=services,
        promo_discount=0,
    )

    promo = None
    promo_discount = 0.0

    # Validate promotional code.
    if promo_code:
        try:
            promo, promo_discount = validate_promotion(
                db=db,
                code=promo_code,
                customer_id=customer.id,
                subtotal=price["subtotal"],
                booking_date=date.today(),
            )
        except PromotionError:
            raise

        # Recalculate with promotional discount.
        price = calculate_price(
            ages=passenger_ages,
            adult_fare=cruise.adult_fare,
            nights=cruise.nights,
            services=services,
            promo_discount=promo_discount,
        )

    # Reserve capacity atomically.
    updated_rows = (
        db.query(Cruise)
        .filter(
            Cruise.id == cruise.id,
            Cruise.capacity >= passenger_count,
        )
        .update(
            {
                Cruise.capacity:
                    Cruise.capacity - passenger_count
            },
            synchronize_session=False,
        )
    )

    if updated_rows != 1:
        raise ValueError(
            "Insufficient cruise capacity."
        )

    # Create booking.
    booking = Booking(
        reference=generate_booking_reference(),

        customer_id=customer.id,
        cruise_id=cruise.id,

        cruise_fare=price["cruise_fare"],
        group_discount=price["group_discount"],
        services_total=price["services_total"],
        promo_discount=price["promo_discount"],

        tax_rate=price["tax_rate"],
        tax_amount=price["tax"],
        total_amount=price["total"],

        promo_code=promo.code if promo else None,

        passenger_snapshot=json.dumps(
            passenger_ages
        ),

        service_snapshot=json.dumps(
            services
        ),

        created_at=datetime.utcnow(),
    )

    db.add(booking)
    db.flush()

    # Store passengers.
    for age in passenger_ages:
        db.add(
            BookingPassenger(
                booking_id=booking.id,
                age=age,
            )
        )

    # Store optional services.
    if services.get("insurance"):
        db.add(
            BookingService(
                booking_id=booking.id,
                service_name="insurance",
                quantity=passenger_count,
                total_price=80 * passenger_count,
            )
        )

    if services.get("wifi"):
        db.add(
            BookingService(
                booking_id=booking.id,
                service_name="wifi",
                quantity=passenger_count,
                total_price=(
                    15
                    * passenger_count
                    * cruise.nights
                ),
            )
        )

    if services.get("shore_excursion"):
        db.add(
            BookingService(
                booking_id=booking.id,
                service_name="shore_excursion",
                quantity=passenger_count,
                total_price=120 * passenger_count,
            )
        )

    # Record promotion redemption.
    if promo:
        db.add(
            PromotionRedemption(
                promo_code_id=promo.id,
                customer_id=customer.id,
                booking_id=booking.id,
                redeemed_at=datetime.utcnow(),
            )
        )

    return booking