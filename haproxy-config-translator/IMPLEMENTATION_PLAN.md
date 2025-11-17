# HAProxy Config Translator - Feature Implementation Plan

## Current Status
- **Test Coverage**: 87% (215/215 tests passing)
- **Version**: v0.4.0
- **Last Feature**: Lua script extraction with inline keyword support

## Feature Parity Analysis Results

Based on comprehensive investigation of HAProxy 2.0 documentation in `/home/user/haproxy/doc/configuration.txt`:

| Component | Current Coverage | Critical Gaps |
|-----------|------------------|---------------|
| Global    | 15% (12/80)     | SSL server defaults, threading, tune.ssl.* |
| Defaults  | 23% (16/70)     | balance, cookie, stick-table, log-format |
| Frontend  | 40% (14/35)     | tcp-request, stick-table, log, capture |
| Backend   | 65% (13/20)     | stick-table, acl, hash-type, tcp-check |
| Server    | 45% (17/38)     | agent-check, slowstart, minconn, ca-file |
| Bind      | 9% (5/56)       | ciphers, ssl-min-ver, verify, maxconn |

##PHASE 1: CRITICAL PRODUCTION FEATURES (v0.5.0)

### 1.1 Stick Tables & Session Persistence
**Priority**: CRITICAL
**Usage**: ~60% of production configs
**Complexity**: HIGH

**Implementation**:
- [ ] Add `StickTable` IR node class
- [ ] Add `stick_table` field to Frontend, Backend, Listen
- [ ] Add `stick on`, `stick match`, `stick store-request/response` directives
- [ ] Grammar rules for stick-table syntax
- [ ] Transformer methods for parsing
- [ ] Code generation for stick-table directives
- [ ] Tests: basic stick-table, stick on, stick match

**Files to Modify**:
- `src/haproxy_translator/ir/nodes.py` - Add StickTable class
- `src/haproxy_translator/grammars/haproxy_dsl.lark` - Add stick rules
- `src/haproxy_translator/transformers/dsl_transformer.py` - Parse stick directives
- `src/haproxy_translator/codegen/haproxy.py` - Generate stick config
- `tests/test_parser/test_stick_tables.py` - NEW TEST FILE

### 1.2 SSL/TLS Hardening Parameters
**Priority**: CRITICAL
**Usage**: Security compliance (PCI-DSS, FIPS, etc.)
**Complexity**: MEDIUM

**Implementation**:
- [ ] Extend `Bind` class with SSL params:
  - `ciphers: str | None`
  - `ciphersuites: str | None`
  - `ssl_min_ver: str | None`
  - `ssl_max_ver: str | None`
  - `verify: str | None` (none/optional/required)
  - `ca_file: str | None`
  - `crl_file: str | None`
- [ ] Extend `GlobalConfig` with server-side SSL:
  - `ssl_default_server_ciphers: str | None`
  - `ssl_default_server_ciphersuites: str | None`
  - `ssl_default_server_options: list[str]`
  - `ssl_dh_param_file: str | None`
  - `ca_base: str | None`
  - `crt_base: str | None`
- [ ] Extend `Server` class:
  - `ca_file: str | None`
  - `crl_file: str | None`
  - `ciphers: str | None`
  - `ciphersuites: str | None`
- [ ] Grammar, transformer, codegen updates
- [ ] Tests for all SSL parameters

**Files to Modify**:
- `src/haproxy_translator/ir/nodes.py` - Extend Bind, GlobalConfig, Server
- `src/haproxy_translator/grammars/haproxy_dsl.lark` - SSL param rules
- `src/haproxy_translator/transformers/dsl_transformer.py` - Parse SSL params
- `src/haproxy_translator/codegen/haproxy.py` - Generate SSL config
- `tests/test_parser/test_ssl_hardening.py` - NEW TEST FILE

### 1.3 TCP Request/Response Processing
**Priority**: CRITICAL
**Usage**: DDoS protection, rate limiting, connection tracking
**Complexity**: HIGH

