# Variables
PYTHON := uv run python
RUFF := uv run ruff
APP_MODULE := app.main:app
DB_CONTAINER := my_project_db

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	uv sync

.PHONY: lint
lint: ## Run linting checks with Ruff
	$(RUFF) check .

.PHONY: format
format: ## Format code with Ruff
	$(RUFF) format .

.PHONY: dev
dev: ## Run the development server
	uv run uvicorn $(APP_MODULE) --reload

.PHONY: db-up
db-up: ## Start the database container
	docker compose up -d

.PHONY: db-down
db-down: ## Stop the database container
	docker compose stop

.PHONY: db-clean
db-clean: ## Remove database volumes and restart
	docker compose down -v
	docker compose up -d

.PHONY: clean
clean: ## Remove python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
