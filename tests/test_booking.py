import json
from datetime import date

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import (
    Booking,
    Cruise,
    Customer,
    PromotionRedemption,
    PromotionalCode,
)


client = TestClient(app)


def get_db():
    return SessionLocal()


def create_customer(db, email):
    customer = Customer(
        name="Booking Test Customer",
        email=email
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def test_create_booking():
    db = get_db()

    customer = create_customer(
        db,
        "booking-test-1@example.com"
    )

    cruise = Cruise(
        cruise_line="Test Cruise",
        ship="Test Ship",
        destination="Test Destination",
        nights=7,
        adult_fare=1000,
        capacity=10,
    )

    db.add(cruise)
    db.commit()
    db.refresh(cruise)

    response = client.post(
        "/bookings",
        json={
            "cruise_id": cruise.id,
            "customer_id": customer.id,
            "passenger_ages": [30, 30],
            "services": {},
            "promo_code": None,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["reference"].startswith("CRZ-")
    assert data["customer_id"] == customer.id
    assert data["cruise_id"] == cruise.id
    assert data["passenger_count"] == 2
    assert data["price"]["cruise_fare"] == 2000.0
    assert data["price"]["group_discount"] == 0.0

    db.close()


def test_booking_reduces_capacity():
    db = get_db()

    customer = create_customer(
        db,
        "booking-test-2@example.com"
    )

    cruise = Cruise(
        cruise_line="Capacity Cruise",
        ship="Capacity Ship",
        destination="Caribbean",
        nights=7,
        adult_fare=1000,
        capacity=5,
    )

    db.add(cruise)
    db.commit()
    db.refresh(cruise)

    response = client.post(
        "/bookings",
        json={
            "cruise_id": cruise.id,
            "customer_id": customer.id,
            "passenger_ages": [30, 30, 30],
            "services": {},
        },
    )

    assert response.status_code == 201

    db.refresh(cruise)

    assert cruise.capacity == 2

    db.close()


def test_booking_beyond_capacity_is_rejected():
    db = get_db()

    customer = create_customer(
        db,
        "booking-test-3@example.com"
    )

    cruise = Cruise(
        cruise_line="Limited Cruise",
        ship="Limited Ship",
        destination="Alaska",
        nights=5,
        adult_fare=1000,
        capacity=2,
    )

    db.add(cruise)
    db.commit()
    db.refresh(cruise)

    response = client.post(
        "/bookings",
        json={
            "cruise_id": cruise.id,
            "customer_id": customer.id,
            "passenger_ages": [30, 30, 30],
            "services": {},
        },
    )

    assert response.status_code == 400
    assert "capacity" in response.json()["detail"].lower()

    db.refresh(cruise)

    # Capacity must remain unchanged after failed booking.
    assert cruise.capacity == 2

    db.close()


def test_booking_can_be_retrieved_by_reference():
    db = get_db()

    customer = create_customer(
        db,
        "booking-test-4@example.com"
    )

    cruise = Cruise(
        cruise_line="History Cruise",
        ship="History Ship",
        destination="Mediterranean",
        nights=10,
        adult_fare=1500,
        capacity=10,
    )

    db.add(cruise)
    db.commit()
    db.refresh(cruise)

    create_response = client.post(
        "/bookings",
        json={
            "cruise_id": cruise.id,
            "customer_id": customer.id,
            "passenger_ages": [30, 10],
            "services": {
                "wifi": True
            },
        },
    )

    assert create_response.status_code == 201

    reference = create_response.json()["reference"]

    get_response = client.get(
        f"/bookings/{reference}"
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["reference"] == reference
    assert data["passenger_ages"] == [30, 10]
    assert data["services"]["wifi"] is True

    db.close()


def test_promotion_redemption_is_recorded():
    db = get_db()

    customer = create_customer(
        db,
        "booking-test-5@example.com"
    )

    cruise = Cruise(
        cruise_line="Promo Cruise",
        ship="Promo Ship",
        destination="Caribbean",
        nights=7,
        adult_fare=1200,
        capacity=10,
    )

    db.add(cruise)

    # Create the promotion specifically for this test.
    promotion = PromotionalCode(
        code="TESTPROMO",
        discount_type="percentage",
        discount_value=10,
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
        max_total_uses=100,
        max_uses_per_customer=1,
        minimum_spend=1000,
    )

    db.add(promotion)
    db.commit()

    db.refresh(cruise)

    response = client.post(
        "/bookings",
        json={
            "cruise_id": cruise.id,
            "customer_id": customer.id,
            "passenger_ages": [30, 30],
            "services": {},
            "promo_code": "TESTPROMO",
        },
    )

    assert response.status_code == 201

    booking = (
        db.query(Booking)
        .filter(
            Booking.reference
            == response.json()["reference"]
        )
        .first()
    )

    assert booking is not None
    assert booking.promo_code == "TESTPROMO"

    redemption = (
        db.query(PromotionRedemption)
        .filter(
            PromotionRedemption.booking_id
            == booking.id
        )
        .first()
    )

    assert redemption is not None
    assert redemption.promo_code_id == promotion.id

    db.close()
    
def test_booking_preserves_historical_price():
    db = get_db()

    customer = create_customer(
        db,
        "booking-history@example.com"
    )

    cruise = Cruise(
        cruise_line="Historical Cruise",
        ship="Historical Ship",
        destination="Caribbean",
        nights=7,
        adult_fare=1200,
        capacity=10,
    )

    db.add(cruise)
    db.commit()
    db.refresh(cruise)

    response = client.post(
        "/bookings",
        json={
            "cruise_id": cruise.id,
            "customer_id": customer.id,
            "passenger_ages": [30],
            "services": {},
        },
    )

    assert response.status_code == 201

    data = response.json()

    reference = data["reference"]
    original_total = data["price"]["total"]

    # Simulate a future price change.
    cruise.adult_fare = 2000
    db.commit()

    # Retrieve the historical booking.
    get_response = client.get(
        f"/bookings/{reference}"
    )

    assert get_response.status_code == 200

    historical_data = get_response.json()

    # The old booking must still contain the original price.
    assert historical_data["price"]["cruise_fare"] == 1200.0
    assert historical_data["price"]["total"] == original_total

    db.close()