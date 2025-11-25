.PHONY: help up down restart build logs logs-app logs-db clean rebuild test shell db-shell

help:
	@echo "FastAPI Backend - Docker Commands"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  up          - Start backend and database containers"
	@echo "  down        - Stop all containers"
	@echo "  restart     - Restart all containers"
	@echo "  build       - Build the Docker images"
	@echo "  rebuild     - Rebuild and restart containers"
	@echo "  logs        - View logs from all containers"
	@echo "  logs-app    - View logs from FastAPI app only"
	@echo "  logs-db     - View logs from PostgreSQL only"
	@echo "  clean       - Stop containers and remove volumes (deletes data)"
	@echo "  test        - Run tests inside container"
	@echo "  shell       - Open shell in FastAPI container"
	@echo "  db-shell    - Open PostgreSQL shell"

up:
	@echo "Starting backend and database..."
	docker-compose up -d
	@echo "Services started! Backend: http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"

down:
	@echo "Stopping containers..."
	docker-compose down

restart:
	@echo "Restarting containers..."
	docker-compose restart

build:
	@echo "Building Docker images..."
	docker-compose build

rebuild:
	@echo "Rebuilding and starting containers..."
	docker-compose up -d --build

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f fastapi-app

logs-db:
	docker-compose logs -f postgres

clean:
	@echo "Stopping containers and removing volumes..."
	docker-compose down -v
	@echo "All containers and data removed!"

test:
	docker-compose exec fastapi-app pytest

shell:
	docker-compose exec fastapi-app /bin/bash

db-shell:
	docker-compose exec postgres psql -U fastapi_user -d fastapi_db
