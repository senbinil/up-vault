.PHONY: run lint lint-fix test create-db migration migrate rollback status

run:
	uv run uvicorn up_vault.main:app --reload

lint:
	uv run ruff check .
	uv run ruff format --check .

lint-fix:
	uv run ruff check . --fix
	uv run ruff format .

test:
	uv run pytest

create-db:
	uv run python scripts/create_db.py

migration:
	@test -n "$(name)" || { echo 'usage: make migration name="<message>"'; exit 1; }
	uv run alembic revision --autogenerate -m "$(name)"

migrate:
	uv run alembic upgrade head

rollback:
	uv run alembic downgrade -1

status:
	uv run alembic current
