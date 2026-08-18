import pytest

from app.services.pricing import (
    validate_passengers,
    calculate_passenger_fare,
    calculate_cruise_fare,
    calculate_group_discount,
    calculate_service_total,
    calculate_price,
)


ADULT_FARE = 1200.0


def test_adult_pays_full_fare():
    assert calculate_passenger_fare(18, ADULT_FARE) == 1200.0


def test_child_age_zero_is_free():
    assert calculate_passenger_fare(0, ADULT_FARE) == 0.0


def test_child_age_four_is_free():
    assert calculate_passenger_fare(4, ADULT_FARE) == 0.0


def test_child_age_five_pays_fifty_percent():
    assert calculate_passenger_fare(5, ADULT_FARE) == 600.0


def test_child_age_eleven_pays_fifty_percent():
    assert calculate_passenger_fare(11, ADULT_FARE) == 600.0


def test_child_age_twelve_pays_seventy_five_percent():
    assert calculate_passenger_fare(12, ADULT_FARE) == 900.0


def test_child_age_seventeen_pays_seventy_five_percent():
    assert calculate_passenger_fare(17, ADULT_FARE) == 900.0


def test_age_eighteen_is_adult():
    assert calculate_passenger_fare(18, ADULT_FARE) == 1200.0


def test_booking_requires_at_least_one_adult():
    with pytest.raises(ValueError):
        validate_passengers([5, 10, 17])


def test_maximum_six_passengers():
    with pytest.raises(ValueError):
        validate_passengers([30, 30, 30, 30, 30, 30, 30])


def test_three_passengers_get_five_percent_group_discount():
    assert calculate_group_discount(3, 3000) == 150.0


def test_four_passengers_get_five_percent_group_discount():
    assert calculate_group_discount(4, 3000) == 150.0


def test_five_passengers_get_ten_percent_group_discount():
    assert calculate_group_discount(5, 3000) == 300.0


def test_two_passengers_get_no_group_discount():
    assert calculate_group_discount(2, 2400) == 0.0


def test_insurance_cost():
    assert calculate_service_total(
        {"insurance": True},
        passenger_count=3,
        nights=7
    ) == 240.0


def test_wifi_cost():
    assert calculate_service_total(
        {"wifi": True},
        passenger_count=3,
        nights=7
    ) == 315.0


def test_shore_excursion_cost():
    assert calculate_service_total(
        {"shore_excursion": True},
        passenger_count=2,
        nights=7
    ) == 240.0


def test_complete_price_calculation():
    result = calculate_price(
        ages=[30, 30, 10],
        adult_fare=1200,
        nights=7,
        services={"wifi": True},
        promo_discount=316.50,
    )

    assert result["cruise_fare"] == 3000.0
    assert result["group_discount"] == 150.0
    assert result["services_total"] == 315.0
    assert result["subtotal"] == 3165.0
    assert result["promo_discount"] == 316.50
    assert result["tax"] == 341.82
    assert result["total"] == 3190.32