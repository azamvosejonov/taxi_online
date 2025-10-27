# Royal Taxi API - Makefile
# Project management commands

.PHONY: help clean

# Default target
help: ## Show this help message
	@echo "Royal Taxi API - Available Commands"
	@echo "==================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Cleanup commands
clean: ## Clean temporary files
	@echo "Cleaning up temporary files..."
	rm -rf __pycache__ */__pycache__
	rm -rf .pytest_cache
	@echo "Cleanup complete"

clean-logs: ## Clean application logs
	rm -rf logs/*
	@echo "Logs cleaned"

clean-uploads: ## Clean uploaded files (⚠️ destroys uploaded data)
	rm -rf uploads/*
	@echo "Uploads cleaned"
	docker-compose ps
	@echo ""
	@echo "=== Health Endpoints ==="
	@echo "API Health: http://localhost:8000/health"
	@echo "Flower: http://localhost:8050"
	@echo "Database: postgresql://localhost:15432/royaltaxi"

# SSL/TLS setup (for production)
ssl-setup: ## Setup SSL certificates (requires domain)
	@echo "Setting up SSL certificates..."
	@echo "Make sure your domain points to this server"
	sudo certbot certonly --standalone -d $$(grep -oP 'CORS_ORIGINS=\K[^,]*' .env | sed 's|https://||')
	sudo cp /etc/letsencrypt/live/$$(grep -oP 'CORS_ORIGINS=\K[^,]*' .env | sed 's|https://||')/fullchain.pem ./ssl/
	sudo cp /etc/letsencrypt/live/$$(grep -oP 'CORS_ORIGINS=\K[^,]*' .env | sed 's|https://||')/privkey.pem ./ssl/
	@echo "SSL certificates installed"

# Development utilities
test: ## Run tests
	docker-compose exec app pytest

shell: ## Open shell in app container
	docker-compose exec app bash

shell-db: ## Open shell in database container
	docker-compose exec db bash

# Update commands
update: ## Update all services and rebuild
	docker-compose pull
	docker-compose build --no-cache
	docker-compose up -d

# Status and info
status: ## Show Docker status
	docker-compose ps
	@echo ""
	docker stats --no-stream

info: ## Show system information
	@echo "=== Docker Version ==="
	docker --version
	docker-compose --version
	@echo ""
	@echo "=== Images ==="
	docker images | grep royaltaxi
	@echo ""
	@echo "=== Volumes ==="
	docker volume ls | grep royaltaxi
	@echo ""
	@echo "=== Networks ==="
	docker network ls | grep royaltaxi
