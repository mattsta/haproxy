# Global Directives - Quick Reference Summary

**Investigation Date**: 2025-11-18  
**Current Implementation**: 15/100+ directives (15%)  
**Missing**: 85+ directives (85%)  
**Target**: 100% parity

---

## CURRENTLY IMPLEMENTED (15 Directives) ✅

| Directive | Category | Status |
|-----------|----------|--------|
| `daemon` | Process Management | ✅ |
| `user` | Process Management | ✅ |
| `group` | Process Management | ✅ |
| `chroot` | Process Management | ✅ |
| `pidfile` | Process Management | ✅ |
| `maxconn` | Performance Limits | ✅ |
| `nbthread` | Process/Threading | ✅ |
| `log` | Logging | ✅ |
| `lua-load` | Lua Configuration | ✅ |
| `ssl-default-bind-ciphers` | SSL/TLS | ✅ |
| `ssl-default-bind-options` | SSL/TLS | ✅ |
| `maxsslconn` | Performance Tuning (via tuning dict) | ✅ |
| `ulimit-n` | Performance Tuning (via tuning dict) | ✅ |
| `stats socket` | Stats/Monitoring | ⚠️ (hardcoded) |

---

## CRITICAL MISSING (PHASE 1 - 15-20 directives) 🔴

**These are most commonly used and should be prioritized:**

### Environment Variables (4)
- `setenv` - Set environment variable
- `presetenv` - Set if not exists
- `resetenv` - Clear all except specified
- `unsetenv` - Remove variable

### Rate Limiting (3)
- `maxconnrate` - Connection rate limit
- `maxsslrate` - SSL connection rate
- `maxsessrate` - Session rate limit

### Buffer & Tuning (3)
- `tune.bufsize` - Buffer size
- `tune.maxrewrite` - Max rewrite space
- `maxpipes` - Pipe buffer count

### SSL/TLS (5)
- `ssl-dh-param-file` - DH parameters
- `ssl-default-server-ciphers` - Server ciphers
- `ssl-server-verify` - Server verification
- `ca-base` - CA certificate directory
- `crt-base` - Certificate directory

### Logging (2)
- `log-tag` - Syslog tag/prefix
- `log-send-hostname` - Include hostname

### Process Control (1)
- `nbproc` - Number of processes (for 2.0-2.4)

---

## HIGH PRIORITY MISSING (PHASE 2 - 25-30 directives) 🟠

### SSL Tuning (10+)
- `tune.ssl.bufsize` - SSL buffer size
- `tune.ssl.cachesize` - Session cache size
- `tune.ssl.lifetime` - Session lifetime
- `tune.ssl.maxrecord` - Max record size
- `tune.ssl.keylog` - SSLKEYLOGFILE
- `tune.ssl.capture-cipherlist` - Capture ciphers
- `tune.ssl.capture-buffer-size` - Cipher buffer
- `tune.ssl.default-dh-param` - Default DH size
- `tune.ssl.ocsp-update.minthour` - OCSP update
- `tune.ssl.ocsp-update.maxhour` - OCSP update

### HTTP/2 Tuning (10+)
- `tune.h2.be.glitches-threshold`
- `tune.h2.be.initial-window-size`
- `tune.h2.be.max-concurrent-streams`
- `tune.h2.fe.glitches-threshold`
- `tune.h2.fe.initial-window-size`
- `tune.h2.fe.max-concurrent-streams`
- `tune.h2.fe.max-total-streams`
- `tune.h2.header-table-size`
- `tune.h2.initial-window-size`
- `tune.h2.max-concurrent-streams`
- `tune.h2.max-frame-size`

### TLS 1.3 & SSL (5)
- `ssl-default-bind-ciphersuites` - TLS 1.3 binding ciphers
- `ssl-default-server-ciphersuites` - TLS 1.3 server ciphers
- `ssl-default-server-options` - Default server SSL options
- `ssl-engine` - OpenSSL engine selection
- `key-base` - Key file directory

### Master-Worker (2)
- `master-worker` - Enable master-worker mode
- `mworker-max-reloads` - Max reload count

---

## MEDIUM PRIORITY MISSING (PHASE 3 - 20+ directives) 🟡

### HTTP Tuning (5)
- `tune.http.maxhdr` - Max header count
- `tune.http.cookielen` - Max cookie length
- `tune.http.logurilen` - Max URI in logs

### Memory Tuning (3)
- `tune.memory.pool-allocator` - Allocator type
- `tune.memory.fail-alloc` - Failure behavior
- `tune.buffers.limit` - Memory limit
- `tune.buffers.reserve` - Reserved memory

### System Integration (5)
- `uid` - Numeric user ID
- `gid` - Numeric group ID
- `setcap` - Linux capabilities
- `set-dumpable` - Core dumps
- `unix-bind` - Unix socket permissions

### CPU & Performance (3)
- `cpu-map` - CPU affinity
- `tune.fd.edge-triggered` - FD polling mode
- `tune.comp.maxlevel` - Compression level

### Advanced Options (4)
- `hard-stop-after` - Shutdown timeout
- `node` - Node identifier
- `description` - Process description
- `external-check` - External health checks

---

## LOW PRIORITY MISSING (PHASE 4 - 20+ directives) 🔵

### QUIC/HTTP3 (10+)
- `tune.quic.*` - All QUIC-specific tuning directives

