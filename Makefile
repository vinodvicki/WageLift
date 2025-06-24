# WageLift Docker Management Makefile
# Provides easy commands for development and deployment

.PHONY: help dev prod build clean logs test lint format

# Default target
help:
	@echo "WageLift Docker Management Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment with hot reload"
	@echo "  make dev-build    - Build and start development environment"
	@echo "  make dev-logs     - View development logs"
	@echo "  make dev-stop     - Stop development environment"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Build and start production environment"
	@echo "  make prod-logs    - View production logs"
	@echo "  make prod-stop    - Stop production environment"
	@echo ""
	@echo "Management:"
	@echo "  make build        - Build all images"
	@echo "  make clean        - Remove all containers, images, and volumes"
	@echo "  make logs         - View all logs"
	@echo "  make test         - Run tests in containers"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"
	@echo ""

# Development commands
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-logs:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

dev-stop:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Production commands
prod:
	docker-compose up -d

prod-build:
	docker-compose up --build -d

prod-logs:
	docker-compose logs -f

prod-stop:
	docker-compose down

# Build commands
build:
	docker-compose build

build-frontend:
	docker-compose build frontend

build-backend:
	docker-compose build backend

# Management commands
clean:
	docker-compose down -v --remove-orphans
	docker image prune -a -f
	docker volume prune -f
	docker network prune -f

logs:
	docker-compose logs -f

# Testing commands
test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

test-backend:
	docker-compose exec backend pytest

test-frontend:
	docker-compose exec frontend npm test

# Code quality commands
lint:
	docker-compose exec backend flake8 app/
	docker-compose exec backend mypy app/
	docker-compose exec frontend npm run lint

format:
	docker-compose exec backend black app/
	docker-compose exec backend isort app/
	docker-compose exec frontend npm run lint:fix

# Database commands
db-migrate:
	docker-compose exec backend alembic upgrade head

db-reset:
	docker-compose exec backend alembic downgrade base
	docker-compose exec backend alembic upgrade head

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Backend: DOWN"
	@curl -f http://localhost:3000/api/health || echo "Frontend: DOWN"

# Setup commands
setup:
	@echo "Setting up WageLift development environment..."
	@echo "1. Copy .env.example to .env and fill in your values"
	@echo "2. Run 'make dev-build' to build and start development environment"
	@echo "3. Visit http://localhost:3000 for frontend"
	@echo "4. Visit http://localhost:8000/docs for API documentation"

# Backup commands
backup-db:
	docker-compose exec postgres pg_dump -U wagelift wagelift > backup_$(shell date +"%Y%m%d_%H%M%S").sql

restore-db:
	@echo "Usage: make restore-db BACKUP_FILE=backup_20241201_120000.sql"
	docker-compose exec -T postgres psql -U wagelift -d wagelift < $(BACKUP_FILE) 