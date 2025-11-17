# Development Guide

## Setup

```bash
# Install uv
pip install uv -U

# Sync dependencies
uv sync -U

# Install with dev dependencies
uv sync --dev -U
```

## Development Workflow

### Code Quality

```bash
# Format code
uv run ruff format src tests

# Check formatting
uv run ruff format --check src tests

# Lint code
uv run ruff check src tests

# Auto-fix lint issues
uv run ruff check --fix src tests

# Type check
uv run mypy --pretty src
```

### Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run tests in parallel
uv run pytest -n auto

# Run specific test file
uv run pytest tests/test_parser.py

# Run with specific marker
uv run pytest -m unit
uv run pytest -m integration

# Fail fast
uv run pytest -x

# Verbose output
uv run pytest -vv
```

### Running the Translator

```bash
# Run translator
uv run haproxy-translate config.hap -o haproxy.cfg

# Validate only
uv run haproxy-translate config.hap --validate

# Watch mode
uv run haproxy-translate config.hap -o haproxy.cfg --watch

# Debug mode
uv run haproxy-translate config.hap --debug
```

### Complete Quality Check

```bash
# Run all checks in sequence
uv run ruff check --fix src tests && \
uv run ruff format src tests && \
uv run mypy --pretty src && \
uv run pytest --cov
```

## Project Structure

```
haproxy-config-translator/
├── src/haproxy_translator/
│   ├── parsers/          # Pluggable parser system
│   ├── ir/               # Intermediate representation
│   ├── grammars/         # Lark DSL grammar
│   ├── transformers/     # Template expansion, variable resolution
│   ├── validators/       # Semantic validation
│   ├── lua/              # Lua extraction and management
│   ├── codegen/          # HAProxy code generator
│   ├── cli/              # Command-line interface
│   └── utils/            # Error handling, helpers
├── tests/                # Test suite
├── examples/             # Example configurations
└── docs/                 # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks: `uv run ruff check --fix src tests && uv run ruff format src tests && uv run mypy --pretty src && uv run pytest`
5. Commit your changes
6. Push and create a pull request

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite: `uv run pytest --cov`
4. Create git tag: `git tag v0.1.0`
5. Push tag: `git push --tags`
6. Build: `uv build`
7. Publish: `uv publish`
