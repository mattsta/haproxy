#!/usr/bin/env bash

# HAProxy Configuration Translator - Management Script
# Modern replacement for Makefile with clean, encapsulated operations
#
# Usage: ./manage.sh <command> [options]
#
# Commands:
#   setup       - Install dependencies and setup development environment
#   install     - Install package (use --dev for development mode)
#   build       - Build distribution packages
#   test        - Run test suite
#   lint        - Run code quality checks
#   format      - Format code with ruff
#   typecheck   - Run type checking with mypy
#   coverage    - Run tests with coverage report
#   watch       - Run tests in watch mode
#   clean       - Clean build artifacts and cache
#   docs        - Generate documentation
#   validate    - Run all quality checks (lint + typecheck + test)
#   help        - Show this help message

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
SRC_DIR="$PROJECT_ROOT/src"
TEST_DIR="$PROJECT_ROOT/tests"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command '$1' not found"
        return 1
    fi
    return 0
}

# Commands

cmd_help() {
    cat << EOF
HAProxy Configuration Translator - Management Script

Usage: ./manage.sh <command> [options]

Commands:
  setup       Install dependencies and setup development environment
  install     Install package
              Options:
                --dev     Install with development dependencies
                --user    Install for current user only
  build       Build distribution packages (sdist and wheel)
  test        Run test suite
              Options:
                -v, --verbose    Verbose output
                -k PATTERN       Run tests matching pattern
                --failed-first   Run failed tests first
  lint        Run code quality checks (ruff)
  format      Format code with ruff
              Options:
                --check   Check formatting without modifying files
  typecheck   Run type checking with mypy
  coverage    Run tests with coverage report
              Options:
                --html    Generate HTML coverage report
  watch       Run tests in watch mode (requires pytest-watch)
  clean       Clean build artifacts and cache
              Options:
                --all     Also remove virtual environment
  docs        Generate documentation (placeholder)
  validate    Run all quality checks (lint + typecheck + test)
  help        Show this help message

Examples:
  ./manage.sh setup
  ./manage.sh install --dev
  ./manage.sh test -v
  ./manage.sh coverage --html
  ./manage.sh validate

Environment Variables:
  PYTHON      Python interpreter to use (default: python3)
  UV          Use uv instead of pip (default: auto-detect)

EOF
}

cmd_setup() {
    log_info "Setting up development environment..."

    # Check for Python
    if ! check_command python3; then
        log_error "Python 3 is required but not found"
        return 1
    fi

    PYTHON="${PYTHON:-python3}"
    log_info "Using Python: $($PYTHON --version)"

    # Check for uv or pip
    if command -v uv &> /dev/null; then
        log_info "Using uv package manager"
        UV_CMD="uv pip"
    elif check_command pip3; then
        log_info "Using pip package manager"
        UV_CMD="pip3"
    else
        log_error "Neither uv nor pip found. Please install one of them."
        return 1
    fi

    # Install package with dev dependencies
    log_info "Installing package with development dependencies..."
    cd "$PROJECT_ROOT"
    $UV_CMD install -e ".[dev]"

    log_success "Development environment setup complete!"
    log_info "You can now run: ./manage.sh test"
}

cmd_install() {
    local dev_mode=false
    local user_mode=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dev)
                dev_mode=true
                shift
                ;;
            --user)
                user_mode=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                return 1
                ;;
        esac
    done

    PYTHON="${PYTHON:-python3}"

    # Determine package manager
    if command -v uv &> /dev/null; then
        UV_CMD="uv pip"
    else
        UV_CMD="pip3"
    fi

    local install_args=""
    if $user_mode; then
        install_args="--user"
    fi

    log_info "Installing package..."
    cd "$PROJECT_ROOT"

    if $dev_mode; then
        log_info "Installing with development dependencies..."
        $UV_CMD install $install_args -e ".[dev]"
    else
        $UV_CMD install $install_args -e .
    fi

    log_success "Installation complete!"
}

cmd_build() {
    log_info "Building distribution packages..."

    PYTHON="${PYTHON:-python3}"
    cd "$PROJECT_ROOT"

    # Clean previous builds
    rm -rf dist/ build/ *.egg-info

    # Build sdist and wheel
    $PYTHON -m build

    log_success "Build complete! Packages in dist/"
    ls -lh dist/
}

