from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cruise, Customer
from app.schemas import QuoteRequest, QuoteResponse, PriceBreakdown
from app.services.pricing import calculate_price
from app.services.promotions import (
    validate_promotion,
    PromotionError,
)


router = APIRouter(
    prefix="/quotes",
    tags=["Quotes"]
)


@router.post("", response_model=QuoteResponse)
def create_quote(
    request: QuoteRequest,
    db: Session = Depends(get_db)
):
    # Find cruise
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

    # Check capacity without modifying it.
    if cruise.capacity < len(request.passenger_ages):
        raise HTTPException(
            status_code=400,
            detail="Insufficient cruise capacity."
        )

    # Customer is required for promotion validation.
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

    # First calculate price without promotional discount.
    price = calculate_price(
        ages=request.passenger_ages,
        adult_fare=cruise.adult_fare,
        nights=cruise.nights,
        services=request.services,
        promo_discount=0,
    )

    promo_discount = 0.0

    # Validate promotion if supplied.
    if request.promo_code:
        try:
            _, promo_discount = validate_promotion(
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

        # Recalculate final price with promo.
        price = calculate_price(
            ages=request.passenger_ages,
            adult_fare=cruise.adult_fare,
            nights=cruise.nights,
            services=request.services,
            promo_discount=promo_discount,
        )

    return QuoteResponse(
        cruise_id=cruise.id,
        cruise_line=cruise.cruise_line,
        ship=cruise.ship,
        destination=cruise.destination,
        nights=cruise.nights,
        passenger_count=len(request.passenger_ages),
        price=PriceBreakdown(**price),
    )