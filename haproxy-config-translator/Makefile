.PHONY: help install dev clean lint format typecheck test test-cov test-fast check-all translate

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)HAProxy Config Translator - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick start:$(NC)"
	@echo "  make install    # Install dependencies"
	@echo "  make dev        # Install dev dependencies"
	@echo "  make check-all  # Run all quality checks"
	@echo "  make test       # Run tests"

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv sync

dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	uv sync --dev

clean: ## Clean build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf htmlcov coverage.xml .coverage

# Code quality
lint: ## Run ruff linter
	@echo "$(BLUE)Running linter...$(NC)"
	uv run ruff check src tests

lint-fix: ## Run ruff linter and auto-fix issues
	@echo "$(BLUE)Running linter with auto-fix...$(NC)"
	uv run ruff check --fix src tests

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format src tests

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	uv run ruff format --check src tests

typecheck: ## Run mypy type checker
	@echo "$(BLUE)Running type checker...$(NC)"
	uv run mypy --pretty src

# Testing
test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run pytest --cov
	@echo "$(GREEN)Coverage report: htmlcov/index.html$(NC)"

test-fast: ## Run tests with fail-fast
	@echo "$(BLUE)Running tests (fail-fast)...$(NC)"
	uv run pytest -x

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	uv run pytest -m unit

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	uv run pytest -m integration

test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	uv run pytest -vv

# Combined checks
check-all: lint format-check typecheck test ## Run all quality checks
	@echo "$(GREEN)All checks passed!$(NC)"

check-fix: lint-fix format typecheck ## Run all quality checks with auto-fix
	@echo "$(GREEN)All checks completed with auto-fix!$(NC)"

# Translation
translate: ## Run translator CLI (requires config file)
	@echo "$(BLUE)Running translator...$(NC)"
	uv run python -m haproxy_translator.cli.main

# Development helpers
watch-test: ## Watch for changes and run tests
	@echo "$(BLUE)Watching for changes...$(NC)"
	uv run pytest-watch

coverage-html: test-cov ## Open coverage report in browser
	@echo "$(BLUE)Opening coverage report...$(NC)"
	@python -m webbrowser htmlcov/index.html || open htmlcov/index.html || xdg-open htmlcov/index.html

# Git helpers
pre-commit: check-fix ## Run checks before committing
	@echo "$(GREEN)Ready to commit!$(NC)"

# Build
build: ## Build package
	@echo "$(BLUE)Building package...$(NC)"
	uv build

# Documentation
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	@echo "$(YELLOW)Documentation not yet set up$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation not yet set up$(NC)"
