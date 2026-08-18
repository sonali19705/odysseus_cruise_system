from datetime import date
from sqlalchemy.orm import Session

from app.models import PromotionalCode, PromotionRedemption


class PromotionError(ValueError):
    """Raised when a promotional code cannot be applied."""


def validate_promotion(
    db: Session,
    code: str,
    customer_id: int,
    subtotal: float,
    booking_date: date | None = None,
) -> tuple[PromotionalCode, float]:

    if booking_date is None:
        booking_date = date.today()

    # Normalize user input
    code = code.strip().upper()

    # 1. Find promotion
    promotion = (
        db.query(PromotionalCode)
        .filter(PromotionalCode.code == code)
        .first()
    )

    if not promotion:
        raise PromotionError("Invalid promotional code.")

    # 2. Validate date
    if booking_date < promotion.valid_from:
        raise PromotionError("Promotional code is not yet valid.")

    if booking_date > promotion.valid_to:
        raise PromotionError("Promotional code has expired.")

    # 3. Validate minimum spend
    if subtotal < promotion.minimum_spend:
        raise PromotionError(
            f"Minimum spend of ${promotion.minimum_spend:.2f} "
            "is required for this promotional code."
        )

    # 4. Validate total usage limit
    if promotion.max_total_uses is not None:
        total_uses = (
            db.query(PromotionRedemption)
            .filter(
                PromotionRedemption.promo_code_id == promotion.id
            )
            .count()
        )

        if total_uses >= promotion.max_total_uses:
            raise PromotionError(
                "Promotional code total usage limit has been reached."
            )

    # 5. Validate per-customer usage limit
    if promotion.max_uses_per_customer is not None:
        customer_uses = (
            db.query(PromotionRedemption)
            .filter(
                PromotionRedemption.promo_code_id == promotion.id,
                PromotionRedemption.customer_id == customer_id,
            )
            .count()
        )

        if customer_uses >= promotion.max_uses_per_customer:
            raise PromotionError(
                "Customer usage limit for this promotional code "
                "has been reached."
            )

    # 6. Calculate discount
    if promotion.discount_type == "percentage":
        discount = subtotal * (
            promotion.discount_value / 100
        )

    elif promotion.discount_type == "fixed":
        discount = promotion.discount_value

    else:
        raise PromotionError(
            "Unsupported promotional discount type."
        )

    # Never allow a promotion to make the subtotal negative.
    discount = min(discount, subtotal)

    return promotion, round(discount, 2)