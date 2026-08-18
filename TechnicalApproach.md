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