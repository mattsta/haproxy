# HAProxy Config Translator - Feature Parity Report

**Generated:** 2025-11-22 21:03:43
**HAProxy Version:** 3.3
**Documentation Source:** `/home/user/haproxy/doc/configuration.txt`

## Executive Summary

This report provides a comprehensive analysis of feature parity between the official HAProxy 3.3
configuration language and the haproxy-config-translator implementation.

## Coverage Statistics

### Global Directives

- **Total HAProxy Directives:** 172
- **Implemented:** 165
- **Coverage:** `95.9%`

```
[===============================================   ] 95.9%
```

### Proxy Keywords (Frontend/Backend/Listen/Defaults)

- **Total HAProxy Keywords:** 79
- **Implemented:** 78
- **Deprecated (handled):** 1
- **Coverage:** `100.0%`

### Test Coverage

- **Total Test Files:** 124
- **Global Directive Tests:** 10
- **Proxy Tests:** 0
- **Bind Option Tests:** 2
- **Server Option Tests:** 9
- **Action Tests:** 3
- **Parser Tests:** 1
- **Codegen Tests:** 1

## Missing Features by Category

### Global Directives

#### Performance Tuning

- **Total:** 77
- **Implemented:** 77
- **Missing:** 0

#### Debugging

- **Total:** 6
- **Implemented:** 6
- **Missing:** 0

#### Httpclient

- **Total:** 5
- **Implemented:** 5
- **Missing:** 0

#### Ssl Tls

- **Total:** 18
- **Implemented:** 18
- **Missing:** 0

#### Lua

- **Total:** 9
- **Implemented:** 9
- **Missing:** 0

#### Quic Http3

- **Total:** 57
- **Implemented:** 50
- **Missing:** 7

<details>
<summary>Missing Directives (7)</summary>

```
  - tune.quic.cc.cubic.min-losses
  - tune.quic.disable-tx-pacing
  - tune.quic.disable-udp-gso
  - tune.quic.frontend.default-max-window-size
  - tune.quic.frontend.max-data-size
  - tune.quic.frontend.max-tx-mem
  - tune.quic.frontend.stream-data-ratio
```

</details>

### Proxy Keywords

## Implementation Strengths

The haproxy-config-translator excels in several areas:

### ✅ Well-Implemented Features

1. **Core Global Directives** - Strong coverage of essential global configuration
   - Process management (daemon, user, group, chroot, pidfile)
   - Connection limits (maxconn, maxsslconn, maxconnrate, maxsessrate)
   - SSL/TLS configuration (ssl-default-bind-_, ssl-default-server-_)
   - Performance tuning (tune.\* directives)

2. **Proxy Configuration** - Comprehensive support for proxy sections
   - Frontend, backend, defaults, listen sections
   - Mode (http/tcp)
   - Balance algorithms (roundrobin, leastconn, source, uri, etc.)
   - Timeouts (connect, client, server, check, tunnel, etc.)

3. **Server Configuration** - Extensive server options
   - 55 server options implemented
   - SSL/TLS server options
   - Health checks
   - Connection pooling

4. **Advanced Features**
   - Stick tables and session persistence
   - ACLs (Access Control Lists)
   - HTTP request/response rules
   - TCP request/response rules
   - Compression
   - Lua integration

5. **Modern DSL Features**
   - Variables and templating
   - Loops and conditionals
   - Import statements
   - Environment variable interpolation

## Priority Recommendations

Based on the analysis, here are recommended priorities for achieving 100% parity:

### 🔴 High Priority (Critical for Production Use)

1. **Missing Core Global Directives**
   - `stats socket` - Runtime API
   - `peers` section - Stick table replication
   - `resolvers` section - DNS resolution
   - `mailers` section - Email alerts

2. **Missing Proxy Keywords**
   - `source` - Source IP for backend connections
   - `dispatch` - Simple load balancing
   - `http-reuse` - Connection pooling

3. **Missing Critical Actions**
   - Additional http-request actions
   - Additional http-response actions

### 🟡 Medium Priority (Important for Advanced Use Cases)

1. **Advanced Global Directives**
   - OCSP stapling configuration
   - QUIC/HTTP3 advanced tuning
   - Profiling options

2. **Additional Proxy Features**
   - `http-error` - Custom error responses
   - `cache` section - HTTP caching
   - `fcgi-app` - FastCGI applications

3. **Extended Bind Options**
   - Additional SSL/TLS bind options
   - QUIC-specific bind options

### 🟢 Low Priority (Nice to Have)

