# Cruise Booking System

A cruise booking system developed for the Odysseus Solutions Campus Placement Technical Assessment.

The system focuses on business-rule correctness, pricing, promotional-code validation, capacity management, persistent booking data, and historical price reconstruction.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest

## Core Features

- View available cruises
- Passenger validation
- Adult and child pricing
- Group discounts
- Optional services
- Promotional codes
- Promotional usage limits
- 12% tax calculation
- Detailed price breakdown
- Cruise capacity management
- Booking confirmation
- Unique booking references
- Historical pricing snapshots
- Booking retrieval
- Automated tests

## Project Structure

```text
odysseus-practical-assessment/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   │
│   ├── routes/
│   │   ├── cruises.py
│   │   ├── quotes.py
│   │   └── bookings.py
│   │
│   └── services/
│       ├── pricing.py
│       ├── promotions.py
│       └── booking.py
│
├── tests/
│   ├── test_pricing.py
│   ├── test_promotions.py
│   └── test_booking.py
│
├── BusinessRequirements.md
├── TechnicalApproach.md
├── UnitTestCases.md
├── PROMPTS.md
├── requirements.txt
└── README.md