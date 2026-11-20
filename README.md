# django-crm

> CRM with sales pipeline, kanban, activities and revenue forecast.

[![CI](https://github.com/dblzroch/django-crm/actions/workflows/ci.yml/badge.svg)](https://github.com/dblzroch/django-crm/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Django 5.0+](https://img.shields.io/badge/django-5.0+-blue.svg)](https://www.djangoproject.com/)

CRM system built with [Django](https://www.djangoproject.com/).
Manage leads, companies and contacts, track opportunities through a visual kanban pipeline,
log activities and forecast revenue.

## Quickstart

```bash
# Clone
git clone https://github.com/dblzroch/django-crm.git
cd django-crm

# Install (uv)
uv sync --dev

# Migrate
uv run python manage.py migrate

# Create superuser (admin access)
uv run python manage.py createsuperuser

# Run the development server
uv run python manage.py runserver
```

## How it works

- **Framework**: Django 5.x with built-in admin, ORM and authentication.
- **Storage**: SQLite (dev) / PostgreSQL (production-ready via DATABASE_URL).
- **Features**: Companies and contacts registry, lead qualification, opportunity pipeline
  with kanban board (drag & drop stages), activity logging (calls, emails, meetings),
  revenue forecast by stage and agent, Django admin for full management.
- **Tests**: `pytest` + `pytest-django` with coverage gate at 80%.
- **CI**: GitHub Actions runs ruff, mypy and pytest on every push/PR.

## Tests & quality

```bash
make test      # pytest with coverage
make lint      # ruff + mypy
make fmt       # ruff format
make migrate   # apply database migrations
```

## License

MIT
