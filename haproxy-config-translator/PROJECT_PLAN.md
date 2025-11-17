# HAProxy Config Translator - Project Plan

## Overview

Complete implementation plan for a production-ready HAProxy configuration translator with comprehensive testing, documentation, and validation.

## Project Status

- **Phase**: Development
- **Version**: 0.1.0
- **Target**: Production-ready v1.0.0

---

## Implementation Phases

### Phase 1: Development Infrastructure ✅ IN PROGRESS

**Goal**: Set up comprehensive development tooling and validation

- [x] Configure ruff for linting and formatting
- [x] Configure mypy for type checking
- [x] Configure pytest with coverage
- [x] Set up uv scripts for common tasks
- [ ] Create Makefile for convenience commands
- [ ] Add pre-commit hooks
- [ ] Configure GitHub Actions CI/CD

**Validation**:
```bash
uv run lint-fix          # Auto-fix lint issues
uv run format            # Format code
uv run typecheck         # Type check
uv run test              # Run tests
uv run check-all         # Run all checks
```

---

### Phase 2: Core Parser Fixes 🔧 PENDING

**Goal**: Fix all Lark grammar issues and ensure parser works correctly

#### Task 2.1: Fix Grammar Conflicts
- [ ] Resolve reduce/reduce conflicts in expression grammar
- [ ] Simplify expression precedence rules
- [ ] Fix template variable parsing
- [ ] Test all grammar rules with unit tests

**Files**:
- `src/haproxy_translator/grammars/haproxy_dsl.lark`

**Tests**:
- `tests/test_parser/test_grammar.py`
- `tests/test_parser/test_expressions.py`

#### Task 2.2: Improve Transformer Robustness
- [ ] Add comprehensive error handling
- [ ] Validate all dataclass constructions
- [ ] Handle edge cases (empty sections, missing fields)
- [ ] Add source location tracking

**Files**:
- `src/haproxy_translator/transformers/dsl_transformer.py`

**Tests**:
- `tests/test_transformers/test_dsl_transformer.py`

---

### Phase 3: Transformation Layer 🔄 PENDING

**Goal**: Implement all transformation logic

#### Task 3.1: Template Expansion
- [ ] Implement template resolution
- [ ] Support template inheritance
- [ ] Handle template spreading (`@template_name`)
- [ ] Validate template references

**Files**:
- `src/haproxy_translator/transformers/template_expander.py`

**Tests**:
- `tests/test_transformers/test_template_expansion.py`

**Example**:
```haproxy-dsl
template server_defaults {
  check: true
  inter: 3s
}

server web1 {
  address: "10.0.1.1"
  port: 8080
  @server_defaults  # Expands template
}
```

#### Task 3.2: Variable Resolution
- [ ] Implement variable lookup
- [ ] Support environment variable substitution
- [ ] Handle default values
- [ ] Validate variable references

**Files**:
- `src/haproxy_translator/transformers/variable_resolver.py`

**Tests**:
- `tests/test_transformers/test_variable_resolution.py`

**Example**:
```haproxy-dsl
let backend_port = env("BACKEND_PORT") ?? 8080
let ssl_cert = "${SSL_CERT:/etc/ssl/default.pem}"
```

#### Task 3.3: Loop Unrolling
- [ ] Implement for-loop expansion
- [ ] Support range syntax (1..10)
- [ ] Support list iteration
- [ ] Handle nested loops

**Files**:
- `src/haproxy_translator/transformers/loop_unroller.py`

**Tests**:
- `tests/test_transformers/test_loop_unrolling.py`

**Example**:
```haproxy-dsl
servers {
  for i in 1..5 {
    server "web${i}" {
      address: "10.0.1.${i}"
      port: 8080
    }
  }
}
```

---

### Phase 4: Validation Framework ✔️ PENDING

**Goal**: Comprehensive configuration validation

#### Task 4.1: Semantic Validation
- [ ] Backend reference validation
- [ ] ACL reference validation
- [ ] Mode compatibility checks
- [ ] Health check validation

**Files**:
- `src/haproxy_translator/validators/semantic.py`

**Tests**:
- `tests/test_validators/test_semantic_validation.py`

#### Task 4.2: Type Validation
- [ ] Port range validation (1-65535)
- [ ] Timeout format validation
- [ ] IP address validation
- [ ] Path validation

**Files**:
- `src/haproxy_translator/validators/type_checker.py`

**Tests**:
- `tests/test_validators/test_type_validation.py`

#### Task 4.3: Circular Dependency Detection
- [ ] Detect circular backend references
- [ ] Detect circular ACL dependencies
- [ ] Provide helpful error messages

