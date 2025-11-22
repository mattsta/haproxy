# HAProxy Configuration Translator - Implementation Roadmap

**Last Updated**: 2025-11-18 (Session 3)
**Current Version**: 0.4.0
**Test Status**: 344 passing, 0 skipped, 0 failed
**Coverage**: 92%
**Linting**: 0 errors (ruff clean)
**Type Checking**: 0 errors (mypy clean)

---

## Executive Summary

The HAProxy Configuration Translator is a **solid foundation** with excellent DSL features but is **missing critical directives** needed for production deployments. This roadmap outlines the path to 100% feature parity with HAProxy 3.0.

### Current State

**Strengths:**

- ✅ Excellent DSL (variables, templates, loops, conditionals)
- ✅ Solid core load balancing and routing
- ✅ SSL/TLS hardening complete
- ✅ Lua integration fully functional
- ✅ 258 tests passing with 0 failures
- ✅ Clean, well-architected codebase

**Weaknesses:**

- ❌ Missing critical production directives (forwardfor already works via generic option!)
- ❌ No `default-server` directive (causes config duplication)
- ❌ Limited performance tuning options
- ❌ No custom logging support
- ❌ 88% test coverage (need 100%)

### Feature Coverage Analysis

| Category                | Coverage | Status           |
| ----------------------- | -------- | ---------------- |
| **DSL Features**        | 100%     | ✅ Complete      |
| **Core Load Balancing** | 100%     | ✅ Complete      |
| **SSL/TLS Hardening**   | 95%      | ✅ Near Complete |
| **Defaults Section**    | 85%      | ✅ Good          |
| **Backend Section**     | 60%      | ⚠️ Needs Work    |
| **Frontend Section**    | 50%      | ⚠️ Needs Work    |
| **Global Section**      | 30%      | ❌ Missing Many  |
| **Server Options**      | 40%      | ❌ Missing Many  |
| **Bind Options**        | 30%      | ❌ Missing Many  |

**Overall Feature Parity**: ~22% of HAProxy directives (80-90 of ~411 total)

---

## Critical Features (MUST IMPLEMENT)

These 4 features are **blocking production use** for many deployments:

### 1. `default-server` Directive ⭐ PRIORITY 1

**Status**: NOT IMPLEMENTED
**Effort**: 4-6 hours
**Impact**: CRITICAL - Eliminates massive config duplication

**Problem**: Without `default-server`, every server must repeat the same options:

```haproxy
# Current (repetitive):
backend api {
    server api1 10.0.1.1:8080 check inter 5s rise 2 fall 3 weight 100
    server api2 10.0.1.2:8080 check inter 5s rise 2 fall 3 weight 100
    server api3 10.0.1.3:8080 check inter 5s rise 2 fall 3 weight 100
}

# With default-server (clean):
backend api {
    default-server check inter 5s rise 2 fall 3 weight 100
    server api1 10.0.1.1:8080
    server api2 10.0.1.2:8080
    server api3 10.0.1.3:8080
}
```

**Implementation Plan**:

1. Add IR node `DefaultServer` in `nodes.py`
2. Add grammar rule `default_server_directive` in `haproxy_dsl.lark`
3. Add transformer in `dsl_transformer.py`
4. Update code generator to apply defaults to all servers
5. Add comprehensive tests

**Files to Modify**:

- `src/haproxy_translator/ir/nodes.py`
- `src/haproxy_translator/grammars/haproxy_dsl.lark`
- `src/haproxy_translator/transformers/dsl_transformer.py`
- `src/haproxy_translator/codegen/haproxy.py`
- `tests/test_parser/test_default_server.py` (new)

### 2. `option forwardfor` ⭐ VERIFIED WORKING

**Status**: ✅ ALREADY IMPLEMENTED (via generic option)
**Effort**: 1 hour (tests only)
**Impact**: CRITICAL - 99% of deployments need this

**Already works!** Just needs explicit tests to verify.

Test created: `tests/test_parser/test_common_options.py::test_option_forwardfor`

### 3. `option http-keep-alive` ⭐ VERIFIED WORKING

**Status**: ✅ ALREADY IMPLEMENTED (via generic option)
**Effort**: 1 hour (tests only)
**Impact**: HIGH - Performance optimization

**Already works!** Just needs explicit tests.

Test created: `tests/test_parser/test_common_options.py::test_option_http_keep_alive`

### 4. Extended Timeout Support

**Status**: PARTIAL
**Effort**: 2-3 hours
**Impact**: HIGH - Security and performance

**Currently Supported**:

