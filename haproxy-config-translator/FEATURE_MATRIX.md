# HAProxy Feature Matrix - Complete Feature Comparison

**Last Updated**: 2025-11-18
**HAProxy Version**: 3.0+
**Translator Version**: 0.4.0

This document provides a comprehensive comparison between HAProxy native configuration directives and our DSL implementation.

## Legend

- ✅ **Fully Implemented** - Feature works exactly as in HAProxy
- ⚠️ **Partially Implemented** - Core functionality works, some options missing
- ❌ **Not Implemented** - Feature not yet supported
- 🔄 **In Progress** - Currently being implemented
- 💡 **DSL Extension** - Feature unique to our DSL (not in native HAProxy)

---

## 1. Global Section

| Directive                   | Status | Notes                              |
| --------------------------- | ------ | ---------------------------------- |
| `daemon`                    | ✅     | Boolean flag                       |
| `user`                      | ✅     | Process user                       |
| `group`                     | ✅     | Process group                      |
| `chroot`                    | ✅     | Filesystem restriction             |
| `pidfile`                   | ✅     | PID file path                      |
| `maxconn`                   | ✅     | Maximum connections                |
| `nbthread`                  | ✅     | Worker thread count                |
| `maxsslconn`                | ✅     | SSL connection limit               |
| `ulimit-n`                  | ✅     | File descriptor limit              |
| `log`                       | ✅     | Syslog targets with facility/level |
| `lua-load`                  | ✅     | Load Lua scripts                   |
| `stats socket`              | ⚠️     | Basic stats support                |
| `stats timeout`             | ⚠️     | Stats timeout                      |
| `ssl-default-bind-ciphers`  | ✅     | Default cipher suites              |
| `ssl-default-bind-options`  | ✅     | SSL/TLS options array              |
| `ssl-dh-param-file`         | ❌     | DH parameters file                 |
| `ca-base`                   | ❌     | Certificate base path              |
| `crt-base`                  | ❌     | Certificate base path              |
| `ssl-server-verify`         | ❌     | Server SSL verify default          |
| `tune.bufsize`              | ❌     | Buffer size tuning                 |
| `tune.maxrewrite`           | ❌     | Max rewrite buffer                 |
| `tune.ssl.default-dh-param` | ❌     | DH parameter size                  |
| `setenv`                    | ❌     | Set environment variables          |
| `presetenv`                 | ❌     | Preset environment variables       |
| `resetenv`                  | ❌     | Reset environment variables        |

**Coverage**: 15/25 (60%)

---

## 2. Defaults Section

| Directive                  | Status | Notes                         |
| -------------------------- | ------ | ----------------------------- |
| `mode`                     | ✅     | http/tcp mode                 |
| `log`                      | ✅     | Logging configuration         |
| `option`                   | ✅     | Generic option array          |
| `retries`                  | ✅     | Connection retry count        |
| `timeout connect`          | ✅     | Server connection timeout     |
| `timeout client`           | ✅     | Client idle timeout           |
| `timeout server`           | ✅     | Server idle timeout           |
| `timeout check`            | ✅     | Health check timeout          |
| `timeout queue`            | ✅     | Queue wait timeout            |
| `timeout http-request`     | ✅     | HTTP request timeout          |
| `timeout http-keep-alive`  | ✅     | Keep-alive timeout            |
| `timeout client-fin`       | ✅     | Client FIN timeout            |
| `timeout server-fin`       | ✅     | Server FIN timeout            |
| `timeout tunnel`           | ✅     | Tunnel timeout                |
| `errorloc`                 | ✅     | Error redirect (302)          |
| `errorloc302`              | ✅     | Error redirect (302 explicit) |
| `errorloc303`              | ✅     | Error redirect (303)          |
| `errorfile`                | ✅     | Custom error pages            |
| `balance`                  | ❌     | Default balance algorithm     |
| `option httplog`           | ✅     | Via generic option            |
| `option tcplog`            | ✅     | Via generic option            |
| `option forwardfor`        | ✅     | Via generic option            |
| `option http-server-close` | ✅     | Via generic option            |