1. **Device Detection**
   - 51Degrees advanced options
   - DeviceAtlas options
   - WURFL options

2. **Deprecated Directives**
   - Legacy options marked as deprecated in docs

3. **Experimental Features**
   - Features requiring `expose-experimental-directives`

## Implementation Roadmap

### Phase 1: Core Completeness (Target: 70% Global Coverage)

- [ ] Add missing critical global directives
- [ ] Implement `stats socket` for runtime API
- [ ] Add `peers` section support
- [ ] Add `resolvers` section support
- [ ] Complete timeout directives

### Phase 2: Advanced Features (Target: 85% Global Coverage)

- [ ] OCSP stapling configuration
- [ ] HTTP caching (`cache` section)
- [ ] Email alerts (`mailers` section)
- [ ] Additional HTTP/TCP actions
- [ ] Extended bind options

### Phase 3: Completeness (Target: 95%+ Coverage)

- [ ] QUIC/HTTP3 advanced configuration
- [ ] FastCGI support
- [ ] Device detection libraries
- [ ] Profiling and debugging options
- [ ] Platform-specific optimizations

## Conclusion

The haproxy-config-translator currently implements **165** out of
**172** global directives (95.9% coverage),
demonstrating strong foundational support for HAProxy configuration.

**Strengths:**

- Excellent coverage of core configuration directives
- Modern DSL features (variables, templates, loops)
- Comprehensive server and proxy configuration
- Strong test coverage

**Areas for Improvement:**

- Runtime API (`stats socket`)
- Stick table replication (`peers`)
- DNS resolution (`resolvers`)
- HTTP caching
- QUIC/HTTP3 advanced features

With focused development following the recommended roadmap, achieving 95%+ feature parity
with HAProxy 3.3 is highly achievable.

## Appendices

### Appendix A: Implemented Global Directives

<details>
<summary>All Implemented Global Directives (243)</summary>