cmd_test() {
    log_info "Running tests..."

    local pytest_args=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -v|--verbose)
                pytest_args="$pytest_args -v"
                shift
                ;;
            -k)
                pytest_args="$pytest_args -k $2"
                shift 2
                ;;
            --failed-first)
                pytest_args="$pytest_args --failed-first"
                shift
                ;;
            *)
                pytest_args="$pytest_args $1"
                shift
                ;;
        esac
    done

    cd "$PROJECT_ROOT"
    pytest $pytest_args

    log_success "Tests passed!"
}

cmd_lint() {
    log_info "Running code quality checks..."

    cd "$PROJECT_ROOT"

    log_info "Checking with ruff..."
    ruff check src tests

    log_success "Code quality checks passed!"
}

cmd_format() {
    local check_only=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --check)
                check_only=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                return 1
                ;;
        esac
    done

    cd "$PROJECT_ROOT"

    if $check_only; then
        log_info "Checking code formatting..."
        ruff format --check src tests
        log_success "Code formatting is correct!"
    else
        log_info "Formatting code with ruff..."
        ruff format src tests
        log_success "Code formatted!"
    fi
}

cmd_typecheck() {
    log_info "Running type checking..."

    cd "$PROJECT_ROOT"
    mypy src

    log_success "Type checking passed!"
}

cmd_coverage() {
    local html_report=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --html)
                html_report=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                return 1
                ;;
        esac
    done

    log_info "Running tests with coverage..."

    cd "$PROJECT_ROOT"

    if $html_report; then
        pytest --cov=haproxy_translator --cov-report=html --cov-report=term
        log_success "Coverage report generated!"
        log_info "HTML report: file://$PROJECT_ROOT/htmlcov/index.html"
    else
        pytest --cov=haproxy_translator --cov-report=term
        log_success "Coverage report complete!"
    fi
}

cmd_watch() {
    log_info "Running tests in watch mode..."

    if ! check_command ptw; then
        log_warning "pytest-watch not found. Installing..."
        pip install pytest-watch
    fi

    cd "$PROJECT_ROOT"
    ptw
}

cmd_clean() {
    local clean_all=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --all)
                clean_all=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                return 1
                ;;
        esac
    done

    log_info "Cleaning build artifacts..."

    cd "$PROJECT_ROOT"

    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true

    # Clean build artifacts
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf .eggs/

    # Clean test artifacts
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    rm -rf .ruff_cache/
    rm -rf htmlcov/
    rm -f .coverage

    log_success "Cleaned build artifacts!"

    if $clean_all; then
        log_warning "Removing virtual environment..."
        rm -rf venv/ .venv/
        log_success "Full clean complete!"
    fi
}

cmd_docs() {
    log_info "Documentation generation not yet implemented"
    log_info "Available documentation:"
    log_info "  - README.md        : Project overview"
    log_info "  - USAGE.md         : Usage guide"
    log_info "  - FEATURES.md      : Feature parity analysis"
    log_info "  - PROJECT_PLAN.md  : Development roadmap"
}

cmd_validate() {
    log_info "Running all quality checks..."

    local failed=false

    # Run lint
    log_info "1/3 Running lint checks..."
    if ! cmd_lint; then
        failed=true
        log_error "Lint checks failed"
    else
        log_success "Lint checks passed"
    fi

    # Run typecheck
    log_info "2/3 Running type checks..."
    if ! cmd_typecheck; then
        failed=true
        log_error "Type checks failed"
    else
        log_success "Type checks passed"
    fi

    # Run tests
    log_info "3/3 Running tests..."
    if ! cmd_test; then
        failed=true
        log_error "Tests failed"
    else
        log_success "Tests passed"
    fi

    if $failed; then
        log_error "Validation failed!"
        return 1
    else
        log_success "All validation checks passed!"
        return 0
    fi
}

# Main entry point
main() {
    if [[ $# -eq 0 ]]; then
        cmd_help
        return 0
    fi

    local command="$1"
    shift

    case "$command" in
        setup)
            cmd_setup "$@"
            ;;
        install)
            cmd_install "$@"
            ;;
        build)
            cmd_build "$@"
            ;;
        test)
            cmd_test "$@"
            ;;
        lint)
            cmd_lint "$@"
            ;;
        format)
            cmd_format "$@"
            ;;
        typecheck)
            cmd_typecheck "$@"
            ;;
        coverage)
            cmd_coverage "$@"
            ;;
        watch)
            cmd_watch "$@"
            ;;
        clean)
            cmd_clean "$@"
            ;;
        docs)
            cmd_docs "$@"
            ;;
        validate)
            cmd_validate "$@"
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            cmd_help
            return 1
            ;;
    esac
}

# Run main function
main "$@"
