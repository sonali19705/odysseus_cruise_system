from typing import List, Dict, Optional


TAX_RATE = 0.12

INSURANCE_PRICE = 80.0
WIFI_PRICE_PER_PASSENGER_PER_NIGHT = 15.0
SHORE_EXCURSION_PRICE = 120.0


def validate_passengers(ages: List[int]) -> None:
    """
    Validate passenger count and age rules.

    Business rules:
    - 1 to 6 passengers
    - At least one adult
    - Age must be between 0 and 120
    - Age 18+ is an adult
    """

    if not ages:
        raise ValueError("At least one passenger is required.")

    if len(ages) > 6:
        raise ValueError("A maximum of 6 passengers is allowed.")

    if any(age < 0 or age > 120 for age in ages):
        raise ValueError("Passenger age must be between 0 and 120.")

    if not any(age >= 18 for age in ages):
        raise ValueError("At least one adult passenger is required.")


def calculate_passenger_fare(age: int, adult_fare: float) -> float:
    """
    Calculate the fare for one passenger based on age.
    """

    if age < 0 or age > 120:
        raise ValueError("Passenger age must be between 0 and 120.")

    if age >= 18:
        return adult_fare

    if age <= 4:
        return 0.0

    if age <= 11:
        return adult_fare * 0.50

    return adult_fare * 0.75


def calculate_cruise_fare(
    ages: List[int],
    adult_fare: float
) -> float:
    """
    Calculate total cruise fare before group discount.
    """

    validate_passengers(ages)

    total = sum(
        calculate_passenger_fare(age, adult_fare)
        for age in ages
    )

    return round(total, 2)


def calculate_group_discount(
    passenger_count: int,
    cruise_fare: float
) -> float:
    """
    Calculate group discount amount.

    1-2 passengers: 0%
    3-4 passengers: 5%
    5-6 passengers: 10%

    Discount applies only to cruise fare.
    """

    if passenger_count <= 2:
        rate = 0.0
    elif passenger_count <= 4:
        rate = 0.05
    elif passenger_count <= 6:
        rate = 0.10
    else:
        raise ValueError("A maximum of 6 passengers is allowed.")

    return round(cruise_fare * rate, 2)


def calculate_service_total(
    services: Optional[Dict[str, bool]],
    passenger_count: int,
    nights: int
) -> float:
    """
    Calculate optional service charges.

    Supported services:
    - insurance: $80 per passenger
    - wifi: $15 per passenger per night
    - shore_excursion: $120 per passenger
    """

    if not services:
        return 0.0

    total = 0.0

    if services.get("insurance", False):
        total += INSURANCE_PRICE * passenger_count

    if services.get("wifi", False):
        total += (
            WIFI_PRICE_PER_PASSENGER_PER_NIGHT
            * passenger_count
            * nights
        )

    if services.get("shore_excursion", False):
        total += SHORE_EXCURSION_PRICE * passenger_count

    return round(total, 2)


def calculate_subtotal(
    cruise_fare: float,
    group_discount: float,
    services_total: float
) -> float:
    """
    Calculate subtotal before promotional discount.
    """

    return round(
        cruise_fare - group_discount + services_total,
        2
    )


def calculate_tax(taxable_amount: float) -> float:
    """
    Apply the configured 12% tax rate.
    """

    return round(taxable_amount * TAX_RATE, 2)


def calculate_total(
    subtotal: float,
    promo_discount: float = 0.0
) -> Dict[str, float]:
    """
    Calculate final booking total.

    Promotional discount is applied before tax.
    """

    promo_discount = min(promo_discount, subtotal)

    taxable_amount = round(
        subtotal - promo_discount,
        2
    )

    tax = calculate_tax(taxable_amount)

    total = round(
        taxable_amount + tax,
        2
    )

    return {
        "subtotal": round(subtotal, 2),
        "promo_discount": round(promo_discount, 2),
        "taxable_amount": taxable_amount,
        "tax_rate": TAX_RATE,
        "tax": tax,
        "total": total,
    }


def calculate_price(
    ages: List[int],
    adult_fare: float,
    nights: int,
    services: Optional[Dict[str, bool]] = None,
    promo_discount: float = 0.0
) -> Dict[str, float]:
    """
    Calculate the complete booking price before booking confirmation.
    """

    validate_passengers(ages)

    passenger_count = len(ages)

    cruise_fare = calculate_cruise_fare(
        ages,
        adult_fare
    )

    group_discount = calculate_group_discount(
        passenger_count,
        cruise_fare
    )

    services_total = calculate_service_total(
        services,
        passenger_count,
        nights
    )

    subtotal = calculate_subtotal(
        cruise_fare,
        group_discount,
        services_total
    )

    result = calculate_total(
        subtotal,
        promo_discount
    )

    return {
        "cruise_fare": cruise_fare,
        "group_discount": group_discount,
        "services_total": services_total,
        **result,
    }