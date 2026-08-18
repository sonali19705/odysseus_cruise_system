# Technical Approach

## 1. Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest

A frontend is intentionally not implemented because the assessment focuses on business rules, data modelling, pricing, persistence, and testing.

## 2. Architecture

The application follows a lightweight layered architecture:

```text
API Routes
    ↓
Service Layer
    ↓
SQLAlchemy / Database
    ↓
SQLite

### Booking Atomicity

Booking confirmation is treated as a single database transaction. Capacity reservation, booking creation, passenger/service persistence, and promotional redemption are committed together.

If any operation fails, the transaction is rolled back so that capacity and promotional usage are not changed without a corresponding confirmed booking.

Capacity is updated using a conditional database update requiring sufficient remaining capacity, reducing the risk of overselling.

