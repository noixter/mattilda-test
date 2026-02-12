# Mattilda Test - School Management API

A FastAPI-based school management system for tracking students, schools, invoices, and payments.

## Tech Stack

- **FastAPI** - Async web framework
- **PostgreSQL** - Database with async SQLAlchemy ORM
- **Docker** - Containerized deployment
- **pytest** - Testing framework
- **uv** - Python package manager

## Business Features

The API implements two core business services:

### School Service
- **Get School Students**: Retrieves all students enrolled in a school with filtering by active/deactivated status and pagination support
- **Calculate School Debt**: Computes the total outstanding debt for a school by summing all pending (unpaid) invoices

### Student Service
- **Financial Status**: Calculates a student's complete financial overview:
  - `total_paid`: Sum of all payments made across all invoices
  - `total_debt`: Sum of all pending (unpaid) invoice amounts

## Project Structure

```
domain/
├── models/          # Pydantic models (Student, School, Invoice, Payment)
└── services/        # Business logic (SchoolService, StudentService)

infrastructure/
├── database/        # SQLAlchemy ORM and async engine
└── repositories/    # Data access layer (StudentRepository, SchoolRepository, InvoiceRepository)

routers/             # FastAPI endpoints
tests/
└── integration/     # Integration tests with in-memory SQLite
```

## Getting Started

### Using Makefile

```bash
# Start all services
make up
docker compose up db api -d

# View logs
make logs
docker compose logs -f api

# Populate database with sample data
make fixtures
docker compose exec api uv run python infrastructure/database/fixtures.py

# Stop services
make down
docker compose down

# Clean up containers and volumes
make clean
docker compose down -v
```

## API Endpoints

go to `http://localhost:8000/docs` to see the interactive documentation

### Students
- `GET /students/` - List students (paginated)
- `POST /students/` - Create student
- `GET /students/{id}` - Get student
- `DELETE /students/{id}` - Delete student
- `GET /students/{id}/financial-status` - Get financial overview

### Schools
- `GET /schools/` - List schools (paginated)
- `POST /schools/` - Create school
- `GET /schools/{id}` - Get school
- `DELETE /schools/{id}` - Delete school
- `GET /schools/{id}/students` - List school students
- `GET /schools/{id}/debt` - Get school debt

### Invoices
- `GET /invoices/` - List invoices (paginated, filterable by school/student)
- `POST /invoices/` - Create invoice
- `DELETE /invoices/{id}` - Delete invoice
- `GET /invoices/payments` - List payments
- `POST /invoices/payments` - Create payment
- `DELETE /invoices/payments/{id}` - Delete payment

## Running Tests

```bash
# Run all tests
docker compose exec api uv run pytest

# Run integration tests only
docker compose exec api uv run pytest tests/integration/

# Run with verbose output
docker compose exec api uv run pytest -v
```

## Development

The application uses:
- **Repository Pattern**: Domain-specific repositories for data access
- **Service Layer**: Business logic separated from API routes
- **Async/Await**: Full async support for database operations
- **Pagination**: Integrated with `fastapi-pagination`