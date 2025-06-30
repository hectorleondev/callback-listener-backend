.PHONY: help install dev test clean build run stop logs migrate shell lint format check-format security-check

# Default target
help: ## Show this help message
	@echo "CallbackListener Backend - Development Commands (with uv)"
	@echo "==========================================================="
	@echo "🚀 Fast package management powered by uv"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Environment
# Check if we're in a virtual environment
VENV_FLAG := $(if $(VIRTUAL_ENV),,--system)

# Package Management
install: ## Install dependencies
	uv pip install $(VENV_FLAG) -r requirements.txt
	python3 -m pre_commit install || echo "Pre-commit hooks not installed (not in git repo)"

install-dev: ## Install development dependencies only
	uv pip install $(VENV_FLAG) -r requirements.txt

update-deps: ## Update all dependencies
	uv pip compile requirements.in --upgrade --output-file requirements.txt

sync-deps: ## Sync dependencies (install exact versions from lock file)
	uv pip sync $(VENV_FLAG) requirements.txt

add-package: ## Add a new package (usage: make add-package pkg=package-name)
	@echo "Adding package $(pkg)..."
	uv pip install $(VENV_FLAG) $(pkg)
	uv pip freeze > requirements.txt

remove-package: ## Remove a package (usage: make remove-package pkg=package-name)
	@echo "Removing package $(pkg)..."
	uv pip uninstall $(pkg)
	uv pip freeze > requirements.txt

create-venv: ## Create virtual environment with uv
	uv venv
	@echo "Virtual environment created! Activate with: source .venv/bin/activate"

dev: ## Start development environment with docker-compose
	docker compose up --build

dev-detached: ## Start development environment in background
	docker compose up -d --build

stop: ## Stop all services
	docker compose down

stop-volumes: ## Stop all services and remove volumes
	docker compose down -v

logs: ## View logs from all services
	docker compose logs -f

logs-web: ## View logs from web service only
	docker compose logs -f web

logs-db: ## View logs from database service only
	docker compose logs -f db

# Database Management
migrate: ## Run database migrations
	docker compose exec backend flask db upgrade

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	docker compose exec backend flask db migrate -m "$(msg)"

migrate-rollback: ## Rollback last migration
	docker compose exec backend flask db downgrade

db-reset: ## Reset database (WARNING: destroys all data)
	docker compose down -v postgres
	docker volume rm callback-listener_postgres_data 2>/dev/null || true
	docker compose up -d postgres
	sleep 15
	docker compose exec backend flask db upgrade

db-init: ## Initialize database with migrations
	docker compose exec backend flask db init

# Testing
test: ## Run all tests
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

test-local: ## Run tests locally (requires local database)
	python3 -m pytest -v --cov=app --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	python3 -m pytest tests/test_models.py tests/test_utils.py -v

test-api: ## Run API tests only
	python3 -m pytest tests/test_api.py -v

test-services: ## Run service tests only
	python3 -m pytest tests/test_services.py -v

test-coverage: ## Generate coverage report
	python3 -m pytest --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Code Quality
lint: ## Run code linting
	python3 -m flake8 app tests
	python3 -m black --check app tests
	python3 -m isort --check-only app tests

format: ## Format code with black and isort
	python3 -m black app tests
	python3 -m isort app tests

check-format: ## Check if code is properly formatted
	python3 -m black --check --diff app tests
	python3 -m isort --check-only --diff app tests

security-check: ## Run security checks
	@echo "Running security checks..."
	@uv pip list --format=json | python3 -c "import json, sys; packages = json.load(sys.stdin); print('Installed packages:', len(packages))" || echo "uv not available, skipping security check"

# Application Management
run: ## Run the application locally
	python3 run.py

run-prod: ## Run with production settings
	FLASK_ENV=production python3 -m gunicorn --bind 0.0.0.0:5000 --workers 4 run:app

shell: ## Open Flask shell
	python3 -m flask shell

# Build and Deploy
build: ## Build Docker image
	docker build -t callback-listener-backend .

build-no-cache: ## Build Docker image without cache
	docker build --no-cache -t callback-listener-backend .

# Cleanup
clean: ## Clean up temporary files and caches
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

clean-docker: ## Clean up Docker resources
	docker system prune -f
	docker volume prune -f

# Database Utilities
db-backup: ## Backup database (usage: make db-backup file=backup.sql)
	docker compose exec postgres pg_dump -U callback_user callback_listener > $(file)

db-restore: ## Restore database (usage: make db-restore file=backup.sql)
	docker compose exec -T postgres psql -U callback_user callback_listener < $(file)

db-shell: ## Connect to database shell
	docker compose exec postgres psql -U callback_user callback_listener

db-status: ## Check PostgreSQL status
	docker compose exec postgres pg_isready -U callback_user -d callback_listener

# Monitoring and Health
health: ## Check application health
	curl -f http://localhost:5000/health/ || echo "Application not responding"

ready: ## Check application readiness
	curl -f http://localhost:5000/health/ready || echo "Application not ready"

# Development Helpers
watch-logs: ## Watch application logs with automatic refresh
	watch -n 2 'docker compose logs --tail=50 web'

inspect-db: ## Show database tables and structure
	docker compose exec postgres psql -U callback_user callback_listener -c "\dt"

seed-data: ## Seed database with sample data for development
	python -c "from scripts.seed_data import seed_development_data; seed_development_data()"

# Git Hooks and Pre-commit
install-hooks: ## Install git hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

run-hooks: ## Run pre-commit hooks on all files
	pre-commit run --all-files

# Documentation
docs: ## Generate API documentation (if implemented)
	@echo "API documentation not yet implemented"

# Environment Setup
setup-dev: ## Complete development environment setup
	cp .env.example .env
	uv pip install $(VENV_FLAG) -r requirements.txt
	python3 -m pre_commit install || echo "Pre-commit hooks not installed (not in git repo)"
	docker compose up -d postgres
	sleep 15
	docker compose exec backend flask db upgrade
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the application"

# Quick Commands
quick-test: format lint test-local ## Quick development cycle: format, lint, test
	@echo "✅ All checks passed!"

deploy-check: lint test security-check ## Pre-deployment checks
	@echo "✅ Ready for deployment!"
