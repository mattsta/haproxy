.PHONY: help install install-dev lint format typecheck test test-fast test-cov clean build docs pre-commit

# Default target
help:
	@echo "HAProxy Config Translator - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install       Install package in production mode"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  pre-commit    Install pre-commit hooks"
	@echo ""
	@echo "Quality:"
	@echo "  lint          Run ruff linter"
	@echo "  format        Format code with ruff"
	@echo "  typecheck     Run mypy type checker"
	@echo "  check         Run all quality checks (lint + typecheck)"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests with parallel execution"
	@echo "  test-fast     Run tests without coverage"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-int      Run integration tests only"
	@echo ""
	@echo "Build:"
	@echo "  build         Build distribution packages"
	@echo "  clean         Remove build artifacts and caches"
	@echo ""
	@echo "Documentation:"
	@echo "  docs          Generate documentation (placeholder)"

# Installation
install:
	uv sync

install-dev:
	uv sync --dev

pre-commit:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push

# Quality checks
lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

typecheck:
	uv run mypy src

check: lint typecheck

# Testing
test:
	uv run pytest tests -n 20 -v

test-fast:
	uv run pytest tests -n 20 -q --tb=short

test-cov:
	uv run pytest tests -n 20 --cov=src --cov-report=html --cov-report=term-missing

test-unit:
	uv run pytest tests -n 20 -m "unit or not (integration or slow)"

test-int:
	uv run pytest tests -n 20 -m integration

# Build
build: clean
	uv build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Documentation (placeholder for future)
docs:
	@echo "Documentation generation not yet implemented"
	@echo "Consider using mkdocs or sphinx"
