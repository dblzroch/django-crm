.PHONY: run test lint fmt install migrate createsuperuser

install:
	uv sync --dev

run:
	uv run python manage.py runserver

test:
	uv run pytest

lint:
	uv run ruff check crmapp crm tests manage.py
	uv run mypy crmapp crm

fmt:
	uv run ruff format crmapp crm tests manage.py

migrate:
	uv run python manage.py migrate

createsuperuser:
	uv run python manage.py createsuperuser