**Coverage**: 21/23 (91%)

---

## 3. Frontend Section

| Directive                   | Status | Notes                      |
| --------------------------- | ------ | -------------------------- |
| `bind`                      | ✅     | Address and port binding   |
| `mode`                      | ✅     | http/tcp mode              |
| `maxconn`                   | ✅     | Maximum connections        |
| `acl`                       | ✅     | Full ACL support           |
| `use_backend`               | ✅     | Conditional routing        |
| `default_backend`           | ✅     | Default backend            |
| `http-request`              | ✅     | Request manipulation       |
| `http-response`             | ✅     | Response manipulation      |
| `tcp-request connection`    | ✅     | Connection-level TCP rules |
| `tcp-request content`       | ✅     | Content inspection         |
| `tcp-response content`      | ✅     | TCP response rules         |
| `stick-table`               | ✅     | Session persistence tables |
| `monitor-uri`               | ✅     | Health check endpoint      |
| `timeout client`            | ✅     | Client timeout override    |
| `timeout http-request`      | ✅     | HTTP request timeout       |
| `timeout http-keep-alive`   | ✅     | Keep-alive timeout         |
| `option`                    | ✅     | Generic options            |
| `log-format`                | ❌     | Custom log format          |
| `capture request header`    | ❌     | Header capture             |
| `capture response header`   | ❌     | Header capture             |
| `tcp-request inspect-delay` | ✅     | Buffer inspection delay    |
| `http-after-response`       | ❌     | Post-response processing   |

**Coverage**: 18/22 (82%)

---

## 4. Backend Section

| Directive                     | Status | Notes                                 |
| ----------------------------- | ------ | ------------------------------------- |
| `mode`                        | ✅     | http/tcp mode                         |
| `balance`                     | ✅     | All 10 algorithms                     |
| `server`                      | ✅     | Full server definition                |
| `default-server`              | ✅     | Server defaults                       |
| `server-template`             | ✅     | Dynamic server generation             |
| `option`                      | ✅     | Generic options                       |
| `cookie`                      | ✅     | Cookie persistence                    |
| `acl`                         | ✅     | Backend ACLs                          |
| `http-request`                | ✅     | Request manipulation                  |
| `http-response`               | ✅     | Response manipulation                 |
| `tcp-request content`         | ✅     | TCP request rules                     |
| `tcp-response content`        | ✅     | TCP response rules                    |
| `stick-table`                 | ✅     | Stick tables                          |
| `stick on`                    | ✅     | Stick rules                           |
| `stick match`                 | ✅     | Stick matching                        |
| `health-check`                | ✅     | Health check config                   |
| `http-check`                  | ✅     | HTTP health checks                    |
| `http-check expect`           | ✅     | Advanced expect (status/string/regex) |
| `timeout connect`             | ✅     | Connection timeout                    |
| `timeout server`              | ✅     | Server timeout                        |
| `timeout check`               | ✅     | Check timeout                         |
| `timeout tunnel`              | ✅     | Tunnel timeout                        |
| `timeout server-fin`          | ✅     | Server FIN timeout                    |
| `retries`                     | ✅     | Retry count                           |
| `compression`                 | ✅     | Response compression                  |
| `http-reuse`                  | ❌     | Connection reuse                      |
| `load-server-state-from-file` | ❌     | Server state persistence              |

**Coverage**: 25/27 (93%)

---

## 5. Server Options

