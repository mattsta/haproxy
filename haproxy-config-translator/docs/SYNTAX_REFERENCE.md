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
12. [Templates](#templates)
13. [Loops](#loops)
14. [Comments](#comments)

---

## File Structure

**IMPORTANT:** Every DSL configuration file must be wrapped in a `config name { }` block:

```javascript
config my_config {
  // Optional: Variable definitions
  let variable_name = value

  // Optional: Templates
  template template_name {
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
}
```

---

## Data Types

### Strings
```javascript
// Double-quoted strings
log: "/dev/log"
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
// Also accepts: yes, no, on, off, 1, 0
```

### Durations
Durations are specified without quotes:
```javascript
timeout: {
  connect: 5s       // seconds
  client: 30s
  server: 5m        // minutes
  tunnel: 1h        // hours
  check: 500ms      // milliseconds
}
```

### Identifiers
Some values like `mode` take identifiers, not strings:
```javascript
// Correct - identifier without quotes
mode: http
mode: tcp
balance: roundrobin

// Incorrect - don't quote these
mode: "http"  // Wrong!
```

### Arrays
```javascript
// Simple array
option: ["httplog", "dontlognull"]

// Multi-line array
alpn: ["h2", "http/1.1"]
```

---

## Variables

### Variable Definition
Variables are defined with `let`:
```javascript
config my_config {
  // Simple values
  let app_port = 8080
  let check_interval = 3s

  // Strings
  let log_server = "/dev/log"

  backend api {
    servers {
      server api1 {
        address: "10.0.1.1"
        port: ${app_port}
        inter: ${check_interval}
      }
    }
  }
}
```

### Environment Variables
```javascript
config my_config {
  global {
    // Direct reference
    maxconn: ${env.HAPROXY_MAXCONN}
  }

  backend api {
    servers {
      server api1 {
        address: "${env.API_HOST}"
        port: 8080
      }
    }
  }
}
```

---

## Global Section

```javascript
config my_config {
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

    // === Logging ===
    log "/dev/log" local0 info     // Log destination (directive style)
    log-send-hostname: "myhost"    // Include hostname
    log-tag: "haproxy"             // Log tag

    // === SSL/TLS Defaults ===
    ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:..."
    ssl-default-bind-ciphersuites: "TLS_AES_128_GCM_SHA256:..."
    ssl-default-bind-options: ["ssl-min-ver TLSv1.2", "no-tls-tickets"]
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
    stats_socket "/var/run/haproxy.sock" {
      level: "admin"
      mode: "660"
    }
  }
}
```

### Complete Global Directives List

The translator supports all 165 non-deprecated HAProxy global directives. See [FEATURE_PARITY_REPORT.md](../FEATURE_PARITY_REPORT.md) for the complete list.

---

## Defaults Section

```javascript
config my_config {
  defaults {
    // === Mode ===
    mode: http                      // http or tcp (identifier, not string)

    // === Timeouts ===
    timeout: {
      connect: 5s                   // Backend connection timeout
      client: 30s                   // Client inactivity timeout
      server: 30s                   // Server inactivity timeout
      check: 5s                     // Health check timeout
      http_request: 10s             // HTTP request timeout
      http_keep_alive: 10s          // Keep-alive timeout
      queue: 30s                    // Queue timeout
      tunnel: 1h                    // Tunnel timeout
    }

    // === Options ===
    option: [
      "httplog",
      "dontlognull",
      "http-server-close",
      "forwardfor except 127.0.0.0/8",
      "redispatch"
    ]

    // === Retries ===
    retries: 3

    // === Error Handling ===
    errorloc 503 "http://maintenance.example.com"
  }
}
```

---

## Frontend Section

```javascript
config my_config {
  frontend web {
    // === Bind Addresses ===
    bind *:80                       // Simple bind (directive style)

    // SSL bind
    bind *:443 ssl {
      cert: "/path/to/cert.pem"
      ca-file: "/path/to/ca.pem"
      verify: "optional"
      alpn: ["h2", "http/1.1"]
    }

    // Unix socket bind
    bind /var/run/socket.sock mode "660" user "haproxy"

    // === Mode & Settings ===
    mode: http                      // http or tcp (identifier)
    maxconn: 10000
    backlog: 10000

    // === Logging ===
    log: "/dev/log local0"
    log-format: "%ci:%cp [%tr] %ft %b/%s"
    log-tag: "frontend"

    // === ACLs ===
    acl is_api {
      path_beg "/api/"
    }

    acl is_static {
      path_end ".jpg" ".png" ".css" ".js"
    }

    acl host_example {
      hdr "host" "-i" "example.com"
    }

    // === Backend Selection ===
    use_backend api_servers if is_api
    use_backend static_servers if is_static
    default_backend: webservers

    // === HTTP Request Rules ===
    http-request {
      deny if { path_beg /admin } !src_local
      set-header "X-Forwarded-Proto" "https" if ssl_fc
      add-header "X-Request-ID" "%[uuid()]"
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
      inspect-delay 5s
    }

    // === Stick Table ===
    stick-table {
      type: ip
      size: 100000
      expire: 30m
      store: ["conn_cur", "conn_rate(10s)"]
    }

    // === Stats ===
    stats {
      enable: true
      uri: "/stats"
      refresh: 10s
      auth: "admin:password"
    }

    // === Capture ===
    capture request header "Host" 64
    capture response header "Content-Type" 64

    // === Rate Limiting ===
    rate-limit sessions: 1000

    // === Monitoring ===
    monitor_uri: "/health"

    // === Unique ID ===
    unique-id-format: "%{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid"
    unique-id-header: "X-Request-ID"
  }
}
```

---

## Backend Section

```javascript
config my_config {
  backend api {
    // === Mode & Balance ===
    mode: http                      // http or tcp (identifier)
    balance: roundrobin             // roundrobin, leastconn, source,
                                   // uri, url_param, random, first,
                                   // static-rr, hdr, rdp-cookie

    // === Hash Options ===
    hash-type: consistent           // map-based or consistent
    hash-balance-factor: 150

    // === Options ===
    option: [
      "httpchk GET /health",
      "http-server-close",
      "forwardfor"
    ]

    // === Default Server Options ===
    default-server {
      check: true
      inter: 3s
      fall: 3
      rise: 2
      maxconn: 100
    }

    // === Servers ===
    servers {
      // Full syntax with all options
      server web1 {
        address: "192.168.1.10"
        port: 8080
        check: true
        weight: 10
        maxconn: 100
        backup: false

        // Health check options
        inter: 3s
        fall: 3
        rise: 2

        // SSL options
        ssl: true
        verify: "required"
        ca-file: "/etc/ssl/ca.pem"
        sni: "req.hdr(host)"

        // Connection options
        maxqueue: 100
        slowstart: 30s

        // Agent check
        agent-check: true
        agent-addr: "192.168.1.10"
        agent-port: 9999
        agent-inter: 5s
      }

      // Compact syntax with comma-separated properties
      server web2 { address: "192.168.1.11", port: 8080, check: true, weight: 10 }

      // Inline syntax (alternative compact format)
      server web3 address: "192.168.1.12" port: 8080 check: true
    }

    // === Server Templates ===
    server-template srv [1..10] {
      address: "_http._tcp.example.com"
      port: 8080
      check: true
      resolvers: "mydns"
    }

    // === HTTP Check ===
    http-check {
      send method GET uri "/health" headers {
        header "Host" "api.example.com"
      }
      expect status 200
    }

    // === TCP Check ===
    tcp-check {
      connect
      send "PING\r\n"
      expect string "+PONG"
    }

    // === Stick Table & Rules ===
    stick-table {
      type: ip
      size: 100000
      expire: 30m
      store: ["conn_cur"]
    }

    stick on src
    stick match src
    stick store-request src

    // === HTTP Reuse ===
    http-reuse: aggressive          // never, safe, aggressive, always

    // === Retries ===
    retries: 3
    retry-on: "conn-failure empty-response"

    // === Email Alert ===
    email-alert {
      mailers: alerters
      from: "haproxy@example.com"
      to: "ops@example.com"
      level: alert
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
}
```

---

## Listen Section

The `listen` section combines frontend and backend:

```javascript
config my_config {
  listen stats {
    // All frontend properties
    bind *:8404
    mode: http

    // All backend properties
    balance: roundrobin

    servers {
      server app1 {
        address: "10.0.1.1"
        port: 8080
        check: true
      }
    }

    // Commonly used for stats
    stats {
      enable: true
      uri: "/stats"
      refresh: 10s
      auth: "admin:password"
      admin if LOCALHOST
    }
  }
}
```

---

## Resolvers Section

```javascript
config my_config {
  resolvers mydns {
    nameserver dns1 "8.8.8.8" 53
    nameserver dns2 "8.8.4.4" 53

    resolve_retries: 3
    timeout_resolve: 1s
    timeout_retry: 1s
    hold_valid: 10s
    hold_obsolete: 30s
  }
}
```

---

## Peers Section

```javascript
config my_config {
  peers mypeers {
    peer haproxy1 "192.168.1.1" 1024
    peer haproxy2 "192.168.1.2" 1024
  }
}
```

---

## Mailers Section

```javascript
config my_config {
  mailers alerters {
    timeout_mail: 10s
    mailer smtp1 "smtp.example.com" 587
  }
}
```

---

## Templates

Templates allow you to define reusable property sets for servers, health checks, and ACLs:

### Server Templates
```javascript
config my_config {
  template server_defaults {
    check: true
    inter: 3s
    rise: 2
    fall: 3
  }

  backend api {
    servers {
      server api1 {
        address: "10.0.1.1"
        port: 8080
        @server_defaults    // Spread template properties
      }
      server api2 {
        address: "10.0.1.2"
        port: 8080
        @server_defaults
      }
    }
  }
}
```

### Health Check Templates
```javascript
config my_config {
  template http_health {
    method: "GET"
    uri: "/health"
    expect_status: 200
  }

  backend api {
    balance: roundrobin
    option: ["httpchk"]

    // Apply template to entire health check
    health-check @http_health

    servers {
      server api1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
```

### ACL Templates
```javascript
config my_config {
  template api_path_acl {
    criterion: "path_beg"
    values: ["/api/"]
  }

  template internal_src_acl {
    criterion: "src"
    values: ["10.0.0.0/8", "192.168.0.0/16"]
  }

  frontend web {
    bind *:80

    // Apply ACL templates
    acl is_api @api_path_acl
    acl is_internal @internal_src_acl

    use_backend api_servers if is_api
    default_backend: web_servers
  }
}
```

### Backend Templates

Backend templates define common backend-level configurations that can be spread into multiple backends using `@template_name`:

```javascript
config backend_templates {
  // Define common backend configuration
  template production_backend {
    balance: leastconn
    option: ["httpchk GET /health", "forwardfor"]
    retries: 3
  }

  template standard_backend {
    balance: roundrobin
    option: ["httpchk"]
  }

  // Apply backend template with @template_name
  backend api {
    @production_backend

    servers {
      server api1 { address: "10.0.1.1", port: 8080, check: true }
      server api2 { address: "10.0.1.2", port: 8080, check: true }
    }
  }

  // Backend template with explicit overrides
  backend web {
    @standard_backend
    balance: leastconn  // Override template's balance

    servers {
      server web1 { address: "10.0.2.1", port: 8080, check: true }
    }
  }
}
```

Backend templates can include:
- `balance`: Load balancing algorithm (roundrobin, leastconn, source, etc.)
- `option`: List of backend options
- `retries`: Number of retries on failure
- `maxconn`: Maximum connections
- `cookie`: Cookie configuration
- `timeout_server`, `timeout_connect`, `timeout_check`: Timeout settings
- `mode`: Protocol mode (http, tcp)

### Multiple Template Types Together
```javascript
config production {
  // Backend template for production backends
  template prod_backend {
    balance: leastconn
    option: ["httpchk", "forwardfor"]
    retries: 3
  }

  // Server template for standardized health checks
  template prod_server {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    maxconn: 500
  }

  // Health check template for HTTP services
  template http_health {
    method: "GET"
    uri: "/health"
    expect_status: 200
  }

  // ACL template for API routing
  template api_acl {
    criterion: "path_beg"
    values: ["/api/"]
  }

  frontend web {
    bind *:80
    acl is_api @api_acl
    use_backend api if is_api
    default_backend: web
  }

  // Backend with multiple template types combined
  backend api {
    @prod_backend  // Backend-level template
    health-check @http_health  // Health check template

    servers {
      for i in [1..5] {
        server "api${i}" {
          address: "10.0.1.${i}"
          port: 8080
          @prod_server  // Server template
        }
      }
    }
  }
}
```

---

## Loops

### For Loop with Range

```javascript
config my_config {
  backend dynamic {
    servers {
      for i in [1..5] {
        server "web${i}" {
          address: "10.0.1.${i}"
          port: 8080
          check: true
        }
      }
    }
  }
}
```

### For Loop with List

```javascript
config my_config {
  backend multi_port {
    servers {
      for port in [8080, 8081, 8082] {
        server "app_${port}" {
          address: "10.0.1.1"
          port: ${port}
          check: true
        }
      }
    }
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

config my_config {
  global {
    daemon: true  // Inline comment
  }
}
```

---

## Key Syntax Rules

1. **Config Wrapper Required**: All DSL files must be wrapped in `config name { }`

2. **Mode Values Are Identifiers**: Use `mode: http` not `mode: "http"`

3. **Bind Is a Directive**: Use `bind *:80` not `bind: "*:80"`

4. **Servers In Blocks**: Define servers inside `servers { }` blocks

5. **Durations Without Quotes**: Use `inter: 3s` not `inter: "3s"`

6. **Balance Values Are Identifiers**: Use `balance: roundrobin` not `balance: "roundrobin"`

---

## See Also

- [Quick Start Guide](QUICK_START.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Architecture Guide](ARCHITECTURE.md)