**Files**:
- `src/haproxy_translator/validators/dependency_checker.py`

**Tests**:
- `tests/test_validators/test_dependency_detection.py`

---

### Phase 5: Code Generator Enhancements 🎨 PENDING

**Goal**: Produce clean, optimized HAProxy configs

#### Task 5.1: Formatting Improvements
- [ ] Consistent indentation
- [ ] Proper line wrapping
- [ ] Comment preservation
- [ ] Section ordering

**Files**:
- `src/haproxy_translator/codegen/haproxy.py`
- `src/haproxy_translator/codegen/formatter.py`

**Tests**:
- `tests/test_codegen/test_formatting.py`

#### Task 5.2: Optimization
- [ ] Merge duplicate ACLs
- [ ] Combine similar rules
- [ ] Remove unused sections
- [ ] Optimize server lists

**Files**:
- `src/haproxy_translator/codegen/optimizer.py`

**Tests**:
- `tests/test_codegen/test_optimization.py`

---

### Phase 6: Comprehensive Test Suite 🧪 PENDING

**Goal**: 95%+ test coverage with comprehensive edge case testing

#### Task 6.1: Unit Tests
- [ ] Parser unit tests (grammar rules)
- [ ] Transformer unit tests (each transformation)
- [ ] Validator unit tests (each validation rule)
- [ ] Code generator unit tests (each section)
- [ ] Lua manager unit tests

**Coverage Target**: 90%+ for each module

#### Task 6.2: Integration Tests
- [ ] End-to-end translation tests
- [ ] Multi-file configuration tests
- [ ] Error handling tests
- [ ] CLI integration tests

**Files**:
- `tests/integration/test_end_to_end.py`
- `tests/integration/test_cli.py`

#### Task 6.3: Edge Case Tests
- [ ] Empty configurations
- [ ] Extremely large configurations
- [ ] Malformed input
- [ ] Unicode and special characters
- [ ] Circular dependencies
- [ ] Missing required fields

**Files**:
- `tests/edge_cases/`

#### Task 6.4: Regression Tests
- [ ] Real-world HAProxy configs
- [ ] Complex configurations
- [ ] Performance benchmarks

**Files**:
- `tests/regression/`

---

### Phase 7: Additional Parsers 📦 PENDING

**Goal**: Support multiple input formats

#### Task 7.1: YAML Parser
- [ ] Implement YAML parser
- [ ] Support YAML anchors/aliases
- [ ] Add YAML-specific tests

**Files**:
- `src/haproxy_translator/parsers/yaml_parser.py`

**Tests**:
- `tests/test_parsers/test_yaml_parser.py`

#### Task 7.2: TOML Parser (Optional)
- [ ] Implement TOML parser
- [ ] Add TOML-specific tests

**Files**:
- `src/haproxy_translator/parsers/toml_parser.py`

**Tests**:
- `tests/test_parsers/test_toml_parser.py`

---

### Phase 8: Documentation 📚 PENDING

**Goal**: Comprehensive documentation for users and developers

#### Task 8.1: User Documentation
- [ ] Getting started guide
- [ ] Installation instructions
- [ ] DSL syntax reference
- [ ] Configuration examples
- [ ] Migration guide (from native HAProxy)
- [ ] CLI reference
- [ ] Troubleshooting guide

**Files**:
- `docs/user-guide/getting-started.md`
- `docs/user-guide/dsl-reference.md`
- `docs/user-guide/examples.md`
- `docs/user-guide/migration.md`

#### Task 8.2: Developer Documentation
- [ ] Architecture overview
- [ ] Contributing guide
- [ ] API reference
- [ ] Adding new parsers
- [ ] Testing guide

**Files**:
- `docs/dev-guide/architecture.md`
- `docs/dev-guide/contributing.md`
- `docs/dev-guide/api-reference.md`

#### Task 8.3: API Documentation
- [ ] Generate API docs with Sphinx/mkdocs
- [ ] Docstring coverage
- [ ] Code examples in docstrings

---

### Phase 9: Performance & Optimization ⚡ PENDING

**Goal**: Fast, efficient translation

#### Task 9.1: Profiling
- [ ] Profile parser performance
- [ ] Profile transformation performance
- [ ] Identify bottlenecks

**Tools**:
- `cProfile`, `py-spy`, `line_profiler`

#### Task 9.2: Optimization
- [ ] Optimize hot paths
- [ ] Cache compiled grammars
- [ ] Parallelize independent operations

#### Task 9.3: Benchmarking
- [ ] Create benchmark suite
- [ ] Measure translation speed
- [ ] Compare with baseline