- ✅ `timeout connect` (defaults/backend)
- ✅ `timeout client` (defaults/frontend)
- ✅ `timeout server` (defaults/backend)
- ✅ `timeout http-request` (defaults/frontend)
- ✅ `timeout http-keep-alive` (defaults/frontend)
- ✅ `timeout check` (defaults/backend)
- ✅ `timeout queue` (defaults)

**Missing**:

- ❌ `timeout http-request` in backend
- ❌ `timeout tunnel` (WebSocket/long connections)
- ❌ `timeout client-fin`
- ❌ `timeout server-fin`

**Implementation**: Add missing timeout rules to backend_property in grammar.

---

## High Priority Features (11 Features, 25-35 hours)

### Performance & Threading

1. **`nbthread`** - Multi-threading support (1 hr)
   - Global directive for worker threads
   - Simple addition to global section

2. **`maxsslconn`** + **`ulimit-n`** - Resource limits (2 hrs)
   - SSL connection limits
   - File descriptor limits

### Logging & Observability

3. **`log-format`** - Custom logging (4 hrs)
   - Custom log format strings
   - Variable substitution
   - Conditional logging

4. **`capture request/response header`** - Header capture (5-6 hrs)
   - Debug tool for production
   - Captures specific headers for logging

### Health Checks

5. **`http-check expect`** - Advanced health checks (3 hrs)
   - Currently: `expect status 200`
   - Missing: `expect string`, `expect rstring`, `expect ! status`

6. **Protocol-specific checks** (4 hrs)
   - `mysql-check`
   - `pgsql-check`
   - `redis-check`
   - `smtpchk`
   - `ldap-check`

### Server Options

7. **Advanced server options** (8 hrs total)
   - `slowstart` - Gradual weight increase
   - `send-proxy-v2` - PROXY protocol v2
   - `check-ssl` - SSL for health checks
   - `check-sni` - SNI for SSL checks
   - `ca-file`, `crt`, `key` - Server certificates
   - `ssl-min-ver`, `ssl-max-ver` - TLS version constraints
   - `source` - Client IP binding
   - `init-addr` - DNS resolution method

### Session Persistence

8. **Stick Tables (IR EXISTS!)** (6 hrs)
   - IR nodes already exist!
   - Grammar exists!
   - Transformers exist!
   - Just need thorough testing and bug fixes

---

## Medium Priority Features (30-40 hours)

### Load Balancing

- Additional balance algorithms: `url32`, `url32+src`, `wt6`
- `hash-type` - Consistent hashing configuration
- `hash-balance-factor` - Hash distribution control

### Connection Management

- `tcp-request connection` - Pre-TLS filtering
- `tcp-request session` - Per-session rules
- `tcp-request content` - Content inspection (PARTIAL - IR exists!)
- `tcp-response content` - Response filtering (PARTIAL - IR exists!)
- `inspect-delay` - Buffer inspection window

### HTTP Processing

- `http-after-response` - Post-response processing
- `http-error` - Custom HTTP error responses
- `return` action - Return custom response
- `set-status` - Change response status
- `normalize-uri` - URI normalization

### Bind Options

- `accept-proxy` - Accept PROXY protocol
- `defer-accept` - Defer connection acceptance
- `tcp-ut` - TCP user timeout
- `transparent` - Transparent proxy
- `interface` - Network interface binding
- `namespace` - Network namespace

### Monitoring

- `monitor fail` - Force health check failure
- `stats` - Enhanced statistics section

---

## Low Priority Features (40+ hours)

### Modern Protocols

- HTTP/2 configuration (`max-concurrent-streams`, etc.)
- HTTP/3 / QUIC support
- Caching (`cache` section, `cache-store`, `cache-use`)

### Advanced Features

- SPOE (Stream Processing Offload Engine)
- FastCGI integration (`fcgi-app`, `use-fcgi-app`)
- Compression filters
- Userlist authentication
- Resolvers for DNS discovery
- Peers/clustering
- Mailers for alerts

### Variables & Maps

- Scoped variables (`global`, `proc`, `sess`, `txn`, `req`, `res`)
- `declare` directive
- Map operations (`set-map`, `add-map`, `del-map`)
- Variable operations (`set-var`, `set-var-fmt`, `unset-var`)

---

## Test Coverage Roadmap

**Current**: 88% (258 tests)
**Target**: 100%

### Missing Coverage Areas

1. **CLI (`src/haproxy_translator/cli/main.py`)**: 69% → 100% (3 hrs)
   - Add CLI integration tests
   - Test error handling
   - Test all flags and options

