from datetime import date

import pytest

from app.database import Base, engine, SessionLocal
from app.models import (
    Customer,
    PromotionalCode,
    PromotionRedemption,
)
from app.services.promotions import (
    validate_promotion,
    PromotionError,
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # Clean tables for isolated tests
    session.query(PromotionRedemption).delete()
    session.query(PromotionalCode).delete()
    session.query(Customer).delete()
    session.commit()

    yield session

    session.close()


@pytest.fixture
def customer(db):
    customer = Customer(
        name="Test Customer",
        email="test@example.com"
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@pytest.fixture
def summer10(db):
    promotion = PromotionalCode(
        code="SUMMER10",
        discount_type="percentage",
        discount_value=10,
        valid_from=date(2026, 6, 1),
        valid_to=date(2026, 8, 31),
        max_total_uses=100,
        max_uses_per_customer=1,
        minimum_spend=1000,
    )

    db.add(promotion)
    db.commit()
    db.refresh(promotion)

    return promotion


def test_valid_percentage_promotion(
    db,
    customer,
    summer10
):
    promotion, discount = validate_promotion(
        db=db,
        code="SUMMER10",
        customer_id=customer.id,
        subtotal=2000,
        booking_date=date(2026, 8, 18),
    )

    assert promotion.code == "SUMMER10"
    assert discount == 200.0


def test_invalid_promotion_code(
    db,
    customer
):
    with pytest.raises(PromotionError):
        validate_promotion(
            db=db,
            code="INVALID",
            customer_id=customer.id,
            subtotal=2000,
            booking_date=date(2026, 8, 18),
        )


def test_promotion_not_yet_valid(
    db,
    customer,
    summer10
):
    with pytest.raises(PromotionError):
        validate_promotion(
            db=db,
            code="SUMMER10",
            customer_id=customer.id,
            subtotal=2000,
            booking_date=date(2026, 5, 31),
        )


def test_expired_promotion(
    db,
    customer,
    summer10
):
    with pytest.raises(PromotionError):
        validate_promotion(
            db=db,
            code="SUMMER10",
            customer_id=customer.id,
            subtotal=2000,
            booking_date=date(2026, 9, 1),
        )


def test_minimum_spend_not_met(
    db,
    customer,
    summer10
):
    with pytest.raises(PromotionError):
        validate_promotion(
            db=db,
            code="SUMMER10",
            customer_id=customer.id,
            subtotal=999,
            booking_date=date(2026, 8, 18),
        )


def test_exact_minimum_spend_is_valid(
    db,
    customer,
    summer10
):
    _, discount = validate_promotion(
        db=db,
        code="SUMMER10",
        customer_id=customer.id,
        subtotal=1000,
        booking_date=date(2026, 8, 18),
    )

    assert discount == 100.0


def test_customer_usage_limit(
    db,
    customer,
    summer10
):
    redemption = PromotionRedemption(
        promo_code_id=summer10.id,
        customer_id=customer.id,
        booking_id=999,
    )

    db.add(redemption)
    db.commit()

    with pytest.raises(PromotionError):
        validate_promotion(
            db=db,
            code="SUMMER10",
            customer_id=customer.id,
            subtotal=2000,
            booking_date=date(2026, 8, 18),
        )


def test_total_usage_limit(
    db,
    customer,
    summer10
):
    summer10.max_total_uses = 1
    db.commit()

    redemption = PromotionRedemption(
        promo_code_id=summer10.id,
        customer_id=customer.id,
        booking_id=999,
    )

    db.add(redemption)
    db.commit()

    # A different customer should also be rejected
    another_customer = Customer(
        name="Another Customer",
        email="another@example.com"
    )

    db.add(another_customer)
    db.commit()

    with pytest.raises(PromotionError):
        validate_promotion(
            db=db,
            code="SUMMER10",
            customer_id=another_customer.id,
            subtotal=2000,
            booking_date=date(2026, 8, 18),
        )


def test_fixed_discount(
    db,
    customer
):
    promotion = PromotionalCode(
        code="FIRST150",
        discount_type="fixed",
        discount_value=150,
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
        max_total_uses=500,
        max_uses_per_customer=1,
        minimum_spend=2000,
    )

    db.add(promotion)
    db.commit()

    _, discount = validate_promotion(
        db=db,
        code="FIRST150",
        customer_id=customer.id,
        subtotal=3000,
        booking_date=date(2026, 8, 18),
    )

    assert discount == 150.0


def test_fixed_discount_cannot_exceed_subtotal(
    db,
    customer
):
    promotion = PromotionalCode(
        code="BIGDISCOUNT",
        discount_type="fixed",
        discount_value=1000,
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
        minimum_spend=0,
    )

    db.add(promotion)
    db.commit()

    _, discount = validate_promotion(
        db=db,
        code="BIGDISCOUNT",
        customer_id=customer.id,
        subtotal=500,
        booking_date=date(2026, 8, 18),
    )

    assert discount == 500.0