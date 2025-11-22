# HAProxy Config Translator - Complete Syntax Reference

This document provides a complete reference for the HAProxy DSL syntax.

## Table of Contents

1. [File Structure](#file-structure)
2. [Data Types](#data-types)
3. [Variables](#variables)
4. [Global Section](#global-section)
5. [Defaults Section](#defaults-section)
6. [Frontend Section](#frontend-section)
7. [Backend Section](#backend-section)
8. [Listen Section](#listen-section)
9. [Resolvers Section](#resolvers-section)
10. [Peers Section](#peers-section)
11. [Mailers Section](#mailers-section)
12. [Loops](#loops)
13. [Comments](#comments)

---

## File Structure

A configuration file consists of one or more sections:

```javascript
// Optional: Variable definitions
variables {
    // ...
}

// Optional: Global settings
global {
    // ...
}

// Optional: Default settings
defaults {
    // ...
}

// One or more frontends
frontend name {
    // ...
}

// One or more backends
backend name {
    // ...
}

// Combined frontend+backend
listen name {
    // ...
}

// Optional: DNS resolution
resolvers name {
    // ...
}

// Optional: Peer synchronization
peers name {
    // ...
}

// Optional: Email alerts
mailers name {
    // ...
}
```

---

## Data Types

### Strings
```javascript
// Double-quoted strings
log: "127.0.0.1 local0"

// Can contain special characters
path: "/var/lib/haproxy"

// Can include variables
host: "${env.API_HOST}"
```

### Numbers
```javascript
maxconn: 4096
weight: 10
port: 8080
```

### Booleans
```javascript
daemon: true
check: false
```

### Durations
```javascript
timeout: "30s"      // seconds
timeout: "5m"       // minutes
timeout: "1h"       // hours
timeout: "1d"       // days
timeout: "500ms"    // milliseconds
timeout: "1h30m"    // combined
```

### Arrays
```javascript
// Simple array
options: ["httplog", "dontlognull"]

// Array of objects
servers: [
    { name: "web1", address: "10.0.1.1", port: 8080 },
    { name: "web2", address: "10.0.1.2", port: 8080 }
]
```

### Objects
```javascript
// Inline object
ssl: { cert: "/path/to/cert.pem", verify: "required" }

// Multi-line object
ssl: {
    cert: "/path/to/cert.pem"
    ca_file: "/path/to/ca.pem"
    verify: "required"
}
```

---

## Variables

### Variable Definition
```javascript
variables {
    // Simple values
    app_port = 8080
    check_interval = "3s"

    // Strings
    log_server = "127.0.0.1"

    // Can reference other variables
    full_log = "${log_server} local0"
}
```

### Variable Usage
```javascript
backend api {
    servers: [
        { name: "api1", address: "10.0.1.1", port: ${app_port} }
    ]
}
```

### Environment Variables
```javascript
global {
    // Direct reference
    maxconn: ${env.HAPROXY_MAXCONN}

    // With default value
    maxconn: ${env.HAPROXY_MAXCONN:-4096}
}
```

---

## Global Section

```javascript
global {
    // === Process Management ===
    daemon: true                    // Run as daemon
    user: "haproxy"                 // Run as user
    group: "haproxy"                // Run as group
    chroot: "/var/lib/haproxy"      // Chroot directory
    pidfile: "/var/run/haproxy.pid" // PID file path

    // === Connection Limits ===
    maxconn: 4096                   // Max connections
    maxsslconn: 1000               // Max SSL connections
    maxconnrate: 1000              // Max conn/sec
    maxsessrate: 1000              // Max sessions/sec

    // === Threading ===
    nbthread: 4                     // Number of threads
    nbproc: 1                       // Number of processes (deprecated)

    // === Logging ===
    log: "127.0.0.1 local0"        // Log destination
    log-send-hostname: true        // Include hostname
    log-tag: "haproxy"             // Log tag

    // === SSL/TLS Defaults ===
    ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:..."
    ssl-default-bind-ciphersuites: "TLS_AES_128_GCM_SHA256:..."
    ssl-default-bind-options: "ssl-min-ver TLSv1.2 no-tls-tickets"
    ssl-default-server-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256"
    ssl-dh-param-file: "/etc/haproxy/dhparam.pem"
    ca-base: "/etc/ssl/certs"
    crt-base: "/etc/ssl/private"

    // === Performance Tuning ===
    tune.bufsize: 16384
    tune.maxrewrite: 1024
    tune.ssl.cachesize: 20000
    tune.ssl.lifetime: 300
    tune.http.maxhdr: 101
    tune.comp.maxlevel: 5

    // === Stats Socket ===
    stats_socket: {
        path: "/var/run/haproxy.sock"
        level: "admin"
        mode: "660"
    }
}
```

### Complete Global Directives List

The translator supports all 165 non-deprecated HAProxy global directives. See [FEATURE_PARITY_REPORT.md](../FEATURE_PARITY_REPORT.md) for the complete list.

---

## Defaults Section

```javascript
defaults {
    // === Mode ===
    mode: "http"                    // http or tcp

    // === Timeouts ===
    timeouts: {
        connect: "5s"               // Backend connection timeout
        client: "30s"               // Client inactivity timeout
        server: "30s"               // Server inactivity timeout
        check: "5s"                 // Health check timeout
        http_request: "10s"         // HTTP request timeout
        http_keep_alive: "10s"      // Keep-alive timeout
        queue: "30s"                // Queue timeout
        tunnel: "1h"                // Tunnel timeout
        tarpit: "10s"               // Tarpit delay
    }

    // === Options ===
    options: [
        "httplog",
        "dontlognull",
        "http-server-close",
        "forwardfor except 127.0.0.0/8",
        "redispatch"
    ]

    // === Retries ===
    retries: 3
    retry_on: "conn-failure empty-response response-timeout"

    // === Error Files ===
    errorfiles: {
        400: "/etc/haproxy/errors/400.http"
        403: "/etc/haproxy/errors/403.http"
        500: "/etc/haproxy/errors/500.http"
    }

    // === Connection Reuse ===
    http_reuse: "safe"              // never, safe, aggressive, always

    // === Logging ===
    log_format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC"
    log_tag: "haproxy"

    // === Compression ===
    compression: {
        algo: "gzip"
        type: "text/html text/plain application/json"
    }

    // === Default Server Options ===
    default_server: {
        check: true
        inter: "3s"
        fall: 3
        rise: 2
    }
}
```

---

## Frontend Section

```javascript
frontend name {
    // === Bind Addresses ===
    bind: "*:80"                    // Simple bind

    // Multiple/complex binds
    binds: [
        { address: "*:80" },
        {
            address: "*:443",
            ssl: {
                cert: "/path/to/cert.pem",
                ca_file: "/path/to/ca.pem",
                verify: "optional",
                alpn: "h2,http/1.1"
            }
        },
        {
            address: "/var/run/socket.sock",
            mode: "660",
            user: "haproxy"
        }
    ]

    // === Mode & Settings ===
    mode: "http"
    maxconn: 10000
    backlog: 10000

    // === Logging ===
    log: "127.0.0.1 local0"
    log_format: "%ci:%cp [%tr] %ft %b/%s"
    log_tag: "frontend"

    // === ACLs ===
    acls: [
        { name: "is_api", criterion: "path_beg /api/" },
        { name: "is_static", criterion: "path_end .jpg .png .css .js" },
        { name: "host_example", criterion: "hdr(host) -i example.com" },
        { name: "src_local", criterion: "src 192.168.0.0/16" }
    ]

    // === Backend Selection ===
    use_backends: [
        { backend: "api_servers", condition: "if is_api" },
        { backend: "static_servers", condition: "if is_static" }
    ]
    default_backend: "webservers"

    // === HTTP Request Rules ===
    http-request {
        deny if { path_beg /admin } !src_local
        set-header "X-Forwarded-Proto" "https" if { ssl_fc }
        add-header "X-Request-ID" "%[uuid()]"
        redirect scheme "https" unless { ssl_fc }
    }

    // === HTTP Response Rules ===
    http-response {
        set-header "X-Frame-Options" "DENY"
        del-header "Server"
    }

    // === TCP Rules ===
    tcp-request {
        connection reject if { src -f /etc/haproxy/blacklist.lst }
        content accept if { req.ssl_hello_type 1 }
        inspect-delay "5s"
    }

    // === Stick Table ===
    stick_table: {
        type: "ip"
        size: "100k"
        expire: "30m"
        store: "conn_cur,conn_rate(10s)"
    }

    // === Stats ===
    stats: {
        enable: true
        uri: "/stats"
        refresh: "10s"
        auth: "admin:password"
    }

    // === Capture ===
    captures: [
        { type: "request", header: "Host", length: 64 },
        { type: "response", header: "Content-Type", length: 64 }
    ]

    // === Rate Limiting ===
    rate_limit_sessions: 1000

    // === Monitoring ===
    monitor_uri: "/health"
    monitor_fail: "if { nbsrv(backend) lt 1 }"

    // === Compression ===
    compression: {
        algo: "gzip"
        type: "text/html text/plain"
    }

    // === Unique ID ===
    unique_id_format: "%{+X}o\\ %ci:%cp_%fi:%fp_%Ts_%rt:%pid"
    unique_id_header: "X-Request-ID"
}
```

---

## Backend Section

```javascript
backend name {
    // === Mode & Balance ===
    mode: "http"
    balance: "roundrobin"           // roundrobin, leastconn, source,
                                    // uri, url_param, hdr, rdp-cookie,
                                    // random, first, static-rr, hash

    // === Hash Options ===
    hash_type: "consistent"         // map-based or consistent
    hash_balance_factor: 150

    // === Options ===
    options: [
        "httpchk GET /health",
        "http-server-close",
        "forwardfor"
    ]

    // === Servers ===
    servers: [
        {
            name: "web1",
            address: "192.168.1.10",
            port: 8080,
            check: true,
            weight: 10,
            maxconn: 100,
            backup: false,

            // Health check options
            inter: "3s",
            fall: 3,
            rise: 2,

            // SSL options
            ssl: true,
            verify: "required",
            ca_file: "/etc/ssl/ca.pem",
            sni: "req.hdr(host)",

            // Connection options
            maxqueue: 100,
            slowstart: "30s",

            // Agent check
            agent_check: true,
            agent_addr: "192.168.1.10",
            agent_port: 9999,
            agent_inter: "5s"
        }
    ]

    // === Server Templates ===
    server_templates: [
        {
            prefix: "srv",
            range: "1-10",
            address: "_http._tcp.example.com",
            port: 8080,
            check: true,
            resolvers: "mydns"
        }
    ]

    // === Default Server Options ===
    default_server: {
        check: true
        inter: "3s"
        fall: 3
        rise: 2
        maxconn: 100
    }

    // === HTTP Check ===
    http_check: {
        send: {
            method: "GET"
            uri: "/health"
            version: "HTTP/1.1"
            headers: {
                Host: "api.example.com"
            }
        }
        expect: { status: "200" }
    }

    // === TCP Check ===
    tcp_check: [
        { connect: true },
        { send: "PING\\r\\n" },
        { expect: { string: "+PONG" } }
    ]

    // === Stick Table & Rules ===
    stick_table: {
        type: "ip"
        size: "100k"
        expire: "30m"
        store: "conn_cur"
    }

    stick_rules: [
        { type: "on", pattern: "src" },
        { type: "match", pattern: "src" },
        { type: "store-request", pattern: "src" }
    ]

    // === Cookie Persistence ===
    cookie: {
        name: "SERVERID"
        mode: "insert"
        options: ["indirect", "nocache"]
    }

    // === HTTP Reuse ===
    http_reuse: "aggressive"

    // === Retries ===
    retries: 3
    retry_on: "conn-failure empty-response"

    // === Email Alert ===
    email_alert: {
        mailers: "alerters"
        from: "haproxy@example.com"
        to: "ops@example.com"
        level: "alert"
    }

    // === HTTP Request/Response ===
    http-request {
        set-header "X-Backend" "api"
    }

    http-response {
        add-header "X-Served-By" "%s"
    }

    // === Source Address ===
    source: "192.168.1.100"
}
```

---

## Listen Section

The `listen` section combines frontend and backend:

```javascript
listen name {
    // All frontend properties
    bind: "*:8404"
    mode: "http"

    // All backend properties
    balance: "roundrobin"
    servers: [
        { name: "app1", address: "10.0.1.1", port: 8080, check: true }
    ]

    // Commonly used for stats
    stats: {
        enable: true
        uri: "/stats"
        refresh: "10s"
        auth: "admin:password"
        admin: "if LOCALHOST"
    }
}
```

---

## Resolvers Section

```javascript
resolvers mydns {
    nameservers: [
        { name: "dns1", address: "8.8.8.8", port: 53 },
        { name: "dns2", address: "8.8.4.4", port: 53 }
    ]

    resolve_retries: 3
    timeout_resolve: "1s"
    timeout_retry: "1s"
    hold_valid: "10s"
    hold_obsolete: "30s"
}
```

---

## Peers Section

```javascript
peers mypeers {
    peer_list: [
        { name: "haproxy1", address: "192.168.1.1", port: 1024 },
        { name: "haproxy2", address: "192.168.1.2", port: 1024 }
    ]
}
```

---

## Mailers Section

```javascript
mailers alerters {
    mailers: [
        { name: "smtp1", address: "smtp.example.com", port: 587 }
    ]

    timeout: "10s"
}
```

---

## Loops

### For Loop with Range

```javascript
backend dynamic {
    for i in [1, 2, 3, 4, 5] {
        server "web${i}" "10.0.1.${i}":8080 check
    }
}
```

### For Loop with List

```javascript
variables {
    ports = [8080, 8081, 8082]
}

backend multi_port {
    for port in ${ports} {
        server "app_${port}" "10.0.1.1":${port} check
    }
}
```

---

## Comments

```javascript
// Single line comment

/*
 * Multi-line
 * comment
 */

global {
    daemon: true  // Inline comment
}
```

---

## See Also

- [Quick Start Guide](QUICK_START.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Architecture Guide](ARCHITECTURE.md)