2. **IR Nodes (`src/haproxy_translator/ir/nodes.py`)**: 91% → 100% (2 hrs)
   - Add tests for `Listen` section (currently disabled)
   - Test all IR node edge cases

3. **DSL Transformer (`src/haproxy_translator/transformers/dsl_transformer.py`)**: 84% → 100% (8 hrs)
   - Most complex file, many untested branches
   - Add tests for all transformer methods
   - Test error paths

4. **Code Generator (`src/haproxy_translator/codegen/haproxy.py`)**: 96% → 100% (2 hrs)
   - Test Listen section generation
   - Test edge cases in server formatting

### Test Organization

Create new test files for missing coverage:

- `tests/test_cli/test_integration.py` - CLI integration tests
- `tests/test_parser/test_listen_section.py` - Listen section tests
- `tests/test_transformer/test_edge_cases.py` - Transformer edge cases
- `tests/test_codegen/test_listen_generation.py` - Listen code generation

---

## Implementation Phases

### Phase 1: Critical Foundation (20-30 hours) → v0.5.0

**Goal**: Production-ready for basic use cases

**Features**:

1. ✅ `option forwardfor` (VERIFIED - add tests only)
2. ✅ `option http-keep-alive` (VERIFIED - add tests only)
3. ⭐ `default-server` directive (4-6 hrs)
4. ✅ Extended timeout support (2-3 hrs)
5. ✅ Common options tests (DONE)
6. Global: `nbthread`, `maxsslconn`, `ulimit-n` (3 hrs)
7. Server: `slowstart`, `send-proxy-v2` (3 hrs)
8. Bind: `accept-proxy` (1 hr)
9. Test coverage: 88% → 92% (5 hrs)

**Deliverables**:

- All critical features implemented
- Common production patterns tested
- 268+ tests passing
- 92%+ coverage

### Phase 2: Advanced Production (25-35 hours) → v0.6.0

**Goal**: Production-ready for advanced use cases

**Features**:

1. `log-format` custom logging (4 hrs)
2. `http-check expect` enhancements (3 hrs)
3. `capture request/response header` (5-6 hrs)
4. Protocol-specific health checks (4 hrs)
5. Advanced server options (8 hrs remaining)
6. Test coverage: 92% → 96% (6 hrs)

**Deliverables**:

- Advanced logging and debugging
- Comprehensive health checks
- 290+ tests passing
- 96%+ coverage

### Phase 3: Enterprise Features (30-40 hours) → v0.7.0

**Goal**: Enterprise-ready with advanced features

**Features**:

1. Additional load balancing algorithms (6 hrs)
2. Full TCP processing support (8 hrs)
3. HTTP advanced processing (8 hrs)
4. Advanced bind options (6 hrs)
5. Enhanced monitoring (4 hrs)
6. Test coverage: 96% → 99% (8 hrs)

**Deliverables**:

- Enterprise-grade features
- Comprehensive test suite
- 320+ tests passing
- 99%+ coverage

### Phase 4: Specialized Features (40+ hours) → v1.0.0

**Goal**: Specialized use cases and modern protocols

**Features**:

1. HTTP/2 configuration (8 hrs)
2. Caching support (10 hrs)
3. SPOE integration (12 hrs)
4. Variables and maps (10 hrs)
5. Test coverage: 99% → 100% (5 hrs)

**Deliverables**:

- Modern protocol support
- Full feature parity
- 350+ tests passing
- 100% coverage

---

## Quick Wins (1-2 hours each)

These can be implemented quickly for immediate value:

1. ✅ **Common options** (DONE - tests added)
2. **`nbthread`** - Threading support
3. **`maxsslconn`** - SSL limits
4. **`ulimit-n`** - FD limits
5. **`slowstart`** - Server warmup
6. **`send-proxy-v2`** - PROXY protocol v2
7. **`accept-proxy`** - Accept PROXY protocol
8. **`hash-type`** - Consistent hashing
9. **Backend timeouts** - http-request, tunnel, etc.
10. **`monitor fail`** - Force monitor failure

---

## Current Sprint (Next 10-15 hours)

### Immediate Tasks

1. ✅ **Run common options tests** (5 min)
   - Verify option forwardfor works
   - Verify option http-keep-alive works
   - Ensure all 11 option tests pass

2. ⭐ **Implement `default-server`** (4-6 hrs)
   - Critical for config maintainability
   - Highest priority missing feature

3. **Implement global tuning** (3 hrs)
   - `nbthread`
   - `maxsslconn`
   - `ulimit-n`

4. **Implement server options** (3 hrs)
   - `slowstart`
   - `send-proxy-v2`

