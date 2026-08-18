import json
from datetime import date, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Booking,
    BookingPassenger,
    BookingService,
    Cruise,
    Customer,
    PromotionRedemption,
)
from app.schemas import (
    BookingRequest,
    BookingResponse,
    BookingDetailResponse,
    PriceBreakdown,
)
from app.services.pricing import calculate_price
from app.services.promotions import (
    validate_promotion,
    PromotionError,
)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


def generate_booking_reference() -> str:
    """
    Generate a unique customer-facing booking reference.
    """
    return f"CRZ-{uuid4().hex[:10].upper()}"


@router.post(
    "",
    response_model=BookingResponse,
    status_code=201
)
def create_booking(
    request: BookingRequest,
    db: Session = Depends(get_db)
):
    try:
        # -------------------------------------------------
        # 1. Validate customer
        # -------------------------------------------------
        customer = (
            db.query(Customer)
            .filter(Customer.id == request.customer_id)
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found."
            )

        # -------------------------------------------------
        # 2. Find cruise
        # -------------------------------------------------
        cruise = (
            db.query(Cruise)
            .filter(Cruise.id == request.cruise_id)
            .first()
        )

        if not cruise:
            raise HTTPException(
                status_code=404,
                detail="Cruise not found."
            )

        passenger_count = len(request.passenger_ages)

        # -------------------------------------------------
        # 3. Calculate price BEFORE changing anything
        # -------------------------------------------------
        price = calculate_price(
            ages=request.passenger_ages,
            adult_fare=cruise.adult_fare,
            nights=cruise.nights,
            services=request.services,
            promo_discount=0,
        )

        promo = None
        promo_discount = 0.0

        # -------------------------------------------------
        # 4. Validate promotional code
        # -------------------------------------------------
        if request.promo_code:
            try:
                promo, promo_discount = validate_promotion(
                    db=db,
                    code=request.promo_code,
                    customer_id=customer.id,
                    subtotal=price["subtotal"],
                    booking_date=date.today(),
                )
            except PromotionError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=str(exc)
                )

            # Recalculate final price including promo.
            price = calculate_price(
                ages=request.passenger_ages,
                adult_fare=cruise.adult_fare,
                nights=cruise.nights,
                services=request.services,
                promo_discount=promo_discount,
            )

        # -------------------------------------------------
        # 5. Atomically reserve capacity
        # -------------------------------------------------
        updated_rows = (
            db.query(Cruise)
            .filter(
                Cruise.id == cruise.id,
                Cruise.capacity >= passenger_count
            )
            .update(
                {
                    Cruise.capacity:
                        Cruise.capacity - passenger_count
                },
                synchronize_session=False
            )
        )

        if updated_rows != 1:
            raise HTTPException(
                status_code=400,
                detail="Insufficient cruise capacity."
            )

        # -------------------------------------------------
        # 6. Create unique booking reference
        # -------------------------------------------------
        reference = generate_booking_reference()

        # -------------------------------------------------
        # 7. Create booking pricing snapshot
        # -------------------------------------------------
        booking = Booking(
            reference=reference,
            customer_id=customer.id,
            cruise_id=cruise.id,

            cruise_fare=price["cruise_fare"],
            group_discount=price["group_discount"],
            services_total=price["services_total"],
            promo_discount=price["promo_discount"],
            tax_rate=price["tax_rate"],
            tax_amount=price["tax"],
            total_amount=price["total"],

            promo_code=(
                promo.code
                if promo
                else None
            ),

            passenger_snapshot=json.dumps(
                request.passenger_ages
            ),

            service_snapshot=json.dumps(
                request.services
            ),

            created_at=datetime.utcnow(),
        )

        db.add(booking)

        # Flush so booking.id exists before redemption.
        db.flush()

        # -------------------------------------------------
        # 8. Store passenger records
        # -------------------------------------------------
        for age in request.passenger_ages:
            passenger = BookingPassenger(
                booking_id=booking.id,
                age=age,
            )

            db.add(passenger)

        # -------------------------------------------------
        # 9. Store service records
        # -------------------------------------------------
        passenger_count = len(request.passenger_ages)

        if request.services.get("insurance"):
            db.add(
                BookingService(
                    booking_id=booking.id,
                    service_name="insurance",
                    quantity=passenger_count,
                    total_price=80 * passenger_count,
                )
            )

        if request.services.get("wifi"):
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

        if request.services.get("shore_excursion"):
            db.add(
                BookingService(
                    booking_id=booking.id,
                    service_name="shore_excursion",
                    quantity=passenger_count,
                    total_price=120 * passenger_count,
                )
            )

        # -------------------------------------------------
        # 10. Record promotional redemption
        # -------------------------------------------------
        if promo:
            redemption = PromotionRedemption(
                promo_code_id=promo.id,
                customer_id=customer.id,
                booking_id=booking.id,
                redeemed_at=datetime.utcnow(),
            )

            db.add(redemption)

        # -------------------------------------------------
        # 11. Commit EVERYTHING together
        # -------------------------------------------------
        db.commit()

        db.refresh(booking)

        return BookingResponse(
            reference=booking.reference,
            customer_id=booking.customer_id,
            cruise_id=booking.cruise_id,
            passenger_count=passenger_count,
            price=PriceBreakdown(
                cruise_fare=booking.cruise_fare,
                group_discount=booking.group_discount,
                services_total=booking.services_total,
                subtotal=round(
                    booking.cruise_fare
                    - booking.group_discount
                    + booking.services_total,
                    2
                ),
                promo_discount=booking.promo_discount,
                taxable_amount=round(
                    booking.total_amount
                    - booking.tax_amount,
                    2
                ),
                tax_rate=booking.tax_rate,
                tax=booking.tax_amount,
                total=booking.total_amount,
            ),
            created_at=booking.created_at.isoformat(),
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Booking could not be created: {str(exc)}"
        )

@router.get(
    "/{reference}",
    response_model=BookingDetailResponse
)
def get_booking(
    reference: str,
    db: Session = Depends(get_db)
):
    booking = (
        db.query(Booking)
        .filter(Booking.reference == reference)
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found."
        )

    return BookingDetailResponse(
        reference=booking.reference,
        customer_id=booking.customer_id,
        cruise_id=booking.cruise_id,
        passenger_ages=json.loads(
            booking.passenger_snapshot
        ),
        services=json.loads(
            booking.service_snapshot
        ),
        price=PriceBreakdown(
            cruise_fare=booking.cruise_fare,
            group_discount=booking.group_discount,
            services_total=booking.services_total,
            subtotal=round(
                booking.cruise_fare
                - booking.group_discount
                + booking.services_total,
                2
            ),
            promo_discount=booking.promo_discount,
            taxable_amount=round(
                booking.total_amount
                - booking.tax_amount,
                2
            ),
            tax_rate=booking.tax_rate,
            tax=booking.tax_amount,
            total=booking.total_amount,
        ),
        promo_code=booking.promo_code,
        created_at=booking.created_at.isoformat(),
    )