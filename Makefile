.PHONY: help install dev-install test lint format clean docker-build docker-up docker-down migrate demo docs

# Default target
help:
	@echo "Australian Privacy Act ADM Compliance Framework - Make Commands"
	@echo "================================================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        - Install production dependencies"
	@echo "  make dev-install    - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start development environment"
	@echo "  make test           - Run test suite"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make lint           - Run linters (flake8, mypy)"
	@echo "  make format         - Format code (black)"
	@echo "  make type-check     - Run type checking (mypy)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Start Docker services"
	@echo "  make docker-down    - Stop Docker services"
	@echo "  make docker-logs    - View Docker logs"
	@echo "  make docker-clean   - Remove Docker containers and volumes"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run database migrations"
	@echo "  make migrate-create - Create new migration"
	@echo "  make db-reset       - Reset database (DESTRUCTIVE)"
	@echo ""
	@echo "Demo & Data:"
	@echo "  make demo           - Generate demo data"
	@echo "  make seed           - Seed database with initial data"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs           - Generate documentation"
	@echo "  make docs-serve     - Serve documentation locally"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean temporary files"
	@echo "  make security       - Run security checks"
	@echo "  make validate       - Validate all configurations"
	@echo ""

# Installation
install:
	@echo "Installing production dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install --production

dev-install:
	@echo "Installing development dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install

# Development
dev:
	@echo "Starting development environment..."
	./scripts/start-dev.sh

# Testing
test:
	@echo "Running test suite..."
	cd backend && pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	cd backend && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-watch:
	@echo "Running tests in watch mode..."
	cd backend && ptw tests/

# Code Quality
lint:
	@echo "Running linters..."
	cd backend && flake8 app tests --max-line-length=120
	cd backend && mypy app --ignore-missing-imports

format:
	@echo "Formatting code..."
	cd backend && black app tests
	cd frontend && npm run format

type-check:
	@echo "Running type checking..."
	cd backend && mypy app --ignore-missing-imports

security:
	@echo "Running security checks..."
	cd backend && pip install bandit safety
	cd backend && bandit -r app
	cd backend && safety check

# Docker
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Services started. Access at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/api/docs"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	@echo "Cleaning Docker environment..."
	docker-compose down -v
	docker system prune -f

# Database
migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

migrate-create:
	@echo "Creating new migration..."
	@read -p "Migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"

migrate-rollback:
	@echo "Rolling back last migration..."
	cd backend && alembic downgrade -1

db-reset:
	@echo "WARNING: This will destroy all data!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		docker-compose exec postgres psql -U postgres -d adm_compliance -f /docker-entrypoint-initdb.d/01-schema.sql; \
	fi

# Demo & Data
demo:
	@echo "Generating demo data..."
	./scripts/generate-demo-data.sh

seed:
	@echo "Seeding database..."
	cd backend && python -m app.utils.seed_data

# Documentation
docs:
	@echo "Generating documentation..."
	cd docs && make html

docs-serve:
	@echo "Serving documentation..."
	cd docs/_build/html && python -m http.server 8080

# Utilities
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "Clean complete!"

validate:
	@echo "Validating configurations..."
	@echo "Checking Docker Compose..."
	docker-compose config
	@echo "Checking Terraform..."
	cd infrastructure/terraform && terraform validate
	@echo "Validation complete!"

# CI/CD simulation
ci:
	@echo "Running CI pipeline locally..."
	make lint
	make type-check
	make test-cov
	make security
	@echo "CI pipeline complete!"

# Production deployment
deploy-staging:
	@echo "Deploying to staging..."
	@echo "Not implemented yet"

deploy-production:
	@echo "Deploying to production..."
	@echo "WARNING: This deploys to production!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "Production deployment not implemented yet"; \
	fi

# Health check
health:
	@echo "Checking application health..."
	@curl -f http://localhost:8000/health || echo "Backend not running"
	@curl -f http://localhost:3000 || echo "Frontend not running"

# Version
version:
	@echo "ADM Compliance Framework v1.0.0"
	@python --version
	@node --version
	@docker --version
	@terraform --version

# Quick start
quickstart: docker-build docker-up
	@echo ""
	@echo "================================"
	@echo "Quick Start Complete!"
	@echo "================================"
	@echo ""
	@echo "Access points:"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/api/docs"
	@echo ""
	@echo "Default credentials:"
	@echo "  Email:    admin@example.gov.au"
	@echo "  Password: Admin123!"
	@echo ""
	@echo "Run 'make help' for more commands"
	@echo ""
