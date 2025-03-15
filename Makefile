.PHONY: build up down logs ps restart shell clean help db-shell migrate

# Project settings
PROJECT := business-card-ocr
SERVICE := api

# Container settings
CONTAINER := $(PROJECT)_$(SERVICE)_1

# Help command
help:
	@echo "Business Card OCR API - Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make build      - Build Docker containers"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs for all services"
	@echo "  make ps         - List running services"
	@echo "  make restart    - Restart all services"
	@echo "  make shell      - Open a shell in the API container"
	@echo "  make db-shell   - Open a PostgreSQL shell"
	@echo "  make migrate    - Run database migrations"
	@echo "  make clean      - Remove containers and volumes"

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

restart:
	docker-compose restart

shell:
	docker-compose exec $(SERVICE) bash

# Database commands
db-shell:
	docker-compose exec db psql -U postgres -d business_cards

migrate:
	docker-compose exec $(SERVICE) alembic upgrade head

# Clean up
clean:
	docker-compose down -v
	rm -rf uploads/*