### Device Detection (10+)
- DeviceAtlas directives (4)
- 51Degrees directives (4)
- WURFL directives (4)

### HTTP Client (8)
- `httpclient.timeout.connect`
- `httpclient.timeout.server-response`
- `httpclient.ssl.*` - SSL options
- `httpclient.resolvers` - Resolver config
- `httpclient.default-ssl-*` - Default modes

### Debugging (4)
- `debug` - Debug mode
- `quiet` - Suppress messages
- `expose-fd` - FD exposure
- `expose-experimental-directives` - Experimental features

### Advanced Enterprise (8+)
- `userlist` - Authentication
- `peers` - Peer sync
- `mailers` - Email config
- `programs` - Program hooks
- `http-errors` - Error pages
- `rings` - Log buffers
- `h1-case-adjust` - Header case
- `email-alert` directives

---

## SUMMARY BY IMPLEMENTATION DIFFICULTY

### EASY (Simple key-value directives - 25+)
```
- setenv, presetenv, resetenv, unsetenv
- maxconnrate, maxsslrate, maxsessrate, maxpipes
- log-tag, log-send-hostname
- ca-base, crt-base, key-base
- All tune.* directives
- uid, gid, description, node, hard-stop-after
- nbproc, cpu-map
```

### MEDIUM (Complex directives with options - 30+)
```
- ssl-dh-param-file, ssl-engine
- ssl-default-*-ciphersuites
- ssl-default-server-ciphers
- master-worker, mworker-max-reloads
- unix-bind, setcap, set-dumpable
- Device detection directives
```

### HARD (Require major IR/grammar changes - 35+)
```
- userlist (authentication section)
- peers (peer sync section)
- mailers (email section)
- programs (program section)
- http-errors (error pages section)
- rings (log buffer section)
- stats section (full config)
- email-alert (complex options)
- h1-case-adjust (header list)
```

---

## QUICK STATS TABLE

| Metric | Count |
|--------|-------|
| **Total Global Directives** | 100+ |
| **Currently Implemented** | 15 |
| **Implementation Rate** | 15% |
| **Missing Directives** | 85+ |
| **Categories Covered** | 2/17 |
| **Categories Partially Covered** | 5/17 |
| **Categories Not Covered** | 10/17 |
| **Phase 1 Directives** | 15-20 |
| **Phase 2 Directives** | 25-30 |
| **Phase 3 Directives** | 20+ |
| **Phase 4 Directives** | 20+ |
| **Total Tests Needed** | 150-200 |
| **Estimated Effort** | 14-18 days |

---

## RECOMMENDED IMPLEMENTATION ORDER

```
WEEK 1 (Phase 1 - Critical Foundation)
├── Day 1-2: Environment variables (setenv, presetenv, resetenv, unsetenv)
├── Day 2: Rate limiting (maxconnrate, maxsslrate, maxsessrate)
├── Day 3: Buffer tuning (tune.bufsize, tune.maxrewrite, maxpipes)
└── Day 3-4: SSL defaults (ca-base, crt-base, ssl-dh-param-file, ssl-default-server-ciphers, ssl-server-verify, log-tag, nbproc)

WEEK 2 (Phase 2 - SSL/HTTP/2 Enhancement)
├── Day 1-2: All tune.ssl.* directives (10+)
├── Day 2-3: All tune.h2.* directives (10+)
├── Day 3: TLS 1.3 ciphersuites + other SSL (ssl-default-*-ciphersuites, ssl-engine, key-base)
├── Day 4: HTTP header tuning (tune.http.maxhdr, cookielen, logurilen)
└── Day 4: Master-worker (master-worker, mworker-max-reloads)

WEEK 2-3 (Phase 3 - Advanced Tuning)
├── Day 1: Memory tuning (tune.memory.*)
├── Day 2: CPU affinity (cpu-map) + system integration (uid, gid, setcap)
├── Day 3: QUIC/HTTP3 (tune.quic.*)
└── Day 4: HTTP client tuning (httpclient.*)

WEEK 3-4 (Phase 4 - Enterprise Features)
├── Day 1-2: Device detection (DeviceAtlas, 51Degrees, WURFL)
├── Day 2: Stats/monitoring full config + email alerts
├── Day 3: Advanced (userlist, peers, mailers, programs)
└── Day 4: Final directives (http-errors, rings, debugging, h1-case-adjust)
```

---

## REFERENCES

**Full Investigation Report**: `GLOBAL_DIRECTIVES_INVESTIGATION.md`

**HAProxy Documentation**:
- HAProxy 2.0.28: http://cbonte.github.io/haproxy-dconv/2.0/configuration.html
- HAProxy 2.8.16: https://docs.haproxy.org/2.8/configuration.html
- HAProxy 3.3-dev: https://docs.haproxy.org/dev/configuration.html

**Current Codebase**:
- Grammar: `src/haproxy_translator/grammars/haproxy_dsl.lark` (lines 23-40)
- IR Nodes: `src/haproxy_translator/ir/nodes.py` (lines 144-159)
- Transformer: `src/haproxy_translator/transformers/dsl_transformer.py` (lines 102-200)
- Code Generator: `src/haproxy_translator/codegen/haproxy.py` (lines 99-160)

---

**Last Updated**: 2025-11-18  
**Prepared By**: Comprehensive investigation of HAProxy documentation and codebase analysis