**Implementation**:
- [ ] Add `TcpRequestRule` IR node class (action, condition)
- [ ] Add `TcpResponseRule` IR node class
- [ ] Add `tcp_request_rules` to Frontend, Backend, Listen
- [ ] Add `tcp_response_rules` to Frontend, Backend, Listen
- [ ] Support actions: accept, reject, expect-proxy, set-var, track-sc*
- [ ] Support conditions: ACL-based conditions
- [ ] Grammar for tcp-request/tcp-response syntax
- [ ] Transformer methods
- [ ] Code generation
- [ ] Tests: connection rules, content rules, inspect-delay

**Files to Modify**:
- `src/haproxy_translator/ir/nodes.py` - Add TcpRequestRule, TcpResponseRule
- `src/haproxy_translator/grammars/haproxy_dsl.lark` - tcp-request rules
- `src/haproxy_translator/transformers/dsl_transformer.py` - Parse tcp rules
- `src/haproxy_translator/codegen/haproxy.py` - Generate tcp rules
- `tests/test_parser/test_tcp_rules.py` - NEW TEST FILE

## PHASE 2: HIGH PRIORITY FEATURES (v0.6.0)

### 2.1 Enhanced Logging
- [ ] Add `log` directive to Frontend, Backend (list[LogTarget])
- [ ] Add `log_format` to Defaults, Frontend, Backend
- [ ] Add `log_tag` support
- [ ] Tests for custom log formats

### 2.2 Cookie-Based Persistence
- [ ] Extend `cookie` field in Backend with structured params
- [ ] Add CookieConfig IR node (name, mode, options)
- [ ] Support: rewrite, insert, prefix, indirect, nocache, postonly, preserve, httponly, secure, domain, maxidle, maxlife, dynamic
- [ ] Tests for cookie persistence modes

### 2.3 Default Server Configuration
- [ ] Wire up `default_server` field in Backend (currently exists but not parsed)
- [ ] Support all server parameters as defaults
- [ ] Tests for default-server inheritance

### 2.4 Agent-Based Health Checks
- [ ] Add to Server class:
  - `agent_check: bool`
  - `agent_port: int | None`
  - `agent_inter: str | None`
  - `agent_send: str | None`
- [ ] Grammar, transformer, codegen
- [ ] Tests for agent-check

### 2.5 ACLs in Backend
- [ ] Add `acls` field to Backend class (already in Frontend)
- [ ] Support ACL-based routing in backends
- [ ] Tests for backend ACLs

## PHASE 3: MEDIUM PRIORITY FEATURES (v0.7.0)

### 3.1 Connection Management
- [ ] Add `maxconn` to Bind, Frontend, Backend
- [ ] Add `fullconn` to Defaults, Backend
- [ ] Add `minconn` to Server
- [ ] Add `slowstart` to Server
- [ ] Add `backlog` to Bind
- [ ] Tests for connection limits

### 3.2 Advanced Health Checks
- [ ] Add `tcp-check` alternative to http-check
- [ ] Add `external-check` support
- [ ] Add `check-ssl`, `check-send-proxy` to Server
- [ ] Tests for tcp-check, external-check

### 3.3 Hash Type & Balance Algorithm Enhancements
- [ ] Add `hash_type` to Backend (consistent, map-based)
- [ ] Add balance algorithm parameters (url_param, hdr with args)
- [ ] Tests for advanced balancing

### 3.4 Error Handling Extensions
- [ ] Add errorfile/errorloc to Frontend, Backend
- [ ] Support http-after-response in Frontend
- [ ] Tests for error page handling

### 3.5 Advanced Server Options
- [ ] Add `send-proxy-v2` to Server
- [ ] Add `observe` to Server (layer4, layer7, error)
- [ ] Add `track` to Server
- [ ] Add `on-marked-down`, `on-marked-up` to Server
- [ ] Add `fastinter`, `downinter` to Server
- [ ] Tests for advanced server features

