# Changelog

All notable changes to the HAProxy Configuration Translator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-17

### Added
- **Listen Section**: Fully implemented listen section with complete grammar and transformer support
  - Combines frontend and backend functionality
  - Supports binds, ACLs, servers, health checks, options, timeouts
  - 4 comprehensive test cases added
- **Additional Balance Algorithms**: static-rr, first, hdr, rdp-cookie
- **Server SSL Enhancements**: SNI (Server Name Indication) and ALPN support
- **HTTP Timeouts**: timeout_http_request and timeout_http_keep_alive for security and performance
- **Frontend Enhancements**: monitor_uri for health check endpoints
- **Backend Enhancements**: default_server for default server options
- **Comprehensive Documentation**:
  - FEATURES.md: Complete HAProxy 3.0 feature parity analysis (~90% coverage)
  - USAGE.md: 850+ line comprehensive usage guide with examples
  - README.md: Complete overhaul with current status and roadmap
  - 5 production-ready example configurations
  - Modern manage.sh build script

### Changed
- Updated README.md with project status and comprehensive feature matrix
- Enhanced IR nodes with new fields for all features
- Grammar expanded to support all new features

### Fixed
- Listen section enabled (was disabled due to grammar conflicts)
- Type annotations in listen_section transformer

### Test Coverage
- 190 tests passing (up from 186)
- 2 skipped, 3 xfailed (Lua extraction - pending parser integration)
- 86% code coverage maintained
- All quality gates passing (ruff, mypy)

### Documentation
- Created FEATURES.md with detailed HAProxy feature parity
- Created USAGE.md with comprehensive usage guide
- Created examples/ directory with 5 real-world configurations
- Updated README.md with current project status
- Created manage.sh for modern build/test/install workflow

### Production Readiness
- ~90% HAProxy feature parity for common use cases
- All high-priority features implemented
- Comprehensive test coverage
- Type-safe throughout
- Clean code generation verified

## [0.2.0] - 2025-01-16 (Previous Session)

### Added
- Complete transformation pipeline integration
- Multi-pass variable resolution for nested references
- Bare variable interpolation in bind addresses
- ACL block syntax support
- Comprehensive CLI tests (65% CLI coverage)
- Auto-directory creation for output files

### Fixed
- Parser support for `${var}:${port}` syntax without quotes
- ACL block parsing
- Nested variable resolution
- ValidationError propagation

### Test Coverage
- 186 tests passing
- 0 failing
- 79% → 86% coverage increase

## [0.1.0] - Initial Release

### Added
- DSL parser with Lark
- Intermediate Representation (IR) with frozen dataclasses
- Template system
- Variable support with string interpolation
- Loop unrolling
- Semantic validation
- HAProxy code generation
- Lua script extraction
- CLI interface
- Comprehensive test suite

[0.3.0]: https://github.com/haproxy/config-translator/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/haproxy/config-translator/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/haproxy/config-translator/releases/tag/v0.1.0
