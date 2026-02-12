.PHONY: help build up down restart logs shell test fixtures clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs from all services"
	@echo "  make shell      - Open a shell in the API container"
	@echo "  make test       - Run tests"
	@echo "  make fixtures   - Populate database with test data"
	@echo "  make clean      - Stop services and remove volumes"

# Build Docker images
build:
	docker compose build

# Start all services
up:
	docker compose up api db -d

# Stop all services
down:
	docker compose down

# Restart all services
restart: down up

# View logs
logs:
	docker compose logs -f api

# Open shell in API container
shell:
	docker compose exec api bash

# Run tests
test:
	docker compose run --rm test

# Populate database with fixtures
fixtures:
	docker compose exec api uv run -m infrastructure.database.fixtures

# Stop services and remove volumes
clean:
	docker compose down -v
