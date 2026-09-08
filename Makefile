# Task runner for macOS / Linux. Windows users: use run.ps1 (same targets).
# Everything runs in Docker; nothing is installed on the host.

COMPOSE := docker compose
PROFILE := --profile library

.DEFAULT_GOAL := help
.PHONY: help start stop restart rebuild logs status test lint library library-stop shell clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-13s\033[0m %s\n", $$1, $$2}'

start: ## Build if needed and start the API + dashboard in the background
	$(COMPOSE) up -d --build
	$(COMPOSE) ps

stop: ## Stop and remove the containers (data is kept)
	$(COMPOSE) $(PROFILE) down

restart: stop start ## stop + start

rebuild: ## Rebuild the image from scratch and start again
	$(COMPOSE) $(PROFILE) down
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d
	$(COMPOSE) ps

logs: ## Follow the live logs (Ctrl+C to exit)
	$(COMPOSE) logs -f

status: ## Show container status
	$(COMPOSE) ps

test: ## Run the pytest suite inside a container
	$(COMPOSE) run --rm --no-deps api python -m pytest -v

lint: ## Run ruff (lint + format check) and mypy inside a container
	$(COMPOSE) run --rm --no-deps api sh -c "ruff check . && ruff format --check . && mypy"

library: ## Start the component library -> http://localhost:8502
	$(COMPOSE) $(PROFILE) up -d library
	@echo "Component library -> http://localhost:8502"

library-stop: ## Stop the component library container
	$(COMPOSE) $(PROFILE) rm -sf library

shell: ## Open a shell inside the API container
	$(COMPOSE) exec api /bin/bash

clean: ## Stop everything and ALSO delete the data volume (asks first)
	@printf 'This ALSO deletes the data volume (tasks will be lost). Type "yes": '
	@read ans && [ "$$ans" = "yes" ] \
		&& $(COMPOSE) $(PROFILE) down -v --rmi local \
		|| echo "Cancelled."
