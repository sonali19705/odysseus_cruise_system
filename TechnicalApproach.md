# Technical Approach

## 1. Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- Git / GitHub

A frontend is intentionally not implemented because the assessment focuses on business rules, data modelling, pricing, persistence, API development, and testing.

SQLite was selected because it provides persistent storage without requiring external database setup, which is appropriate for a time-constrained assessment. SQLAlchemy keeps database access separated from business logic and allows the database to be changed later if required.

---

## 2. Architecture

The application follows a lightweight layered architecture:

```text
Client / Swagger
      ↓
FastAPI API Routes
      ↓
Service Layer
      ↓
SQLAlchemy ORM
      ↓
SQLite Database