**Files**:
- `benchmarks/`

---

### Phase 10: Production Readiness 🚀 PENDING

**Goal**: Ready for production use

#### Task 10.1: Error Handling
- [ ] User-friendly error messages
- [ ] Suggestions for fixes
- [ ] Detailed stack traces in debug mode

#### Task 10.2: CLI Enhancements
- [ ] Progress indicators
- [ ] Color-coded output
- [ ] JSON output mode
- [ ] Diff mode (show changes)

#### Task 10.3: Packaging
- [ ] PyPI package
- [ ] Docker image
- [ ] Homebrew formula
- [ ] Release automation

#### Task 10.4: CI/CD
- [ ] GitHub Actions workflow
- [ ] Automated testing
- [ ] Automated releases
- [ ] Code quality checks

**Files**:
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`

---

## Testing Strategy

### Test Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Parsers | 95% | 0% |
| Transformers | 95% | 0% |
| Validators | 95% | 0% |
| Code Generator | 90% | 0% |
| CLI | 80% | 0% |
| **Overall** | **90%** | **0%** |

### Test Types

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test full translation pipeline
4. **Regression Tests**: Prevent regressions
5. **Performance Tests**: Ensure acceptable performance

---

## Quality Gates

Before each release, ensure:

- [ ] `uv run lint` passes with no errors
- [ ] `uv run format-check` passes
- [ ] `uv run typecheck` passes with no errors
- [ ] `uv run test-cov` achieves 90%+ coverage
- [ ] All integration tests pass
- [ ] Documentation is up-to-date
- [ ] CHANGELOG is updated
- [ ] Version is bumped appropriately

---

## Development Workflow

### Daily Development

```bash
# 1. Start development
uv sync --dev

# 2. Make changes

# 3. Run checks frequently
uv run lint-fix          # Auto-fix issues
uv run format            # Format code
uv run typecheck         # Type check

# 4. Run tests
uv run test-fast         # Fast fail
uv run test-unit         # Unit tests only

# 5. Before committing
uv run check-all         # Full validation
```

### Before Pull Request

```bash
# Full test suite
uv run test-cov

# Check coverage
open htmlcov/index.html

# Ensure quality gates pass
uv run check-all
```

---

## Milestones

### Milestone 1: Core Functionality (v0.1.0)
- ✅ Parser infrastructure
- ✅ Basic DSL support
- ✅ Code generator
- ✅ CLI tool
- Target: Week 1

### Milestone 2: Complete Transformations (v0.2.0)
- [ ] Template expansion
- [ ] Variable resolution
- [ ] Loop unrolling
- [ ] Basic validation
- Target: Week 2

### Milestone 3: Comprehensive Testing (v0.3.0)
- [ ] 90%+ test coverage
- [ ] Integration tests
- [ ] Edge case tests
- Target: Week 3

### Milestone 4: Production Ready (v1.0.0)
- [ ] Full documentation
- [ ] Multiple parsers (YAML)
- [ ] Performance optimization
- [ ] CI/CD pipeline
- Target: Week 4

---

## Success Criteria

A successful v1.0.0 release includes:

1. **Functionality**
   - Full DSL support
   - All transformations working
   - Comprehensive validation
   - Clean code generation

2. **Quality**
   - 90%+ test coverage
   - All quality gates passing
   - No critical bugs
   - Performance acceptable (<1s for typical configs)

3. **Documentation**
   - Complete user guide
   - Developer documentation
   - API reference
   - Real-world examples

4. **Usability**
   - Intuitive CLI
   - Clear error messages
   - Good performance
   - Easy installation

---

## Current Sprint Tasks

### Sprint 1: Foundation & Fixes

1. ✅ Set up development tooling
2. ⏳ Fix Lark grammar conflicts
3. ⏳ Implement template expansion
4. ⏳ Create comprehensive parser tests
5. ⏳ Fix all type checking errors

**Goal**: Working parser with template support and 50%+ test coverage

---

## Appendix: Useful Commands

```bash
# Development
uv sync --dev                    # Install dependencies
uv run lint-fix                  # Fix lint issues
uv run format                    # Format code
uv run typecheck                 # Type check
uv run test                      # Run tests
uv run test-cov                  # Run tests with coverage
uv run check-all                 # Run all checks

# Testing
uv run test-unit                 # Unit tests only
uv run test-integration          # Integration tests only
uv run test-fast                 # Fail fast
uv run test-verbose              # Verbose output

# Translation
uv run translate config.hap -o haproxy.cfg
uv run translate config.hap --validate
uv run translate config.hap --watch

# Coverage report
open htmlcov/index.html
```