| Option          | Status | Notes                 |
| --------------- | ------ | --------------------- |
| `address`       | ✅     | Server address        |
| `port`          | ✅     | Server port           |
| `check`         | ✅     | Health checking       |
| `inter`         | ✅     | Check interval        |
| `rise`          | ✅     | Rise threshold        |
| `fall`          | ✅     | Fall threshold        |
| `weight`        | ✅     | Load balancing weight |
| `maxconn`       | ✅     | Max connections       |
| `ssl`           | ✅     | SSL/TLS               |
| `verify`        | ✅     | SSL verification      |
| `sni`           | ✅     | SNI support           |
| `alpn`          | ✅     | ALPN protocols        |
| `backup`        | ✅     | Backup server         |
| `send-proxy`    | ✅     | PROXY protocol v1     |
| `send-proxy-v2` | ✅     | PROXY protocol v2     |
| `slowstart`     | ✅     | Gradual weight ramp   |
| `check-ssl`     | ❌     | SSL for health checks |
| `check-sni`     | ❌     | SNI for health checks |
| `ca-file`       | ❌     | CA certificate file   |
| `crt`           | ❌     | Client certificate    |
| `ssl-min-ver`   | ❌     | Minimum TLS version   |
| `ssl-max-ver`   | ❌     | Maximum TLS version   |
| `source`        | ❌     | Source IP binding     |
| `init-addr`     | ❌     | DNS resolution method |
| `track`         | ❌     | Track another server  |

**Coverage**: 16/25 (64%)

---

## 6. Bind Options

| Option         | Status | Notes                       |
| -------------- | ------ | --------------------------- |
| `ssl`          | ✅     | SSL/TLS termination         |
| `crt`          | ✅     | Certificate file            |
| `alpn`         | ✅     | ALPN protocols              |
| `accept-proxy` | ❌     | Accept PROXY protocol       |
| `defer-accept` | ❌     | Defer connection acceptance |
| `transparent`  | ❌     | Transparent proxy           |
| `interface`    | ❌     | Network interface           |
| `tcp-ut`       | ❌     | TCP user timeout            |
| `namespace`    | ❌     | Network namespace           |
| `process`      | ❌     | Process affinity            |
| `thread`       | ❌     | Thread affinity             |

**Coverage**: 3/11 (27%)

---

## 7. Balance Algorithms

| Algorithm    | Status | Notes              |
| ------------ | ------ | ------------------ |
| `roundrobin` | ✅     | Round-robin        |
| `static-rr`  | ✅     | Static round-robin |
| `leastconn`  | ✅     | Least connections  |
| `first`      | ✅     | First available    |
| `source`     | ✅     | Source IP hash     |
| `uri`        | ✅     | URI hash           |
| `url_param`  | ✅     | URL parameter hash |
| `hdr`        | ✅     | Header hash        |
| `rdp-cookie` | ✅     | RDP cookie         |
| `random`     | ✅     | Random selection   |
| `hash`       | ❌     | Generic hash       |

**Coverage**: 10/11 (91%)

---

## 8. ACLs

| Feature              | Status | Notes           |
| -------------------- | ------ | --------------- |
| ACL definition       | ✅     | Full support    |
| ACL blocks           | ✅     | Multiple ACLs   |
| String matching      | ✅     | Exact/substring |
| Regex matching       | ✅     | Via criterion   |
| IP matching          | ✅     | CIDR/ranges     |
| Integer matching     | ✅     | Comparisons     |
| Boolean matching     | ✅     | true/false      |
| Flags (-i, -f, etc.) | ⚠️     | Partial support |
| OR conditions        | ✅     | Multiple ACLs   |
| AND conditions       | ✅     | if expressions  |
| NOT conditions       | ✅     | ! operator      |

**Coverage**: 10/11 (91%)

---

## 9. HTTP Actions

