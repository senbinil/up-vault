.PHONY: run lint lint-fix test

run:
	uv run uvicorn up_vault.main:app --reload

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

test:
	uv run pytest