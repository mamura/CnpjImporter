.PHONY: install setup lint test run-info run-check-dirs run-db-ping

install:
	uv sync

setup:
	cp -n .env.example .env || true
	mkdir -p data/input data/extracted data/temp logs

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

run-info:
	uv run python -m src.cli.main info

run-check-dirs:
	uv run python -m src.cli.main check-dirs

run-db-ping:
	uv run python -m src.cli.main db-ping