| Action           | Status | Notes                       |
| ---------------- | ------ | --------------------------- |
| `deny`           | ✅     | Deny request                |
| `allow`          | ✅     | Allow request               |
| `redirect`       | ✅     | HTTP redirect               |
| `set-header`     | ✅     | Set request/response header |
| `del-header`     | ✅     | Delete header               |
| `add-header`     | ✅     | Add header                  |
| `replace-header` | ✅     | Replace header value        |
| `replace-value`  | ✅     | Replace header value        |
| `set-var`        | ✅     | Set variable                |
| `lua.function`   | ✅     | Call Lua function           |
| `return`         | ❌     | Return custom response      |
| `set-status`     | ❌     | Change response status      |
| `normalize-uri`  | ❌     | URI normalization           |
| `strict-mode`    | ❌     | Strict protocol mode        |

**Coverage**: 10/14 (71%)

---

## 10. Lua Integration

| Feature                       | Status | Notes                   |
| ----------------------------- | ------ | ----------------------- |
| `lua-load`                    | ✅     | Load external Lua files |
| Inline Lua scripts            | ✅     | 💡 DSL extension        |
| Lua function calls            | ✅     | In HTTP rules           |
| Variable interpolation in Lua | ✅     | ${var} support          |
| Lua parameter passing         | ✅     | Function parameters     |
| Lua script extraction         | ✅     | To separate files       |

**Coverage**: 6/6 (100%)

---

## 11. DSL Unique Features 💡

| Feature                   | Status | Notes                     |
| ------------------------- | ------ | ------------------------- |
| Variables                 | ✅     | let statements            |
| Templates                 | ✅     | Reusable configs          |
| Template spreading        | ✅     | @template syntax          |
| For loops                 | ✅     | Dynamic server generation |
| If statements             | ✅     | Conditional config        |
| env() function            | ✅     | Environment variables     |
| String interpolation      | ✅     | ${var} in strings         |
| Nested objects            | ✅     | Clean syntax              |
| Comments (// and /\* \*/) | ✅     | C-style comments          |

**Coverage**: 9/9 (100%)

---

## Summary by Category

| Category           | Implemented | Total   | Coverage |
| ------------------ | ----------- | ------- | -------- |
| Global             | 15          | 25      | 60%      |
| Defaults           | 21          | 23      | 91%      |
| Frontend           | 18          | 22      | 82%      |
| Backend            | 25          | 27      | 93%      |
| Server Options     | 16          | 25      | 64%      |
| Bind Options       | 3           | 11      | 27%      |
| Balance Algorithms | 10          | 11      | 91%      |
| ACLs               | 10          | 11      | 91%      |
| HTTP Actions       | 10          | 14      | 71%      |
| Lua                | 6           | 6       | 100%     |
| **TOTAL**          | **134**     | **175** | **77%**  |

---

## Priority Implementation Queue

### Critical (Blocking Production Use)

1. ❌ `log-format` - Custom logging (Frontend/Backend)
2. ❌ `source` - Source IP binding (Server)
3. ❌ `ca-file`, `crt` - Server certificates (Server)

### High Priority (Common Use Cases)

4. ❌ `accept-proxy` - PROXY protocol acceptance (Bind)
5. ❌ `capture request/response header` - Header capture (Frontend)
6. ❌ `check-ssl`, `check-sni` - SSL health checks (Server)
7. ❌ `ssl-min-ver`, `ssl-max-ver` - TLS version constraints (Server/Bind)
8. ❌ `return` - Custom response action (HTTP)
9. ❌ `set-status` - Status modification (HTTP)

### Medium Priority (Advanced Features)

10. ❌ `http-reuse` - Connection reuse (Backend)
11. ❌ `http-after-response` - Post-response processing (Frontend)
12. ❌ `normalize-uri` - URI normalization (HTTP)
13. ❌ `transparent` - Transparent proxy (Bind)
14. ❌ `hash` - Generic hash balance (Backend)

### Low Priority (Specialized Features)

15. ❌ Global tuning parameters (tune.\*)
16. ❌ SSL advanced options (ca-base, crt-base, dh-params)
17. ❌ Server state persistence
18. ❌ Process/thread affinity
19. ❌ Network namespace support
