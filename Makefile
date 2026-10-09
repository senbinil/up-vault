.PHONY: run lint lint-fix test create-db

run:
	uv run uvicorn up_vault.main:app --reload

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

test:
	uv run pytest

create-db:
	uv run python scripts/create_db.py
