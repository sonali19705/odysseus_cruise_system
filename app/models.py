from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
)

from sqlalchemy.orm import relationship

from app.database import Base


class Cruise(Base):
    __tablename__ = "cruises"

    id = Column(Integer, primary_key=True, index=True)
    cruise_line = Column(String, nullable=False)
    ship = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    nights = Column(Integer, nullable=False)
    adult_fare = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)

    bookings = relationship("Booking", back_populates="cruise")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)

    bookings = relationship("Booking", back_populates="customer")


class PromotionalCode(Base):
    __tablename__ = "promotional_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True, index=True)
    discount_type = Column(String, nullable=False)
    discount_value = Column(Float, nullable=False)

    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)

    max_total_uses = Column(Integer, nullable=True)
    max_uses_per_customer = Column(Integer, nullable=True)
    minimum_spend = Column(Float, nullable=False, default=0)

    redemptions = relationship(
        "PromotionRedemption",
        back_populates="promo_code"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    reference = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    cruise_id = Column(
        Integer,
        ForeignKey("cruises.id"),
        nullable=False
    )

    # Historical pricing snapshot
    cruise_fare = Column(Float, nullable=False)
    group_discount = Column(Float, nullable=False)
    services_total = Column(Float, nullable=False)
    promo_discount = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Store the promo code actually used
    promo_code = Column(String, nullable=True)

    # JSON-like snapshots stored as text
    passenger_snapshot = Column(Text, nullable=False)
    service_snapshot = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    customer = relationship(
        "Customer",
        back_populates="bookings"
    )

    cruise = relationship(
        "Cruise",
        back_populates="bookings"
    )

    passengers = relationship(
        "BookingPassenger",
        back_populates="booking",
        cascade="all, delete-orphan"
    )

    services = relationship(
        "BookingService",
        back_populates="booking",
        cascade="all, delete-orphan"
    )


class BookingPassenger(Base):
    __tablename__ = "booking_passengers"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    age = Column(Integer, nullable=False)

    booking = relationship(
        "Booking",
        back_populates="passengers"
    )


class BookingService(Base):
    __tablename__ = "booking_services"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    service_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    booking = relationship(
        "Booking",
        back_populates="services"
    )


class PromotionRedemption(Base):
    __tablename__ = "promotion_redemptions"

    id = Column(Integer, primary_key=True, index=True)

    promo_code_id = Column(
        Integer,
        ForeignKey("promotional_codes.id"),
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    redeemed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    promo_code = relationship(
        "PromotionalCode",
        back_populates="redemptions"
    )