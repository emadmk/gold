.PHONY: help up down logs ps backend frontend migrate seed test lint observability-check security-check seam-check

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk -F':.*?##' '{printf "  %-22s %s\n", $$1, $$2}'

up:  ## Bring the dev stack up
	docker compose -f compose.dev.yml up --build -d

down:  ## Stop the dev stack
	docker compose -f compose.dev.yml down

logs:  ## Tail backend logs
	docker compose -f compose.dev.yml logs -f backend

ps:  ## List containers
	docker compose -f compose.dev.yml ps

backend:  ## Shell inside backend
	docker compose -f compose.dev.yml exec backend bash

frontend:  ## Shell inside frontend
	docker compose -f compose.dev.yml exec frontend sh

migrate:  ## Apply database migrations
	docker compose -f compose.dev.yml exec backend python manage.py makemigrations
	docker compose -f compose.dev.yml exec backend python manage.py migrate

seed:  ## Seed dev data
	docker compose -f compose.dev.yml exec backend python manage.py seed_dev

test:  ## Run backend tests
	docker compose -f compose.dev.yml exec backend pytest -q --cov

lint:  ## Run linters
	docker compose -f compose.dev.yml exec backend ruff check apps core
	docker compose -f compose.dev.yml exec backend mypy apps core
	docker compose -f compose.dev.yml exec frontend npm run lint
	docker compose -f compose.dev.yml exec frontend npm run typecheck

observability-check:  ## Verify catalogue + state machine parity (CI gate)
	docker compose -f compose.dev.yml exec backend python -m apps.audit.checks event_coverage
	docker compose -f compose.dev.yml exec backend python -m apps.audit.checks catalogue
	docker compose -f compose.dev.yml exec backend python -m apps.audit.checks sm_coverage

security-check:  ## Run bandit + pip-audit (CI gate)
	docker compose -f compose.dev.yml exec backend bandit -r apps core
	docker compose -f compose.dev.yml exec backend pip-audit

seam-check:  ## Verify roadmap seams haven't been removed (CI gate)
	docker compose -f compose.dev.yml exec backend python -c "from apps.accounts.models import User; assert hasattr(User, 'tier') and hasattr(User, 'referred_by') and hasattr(User, 'share_trades')"
	docker compose -f compose.dev.yml exec backend python -c "from apps.orders.models import Order; assert 'metadata' in {f.name for f in Order._meta.fields}"
	docker compose -f compose.dev.yml exec backend python -c "from apps.wallet.models import RialWallet; assert hasattr(RialWallet, 'currency')"
	@echo "OK: roadmap seams intact"