```
  ✓ 51degrees-cache-size
  ✓ 51degrees-data-file
  ✓ 51degrees-property-name-list
  ✓ 51degrees-property-separator
  ✓ anonkey
  ✓ busy-polling
  ✓ ca-base
  ✓ chroot
  ✓ crt-base
  ✓ daemon
  ✓ debug.counters
  ✓ default-path
  ✓ description
  ✓ deviceatlas-json-file
  ✓ deviceatlas-log-level
  ✓ deviceatlas-properties-cookie
  ✓ deviceatlas-separator
  ✓ external-check
  ✓ fd-hard-limit
  ✓ force-cfg-parser-pause
  ✓ gid
  ✓ group
  ✓ hard-stop-after
  ✓ httpclient.resolvers.disabled
  ✓ httpclient.resolvers.id
  ✓ httpclient.resolvers.prefer
  ✓ httpclient.retries
  ✓ httpclient.ssl.ca-file
  ✓ httpclient.ssl.verify
  ✓ httpclient.timeout.connect
  ✓ issuers-chain-path
  ✓ key-base
  ✓ limited-quic
  ✓ load-server-state-from-file
  ✓ localpeer
  ✓ log-send-hostname
  ✓ log-tag
  ✓ master-worker
  ✓ max-spread-checks
  ✓ maxcompcpuusage
  ✓ maxcomprate
  ✓ maxconn
  ✓ maxconnrate
  ✓ maxpipes
  ✓ maxsessrate
  ✓ maxsslconn
  ✓ maxsslrate
  ✓ maxzlibmem
  ✓ mworker-max-reloads
  ✓ nbproc
  ✓ nbthread
  ✓ no-memory-trimming
  ✓ node
  ✓ noepoll
  ✓ noevports
  ✓ nogetaddrinfo
  ✓ nokqueue
  ✓ noktls
  ✓ nopoll
  ✓ noreuseport
  ✓ nosplice
  ✓ numa-cpu-mapping
  ✓ pidfile
  ✓ profiling.memory
  ✓ profiling.memory.on
  ✓ profiling.tasks
  ✓ profiling.tasks.automatic
  ✓ profiling.tasks.on
  ✓ quiet
  ✓ server-state-base
  ✓ server-state-file
  ✓ set-dumpable
  ✓ setcap
  ✓ spread-checks
  ✓ ssl-default-bind-ciphers
  ✓ ssl-default-bind-ciphersuites
  ✓ ssl-default-bind-client-sigalgs
  ✓ ssl-default-bind-curves
  ✓ ssl-default-bind-options
  ✓ ssl-default-bind-sigalgs
  ✓ ssl-default-server-ciphers
  ✓ ssl-default-server-ciphersuites
  ✓ ssl-default-server-client-sigalgs
  ✓ ssl-default-server-curves
  ✓ ssl-default-server-options
  ✓ ssl-default-server-sigalgs
  ✓ ssl-dh-param-file
  ✓ ssl-engine
  ✓ ssl-load-extra-del-ext
  ✓ ssl-load-extra-files
  ✓ ssl-mode-async
  ✓ ssl-propquery
  ✓ ssl-provider
  ✓ ssl-provider-path
  ✓ ssl-security-level
  ✓ ssl-server-verify
  ✓ strict-limits
  ✓ thread-groups
  ✓ tune.applet.zero-copy-forwarding
  ✓ tune.buffers.limit
  ✓ tune.buffers.reserve
  ✓ tune.bufsize
  ✓ tune.bufsize.small
  ✓ tune.comp.maxlevel
  ✓ tune.disable-fast-forward
  ✓ tune.disable-zero-copy-forwarding
  ✓ tune.epoll.mask-events
  ✓ tune.events.max-events-at-once
  ✓ tune.fail-alloc
  ✓ tune.fd.edge-triggered
  ✓ tune.h1.zero-copy-fwd-recv
  ✓ tune.h1.zero-copy-fwd-send
  ✓ tune.h2.be.glitches-threshold
  ✓ tune.h2.be.initial-window-size
  ✓ tune.h2.be.max-concurrent-streams
  ✓ tune.h2.be.rxbuf
  ✓ tune.h2.fe.glitches-threshold
  ✓ tune.h2.fe.initial-window-size
  ✓ tune.h2.fe.max-concurrent-streams
  ✓ tune.h2.fe.max-total-streams
  ✓ tune.h2.fe.rxbuf
  ✓ tune.h2.header-table-size
  ✓ tune.h2.initial-window-size
  ✓ tune.h2.max-concurrent-streams
  ✓ tune.h2.max-frame-size
  ✓ tune.h2.zero-copy-fwd-send
  ✓ tune.http.cookielen
  ✓ tune.http.logurilen
  ✓ tune.http.maxhdr
  ✓ tune.idle-pool.shared
  ✓ tune.idletimer
  ✓ tune.lua.bool-sample-conversion
  ✓ tune.lua.burst-timeout
  ✓ tune.lua.forced-yield
  ✓ tune.lua.log.loggers
  ✓ tune.lua.log.stderr
  ✓ tune.lua.maxmem
  ✓ tune.lua.service-timeout
  ✓ tune.lua.session-timeout
  ✓ tune.lua.task-timeout
  ✓ tune.max-checks-per-thread
  ✓ tune.max-rules-at-once
  ✓ tune.maxaccept
  ✓ tune.maxpollevents
  ✓ tune.maxrewrite
  ✓ tune.memory.fail-alloc
  ✓ tune.memory.hot-size
  ✓ tune.memory.pool-allocator
  ✓ tune.pattern.cache-size
  ✓ tune.peers.max-updates-at-once
  ✓ tune.pipesize
  ✓ tune.pool.high-fd-ratio
  ✓ tune.pool.low-fd-ratio
  ✓ tune.pt.zero-copy-forwarding
  ✓ tune.quic.be.cc.cubic-min-losses
  ✓ tune.quic.be.cc.hystart
  ✓ tune.quic.be.cc.max-frame-loss
  ✓ tune.quic.be.cc.max-win-size
  ✓ tune.quic.be.cc.reorder-ratio
  ✓ tune.quic.be.max-idle-timeout
  ✓ tune.quic.be.sec.glitches-threshold
  ✓ tune.quic.be.stream.data-ratio
  ✓ tune.quic.be.stream.max-concurrent
  ✓ tune.quic.be.stream.rxbuf
  ✓ tune.quic.be.tx.pacing
  ✓ tune.quic.be.tx.udp-gso
  ✓ tune.quic.cc-hystart
  ✓ tune.quic.fe.cc.cubic-min-losses
  ✓ tune.quic.fe.cc.hystart
  ✓ tune.quic.fe.cc.max-frame-loss
  ✓ tune.quic.fe.cc.max-win-size
  ✓ tune.quic.fe.cc.reorder-ratio
  ✓ tune.quic.fe.max-idle-timeout
  ✓ tune.quic.fe.sec.glitches-threshold
  ✓ tune.quic.fe.sec.retry-threshold
  ✓ tune.quic.fe.sock-per-conn
  ✓ tune.quic.fe.stream.data-ratio
  ✓ tune.quic.fe.stream.max-concurrent
  ✓ tune.quic.fe.stream.rxbuf
  ✓ tune.quic.fe.tx.pacing
  ✓ tune.quic.fe.tx.udp-gso
  ✓ tune.quic.frontend.conn-tx-buffers.limit
  ✓ tune.quic.frontend.glitches-threshold
  ✓ tune.quic.frontend.max-idle-timeout
  ✓ tune.quic.frontend.max-streams-bidi
  ✓ tune.quic.listen
  ✓ tune.quic.max-frame-loss
  ✓ tune.quic.mem.tx-max
  ✓ tune.quic.reorder-ratio
  ✓ tune.quic.retry-threshold
  ✓ tune.quic.socket.owner
  ✓ tune.quic.zero-copy-fwd-send
  ✓ tune.rcvbuf.backend
  ✓ tune.rcvbuf.client
  ✓ tune.rcvbuf.frontend
  ✓ tune.rcvbuf.server
  ✓ tune.recv_enough
  ✓ tune.renice.runtime
  ✓ tune.renice.startup
  ✓ tune.ring.queues
  ✓ tune.runqueue-depth
  ✓ tune.sched.low-latency
  ✓ tune.sndbuf.backend
  ✓ tune.sndbuf.client
  ✓ tune.sndbuf.frontend
  ✓ tune.sndbuf.server
  ✓ tune.ssl.bufsize
  ✓ tune.ssl.cachesize
  ✓ tune.ssl.capture-buffer-size
  ✓ tune.ssl.capture-cipherlist-size
  ✓ tune.ssl.default-dh-param
  ✓ tune.ssl.force-private-cache
  ✓ tune.ssl.hard-maxrecord
  ✓ tune.ssl.keylog
  ✓ tune.ssl.lifetime
  ✓ tune.ssl.maxrecord
  ✓ tune.ssl.ocsp-update.maxdelay
  ✓ tune.ssl.ocsp-update.maxhour
  ✓ tune.ssl.ocsp-update.mindelay
  ✓ tune.ssl.ocsp-update.minthour
  ✓ tune.ssl.ssl-ctx-cache-size
  ✓ tune.stick-counters
  ✓ tune.takeover-other-tg-connections
  ✓ tune.vars.global-max-size
  ✓ tune.vars.proc-max-size
  ✓ tune.vars.reqres-max-size
  ✓ tune.vars.sess-max-size
  ✓ tune.vars.txn-max-size
  ✓ tune.zlib.memlevel
  ✓ tune.zlib.windowsize
  ✓ uid
  ✓ ulimit-n
  ✓ unix-bind
  ✓ user
  ✓ warn-blocked-traffic-after
  ✓ wurfl-cache-size
  ✓ wurfl-data-file
  ✓ wurfl-engine-mode
  ✓ wurfl-information-list
  ✓ wurfl-information-list-separator
  ✓ wurfl-patch-file
  ✓ wurfl-useragent-priority
  ✓ zero-warning
```