5. **Add CLI tests** (3 hrs)
   - Get CLI coverage to 100%

**Sprint Goal**: 270+ tests, 92%+ coverage, critical features done

---

## Long-Term Vision

### v1.0 Goals (100% Feature Parity)

- **350+ tests** with 100% passing
- **100% code coverage**
- **75%+ HAProxy directive coverage** (300+ of 411 directives)
- **All common use cases** supported
- **Production-ready** for any deployment size
- **Enterprise-ready** with advanced features
- **Modern protocols** (HTTP/2, HTTP/3)

### Beyond v1.0

- **HAProxy 3.1+ tracking** - Stay current with HAProxy releases
- **DSL enhancements** - More powerful templating
- **Migration tools** - Convert existing HAProxy configs to DSL
- **Validation improvements** - Catch more errors at parse time
- **Performance** - Optimize for large configs (1000s of servers)
- **Documentation** - Comprehensive user guide
- **Examples** - Production-ready templates

---

## Metrics & Success Criteria

### Code Quality

- ✅ **Test Coverage**: 88% → **Target: 100%**
- ✅ **Test Pass Rate**: 100% (258/258) → **Maintain 100%**
- ✅ **Type Safety**: Full type hints → **Maintain**
- ✅ **Code Style**: Black, isort, pylint → **Maintain**

### Feature Completeness

- **Current**: ~22% of HAProxy directives
- **Phase 1**: ~25% (basic production)
- **Phase 2**: ~40% (advanced production)
- **Phase 3**: ~50% (enterprise)
- **Phase 4**: ~75%+ (specialized)

### Performance

- **Parse Speed**: <100ms for typical configs
- **Generate Speed**: <50ms for typical configs
- **Memory**: <50MB for large configs
- **Lua Generation**: <10ms per script

### User Experience

- **Error Messages**: Clear, actionable
- **Documentation**: Comprehensive examples
- **Migration Path**: Easy from native HAProxy
- **Learning Curve**: Gentle for HAProxy users

---

## Risk Assessment

### Technical Risks

1. **Grammar Complexity** (LOW)
   - Lark parser handles complex grammars well
   - Earley algorithm prevents ambiguity
   - Mitigation: Thorough testing

2. **HAProxy Compatibility** (MEDIUM)
   - HAProxy changes between versions
   - Some directives deprecated/added
   - Mitigation: Version-specific validators

3. **Performance** (LOW)
   - Large configs (1000s of servers) may be slow
   - Mitigation: Optimize hot paths, add caching

### Project Risks

1. **Scope Creep** (MEDIUM)
   - HAProxy has 411+ directives
   - Can't implement everything
   - Mitigation: Focus on common use cases (80/20 rule)

2. **Maintenance** (MEDIUM)
   - Keep up with HAProxy releases
   - Maintain backward compatibility
   - Mitigation: Automated testing, version tracking

---

## Resources & References

### HAProxy Documentation

- **Main Config**: `/home/user/haproxy/doc/configuration.txt` (1.5MB)
- **Management**: `/home/user/haproxy/doc/management.txt`
- **Intro**: `/home/user/haproxy/doc/intro.txt`
- **SPOE**: `/home/user/haproxy/doc/SPOE.txt`

### Project Files

- **Grammar**: `src/haproxy_translator/grammars/haproxy_dsl.lark`
- **IR Nodes**: `src/haproxy_translator/ir/nodes.py`
- **Transformer**: `src/haproxy_translator/transformers/dsl_transformer.py`
- **Code Generator**: `src/haproxy_translator/codegen/haproxy.py`
- **Tests**: `tests/`

### External Resources

- HAProxy Official Docs: https://docs.haproxy.org
- HAProxy GitHub: https://github.com/haproxy/haproxy
- Mozilla SSL Config: https://ssl-config.mozilla.org/

---

## Conclusion

The HAProxy Configuration Translator has a **solid foundation** and is ready for the next phase of development. With focused effort on critical features (especially `default-server`), we can achieve production-readiness for most use cases within 20-30 hours.

The phased approach ensures we:

1. **Deliver value quickly** (Phase 1 critical features)
2. **Build systematically** (Phases 2-3 advanced features)
3. **Achieve excellence** (Phase 4 specialized features)
4. **Maintain quality** (100% test coverage throughout)

**Next Actions**:

1. ✅ Run common options tests
2. ⭐ Implement `default-server` (highest priority)
3. Add global tuning directives
4. Increase test coverage to 92%+
5. Release v0.5.0 with critical features

This roadmap will be updated as features are implemented and priorities shift.
