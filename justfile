default:
    @just --list

install:
    uv sync
    cd typescript && npm install

generate:
    uv run python scripts/generate_openapi.py
    uv run python scripts/generate_dbt_schema.py
    cd typescript && npm run generate

test:
    uv run pytest