</details>

### Appendix B: Implemented Server Options

<details>
<summary>All Implemented Server Options (55)</summary>

```
  ✓ address
  ✓ agent_addr
  ✓ agent_check
  ✓ agent_inter
  ✓ agent_port
  ✓ agent_send
  ✓ alpn
  ✓ backup
  ✓ ca_file
  ✓ check
  ✓ check_proto
  ✓ check_send_proxy
  ✓ check_sni
  ✓ check_ssl
  ✓ cookie
  ✓ crt
  ✓ disabled
  ✓ enabled
  ✓ error_limit
  ✓ fall
  ✓ id
  ✓ init_addr
  ✓ inline
  ✓ inter
  ✓ max_reuse
  ✓ maxconn
  ✓ maxqueue
  ✓ minconn
  ✓ namespace
  ✓ observe
  ✓ on_error
  ✓ on_marked_down
  ✓ on_marked_up
  ✓ pool_max_conn
  ✓ pool_purge_delay
  ✓ port
  ✓ proto
  ✓ redir
  ✓ resolve_prefer
  ✓ resolvers
  ✓ rise
  ✓ send_proxy
  ✓ send_proxy_v2
  ✓ slowstart
  ✓ sni
  ✓ source
  ✓ ssl
  ✓ ssl_max_ver
  ✓ ssl_min_ver
  ✓ template_spread
  ✓ tfo
  ✓ track
  ✓ usesrc
  ✓ verify
  ✓ weight
```

</details>
