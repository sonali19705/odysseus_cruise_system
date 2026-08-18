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
- Git / GitHub

## Core Features

- Cruise availability and capacity validation
- Passenger validation
- Adult and child pricing
- Group discounts
- Optional services
- Promotional codes
- Promotional usage limits
- 12% tax calculation
- Detailed price breakdown
- Quote calculation
- Cruise capacity management
- Booking confirmation
- Unique booking references
- Historical pricing snapshots
- Booking retrieval
- Promotional redemption tracking
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
│   │   ├── quotes.py
│   │   └── bookings.py
│   │
│   └── services/
│       ├── pricing.py
│       └── promotions.py
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