from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class QuoteRequest(BaseModel):
    cruise_id: int
    customer_id: int
    passenger_ages: List[int] = Field(min_length=1, max_length=6)
    services: Dict[str, bool] = {}
    promo_code: Optional[str] = None

    @field_validator("passenger_ages")
    @classmethod
    def validate_ages(cls, ages):
        if any(age < 0 or age > 120 for age in ages):
            raise ValueError(
                "Passenger age must be between 0 and 120."
            )

        if not any(age >= 18 for age in ages):
            raise ValueError(
                "At least one adult passenger is required."
            )

        return ages


class PriceBreakdown(BaseModel):
    cruise_fare: float
    group_discount: float
    services_total: float
    subtotal: float
    promo_discount: float
    taxable_amount: float
    tax_rate: float
    tax: float
    total: float


class QuoteResponse(BaseModel):
    cruise_id: int
    cruise_line: str
    ship: str
    destination: str
    nights: int
    passenger_count: int
    price: PriceBreakdown