### 3.6 Bind Enhancements
- [ ] Add `accept-proxy` to Bind
- [ ] Add `maxconn` to Bind
- [ ] Add `transparent` to Bind
- [ ] Add `defer-accept`, `tfo` to Bind
- [ ] Tests for advanced bind options

### 3.7 Global Enhancements
- [ ] Add `nbthread`, `nbproc` to GlobalConfig
- [ ] Add `hard-stop-after` to GlobalConfig
- [ ] Add tune.ssl.* parameters to GlobalConfig.tuning
- [ ] Add `maxconnrate`, `maxsessrate` to GlobalConfig
- [ ] Tests for threading and tuning

## PHASE 4: COMPLETENESS (v1.0.0)

### 4.1 Capture Directives
- [ ] Add capture request/response header support
- [ ] Add capture cookie support
- [ ] Add declare capture
- [ ] Tests for capture

### 4.2 Monitoring Enhancements
- [ ] Add `monitor fail` to Frontend
- [ ] Add `monitor-net` to Defaults, Frontend
- [ ] Tests for monitoring

### 4.3 Filters
- [ ] Add compression filter configuration
- [ ] Add trace filter support
- [ ] Tests for filters

### 4.4 Advanced Persistence
- [ ] Add `persist` directive
- [ ] Add `dynamic-cookie-key`
- [ ] Tests for persistence modes

### 4.5 Process & Socket Management
- [ ] Add `bind-process` to Bind
- [ ] Add socket ownership fields (user, group, uid, gid, mode)
- [ ] Add `interface` to Bind
- [ ] Tests for process binding

## Testing Strategy

### Test Coverage Goals
- **Current**: 87% overall
- **Target Phase 1**: 90% overall
- **Target Phase 2**: 92% overall
- **Target Phase 3-4**: 95% overall

### Test Categories
1. **Unit Tests**: Individual directive parsing and IR node creation
2. **Integration Tests**: End-to-end DSL → IR → HAProxy config
3. **Validation Tests**: Semantic validation of configurations
4. **Regression Tests**: Ensure existing features don't break

### New Test Files Needed
- `tests/test_parser/test_stick_tables.py`
- `tests/test_parser/test_ssl_hardening.py`
- `tests/test_parser/test_tcp_rules.py`
- `tests/test_parser/test_logging.py`
- `tests/test_parser/test_cookie_persistence.py`
- `tests/test_parser/test_agent_check.py`
- `tests/test_parser/test_connection_limits.py`
- `tests/test_parser/test_hash_types.py`
- `tests/test_parser/test_capture.py`
- `tests/test_parser/test_monitoring.py`

## Success Criteria

### Phase 1 Success (v0.5.0)
- ✅ Stick tables fully functional
- ✅ SSL/TLS hardening params supported
- ✅ tcp-request/tcp-response working
- ✅ All tests passing (220+ tests)
- ✅ 90%+ test coverage
- ✅ No regressions

### Phase 2 Success (v0.6.0)
- ✅ Enhanced logging functional
- ✅ Cookie persistence working
- ✅ default-server implemented
- ✅ agent-check supported
- ✅ Backend ACLs working
- ✅ All tests passing (240+ tests)
- ✅ 92%+ test coverage

### Phase 3-4 Success (v1.0.0)
- ✅ ALL documented HAProxy 2.0 directives supported
- ✅ 100% feature parity
- ✅ All tests passing (300+ tests)
- ✅ 95%+ test coverage
- ✅ Production-ready documentation

## Implementation Timeline

- **Phase 1**: IMMEDIATE (current session)
- **Phase 2**: Follow-up session
- **Phase 3-4**: Subsequent sessions

## Notes

- Each feature must include grammar, transformer, IR nodes, codegen, and tests
- No feature is "done" until tests pass
- Maintain backward compatibility throughout
- Document breaking changes (if any)
- Update CHANGELOG.md for each phase
