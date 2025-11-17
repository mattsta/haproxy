# HAProxy Configuration Translator - Usage Guide

This comprehensive guide covers all aspects of using the HAProxy Configuration Translator, from basic examples to advanced patterns.

## Table of Contents

1. [Installation](#installation)
2. [CLI Usage](#cli-usage)
3. [DSL Syntax Guide](#dsl-syntax-guide)
4. [Common Patterns](#common-patterns)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Installation

### Prerequisites

- Python 3.9 or later
- `uv` package manager (recommended) or `pip`

### Install from Source

```bash
# Clone the repository
git clone https://github.com/haproxy/config-translator
cd config-translator/haproxy-config-translator

# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Verify installation
haproxy-translate --version
```

---

## CLI Usage

### Basic Commands

**Translate to stdout:**
```bash
haproxy-translate config.hap
```

**Translate to file:**
```bash
haproxy-translate config.hap -o /etc/haproxy/haproxy.cfg
```

**Validate only (no output):**
```bash
haproxy-translate config.hap --validate
```

**Watch mode (auto-regenerate on changes):**
```bash
haproxy-translate config.hap -o haproxy.cfg --watch
```

### Debugging and Inspection

**Show IR debug information:**
```bash
haproxy-translate config.hap --debug
```

Output includes:
- Frontends list
- Backends list
- Variables defined
- Templates defined
- Transformation steps

**Verbose output:**
```bash
haproxy-translate config.hap -o haproxy.cfg --verbose
```

Shows:
- Input file path
- Parser used
- Parse success info
- Output file location
- Lua scripts extracted

### Format Options

**Auto-detect format (default):**
```bash
haproxy-translate config.hap  # .hap → DSL parser
```

**Explicit format:**
```bash
haproxy-translate config.txt --format dsl
```

**List available formats:**
```bash
haproxy-translate --list-formats
```

### Lua Script Options

**Custom Lua output directory:**
```bash
haproxy-translate config.hap -o haproxy.cfg --lua-dir /etc/haproxy/lua
```

Default behavior:
- If `-o` specified: Lua scripts go to same directory as output
- If stdout: Lua scripts go to current directory

---

## DSL Syntax Guide

### Configuration Structure

Every DSL file starts with a `config` block:

```haproxy-dsl
config my_config {
    version: "2.0"

    // Sections...
    global { ... }
    defaults { ... }
    frontend name { ... }
    backend name { ... }
}
```

### Comments

```haproxy-dsl
// Single-line comment

/* Multi-line
   comment */
```

### Variables

#### Basic Variables

```haproxy-dsl
let port = 8080
let host = "example.com"
let enabled = true
```

#### Environment Variables

```haproxy-dsl
// With fallback
let port = env("BACKEND_PORT", "8080")

// Without fallback (error if not set)
let api_key = env("API_KEY")
```

#### String Interpolation

```haproxy-dsl
let host = "api.example.com"
let port = 8080
let url = "http://${host}:${port}"  // → "http://api.example.com:8080"
```

#### Nested Variable References

```haproxy-dsl
let base_ip = "10.0.1"
let server1 = "${base_ip}.10"  // → "10.0.1.10"
let server2 = "${base_ip}.20"  // → "10.0.1.20"
```

Multi-pass resolution handles complex references automatically.

### Templates

Templates define reusable configuration blocks:

```haproxy-dsl
template server_defaults {
    check: true
    inter: 3s
    rise: 2
    fall: 3
    maxconn: 100
}

backend app {
    servers {
        server web1 {
            address: "10.0.1.1"
            port: 8080
            @server_defaults  // Spread template
        }
    }
}
```

**Generated:**
```
server web1 10.0.1.1:8080 check inter 3s rise 2 fall 3 maxconn 100
```

### Loops

Generate repeated configurations:

```haproxy-dsl
// Range-based loop
servers {
    for i in [1..5] {
        server "web${i}" {
            address: "10.0.1.${i}"
            port: 8080
            check: true
        }
    }
}
```

**Generated:**
```
server web1 10.0.1.1:8080 check
server web2 10.0.1.2:8080 check
server web3 10.0.1.3:8080 check
server web4 10.0.1.4:8080 check
server web5 10.0.1.5:8080 check
```

### Conditionals

```haproxy-dsl
if env("ENVIRONMENT") == "production" {
    backend api {
        balance: leastconn
        maxconn: 10000
    }
} else {
    backend api {
        balance: roundrobin
        maxconn: 100
    }
}
```

### Global Section

```haproxy-dsl
global {
    daemon: true
    maxconn: 4096
    user: "haproxy"
    group: "haproxy"
    pidfile: "/var/run/haproxy.pid"

    // Logging
    log "/dev/log" local0 info
    log "/dev/log" local1 notice

    // SSL
    ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:..."
    ssl-default-bind-options: [
        "ssl-min-ver TLSv1.2",
        "no-tls-tickets"
    ]

    // Lua scripts
    lua {
        load "/etc/haproxy/lua/auth.lua"
        script custom_handler {
            // Inline Lua code
            core.register_action("custom", {"http-req"}, function(txn)
                -- Custom logic
            end)
        }
    }

    // Stats
    stats {
        enable: true
        uri: "/admin/stats"
        auth: "admin:secret"
    }
}
```

### Defaults Section

```haproxy-dsl
defaults {
    mode: http
    retries: 3

    timeout: {
        connect: 5s
        client: 50s
        server: 50s
        check: 10s
        queue: 30s
    }

    log: "global"
    option: ["httplog", "dontlognull", "http-server-close"]

    errorfile 400 "/etc/haproxy/errors/400.http"
    errorfile 403 "/etc/haproxy/errors/403.http"
    errorfile 500 "/etc/haproxy/errors/500.http"
}
```

### Frontend Section

```haproxy-dsl
frontend http_front {
    // Bind directives
    bind *:80
    bind *:443 ssl {
        cert: "/etc/haproxy/certs/site.pem"
        alpn: ["h2", "http/1.1"]
    }

    mode: http
    maxconn: 2000
    timeout_client: 30s

    // ACLs - Block syntax
    acl {
        is_api path_beg "/api/"
        is_static path_beg "/static/" "/images/"
        is_websocket hdr(Upgrade) -i WebSocket
    }

    // ACLs - Individual syntax
    acl is_secure ssl_fc

    // HTTP request rules
    http-request {
        deny if !is_secure
        set-header "X-Forwarded-Proto" "https"
        add-header "X-Request-ID" "%[uuid()]"
        lua.custom_auth if is_api
    }

    // HTTP response rules
    http-response {
        set-header "X-Frame-Options" "DENY"
        set-header "X-Content-Type-Options" "nosniff"
    }

    // Routing
    use_backend {
        backend: api_backend if is_api
        backend: static_backend if is_static
    }

    default_backend: web_backend

    option: ["forwardfor", "http-keep-alive"]
}
```

### Backend Section

```haproxy-dsl
backend web_backend {
    mode: http
    balance: roundrobin
    retries: 3

    // Timeouts
    timeout_connect: 5s
    timeout_server: 50s
    timeout_check: 10s

    // Cookie persistence
    cookie: "SERVERID insert indirect nocache"

    // Health check
    health-check {
        method: "GET"
        uri: "/health"
        expect: status 200
        header "Host" "example.com"
    }

    // HTTP rules
    http-request {
        set-header "X-Backend" "web"
    }

    http-response {
        del-header "Server"
    }

    // Compression
    compression {
        algo: "gzip"
        type: ["text/html", "text/plain", "application/json"]
    }

    // Servers
    servers {
        server web1 {
            address: "10.0.1.1"
            port: 8080
            check: true
            inter: 3s
            rise: 2
            fall: 3
            weight: 100
            maxconn: 200
        }

        server web2 {
            address: "10.0.1.2"
            port: 8080
            check: true
            inter: 3s
            rise: 2
            fall: 3
            weight: 100
            backup: true  // Backup server
        }
    }

    option: ["httpchk", "forwardfor"]
}
```

### Server Template

For dynamic server generation:

```haproxy-dsl
backend api_backend {
    balance: leastconn

    server-template api[1..10] {
        fqdn: "api-{id}.example.com"
        port: 8080
        check: true
        inter: 5s
        rise: 2
        fall: 3
    }
}
```

**Generated:**
```
server-template api 10 api-{id}.example.com:8080 check inter 5s rise 2 fall 3
```

### SSL Configuration

```haproxy-dsl
frontend https_front {
    bind *:443 ssl {
        cert: "/etc/haproxy/certs/example.pem"
        alpn: ["h2", "http/1.1"]
        no-sslv3: true
        no-tlsv10: true
        no-tlsv11: true
    }

    // ... routing
}

backend secure_backend {
    servers {
        server backend1 {
            address: "10.0.1.1"
            port: 443
            ssl: true
            verify: "required"
            check: true
        }
    }
}
```

### Lua Integration

#### Inline Lua Scripts

```haproxy-dsl
global {
    lua {
        script rate_limiter {
            core.register_fetches("rate_limit", function(txn)
                local rate = txn.sc:get_gpc0(0)
                return rate > 100 and "blocked" or "allowed"
            end)
        }
    }
}
```

#### External Lua Files

```haproxy-dsl
global {
    lua {
        load "/etc/haproxy/lua/auth.lua"
        load "/etc/haproxy/lua/logging.lua"
    }
}
```

#### Lua Actions in HTTP Rules

```haproxy-dsl
frontend api {
    http-request {
        lua.authenticate if is_api
        lua.rate_limit if is_api
    }
}
```

#### Lua with Template Parameters

```haproxy-dsl
lua {
    script rate_limiter(max_rate: ${max_req_per_sec}) {
        core.register_fetches("rate_limit", function(txn)
            local rate = txn.sc:get_gpc0(0)
            return rate > ${max_rate} and "blocked" or "allowed"
        end)
    }
}
```

---

## Common Patterns

### Simple Load Balancer

```haproxy-dsl
config simple_lb {
    defaults {
        mode: http
        timeout: {
            connect: 5s
            client: 50s
            server: 50s
        }
        option: ["httplog"]
    }

    frontend web {
        bind *:80
        default_backend: servers
    }

    backend servers {
        balance: roundrobin
        servers {
            server web1 { address: "10.0.1.1", port: 8080, check: true }
            server web2 { address: "10.0.1.2", port: 8080, check: true }
            server web3 { address: "10.0.1.3", port: 8080, check: true }
        }
    }
}
```

### SSL Termination

```haproxy-dsl
config ssl_termination {
    global {
        ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
        ssl-default-bind-options: ["ssl-min-ver TLSv1.2", "no-tls-tickets"]
    }

    defaults {
        mode: http
        timeout: {
            connect: 5s
            client: 50s
            server: 50s
        }
    }

    frontend https {
        bind *:443 ssl {
            cert: "/etc/haproxy/certs/site.pem"
            alpn: ["h2", "http/1.1"]
        }

        http-request {
            set-header "X-Forwarded-Proto" "https"
            set-header "X-Forwarded-For" "%[src]"
        }

        default_backend: web_servers
    }

    backend web_servers {
        balance: roundrobin
        option: ["forwardfor"]
        servers {
            server web1 { address: "10.0.1.1", port: 80, check: true }
            server web2 { address: "10.0.1.2", port: 80, check: true }
        }
    }
}
```

### ACL-Based Routing

```haproxy-dsl
config acl_routing {
    frontend web {
        bind *:80

        acl {
            is_api path_beg "/api/"
            is_static path_beg "/static/" "/images/" "/css/" "/js/"
            is_admin path_beg "/admin/"
            has_auth hdr(Authorization) -m found
        }

        http-request {
            deny if is_admin !has_auth
        }

        use_backend {
            backend: api_backend if is_api
            backend: static_backend if is_static
            backend: admin_backend if is_admin
        }

        default_backend: web_backend
    }

    backend api_backend {
        balance: leastconn
        servers {
            server api1 { address: "10.0.1.1", port: 8080, check: true }
            server api2 { address: "10.0.1.2", port: 8080, check: true }
        }
    }

    backend static_backend {
        balance: roundrobin
        servers {
            server cdn1 { address: "10.0.2.1", port: 80, check: true }
            server cdn2 { address: "10.0.2.2", port: 80, check: true }
        }
    }

    backend admin_backend {
        servers {
            server admin { address: "10.0.3.1", port: 8080, check: true }
        }
    }

    backend web_backend {
        balance: roundrobin
        servers {
            server web1 { address: "10.0.4.1", port: 8080, check: true }
            server web2 { address: "10.0.4.2", port: 8080, check: true }
        }
    }
}
```

### Dynamic Server Generation

```haproxy-dsl
config dynamic_servers {
    let num_servers = env("NUM_SERVERS", "5")
    let base_ip = "10.0.1"
    let base_port = 8080

    template server_defaults {
        check: true
        inter: 3s
        rise: 2
        fall: 3
        maxconn: 200
    }

    frontend web {
        bind *:80
        default_backend: app_servers
    }

    backend app_servers {
        balance: roundrobin

        servers {
            for i in [1..${num_servers}] {
                server "app${i}" {
                    address: "${base_ip}.${i}"
                    port: base_port
                    @server_defaults
                }
            }
        }
    }
}
```

### Health Check Configuration

```haproxy-dsl
config health_checks {
    defaults {
        mode: http
        timeout: {
            connect: 5s
            client: 50s
            server: 50s
            check: 10s
        }
    }

    backend app {
        balance: roundrobin

        health-check {
            method: "GET"
            uri: "/health"
            expect: status 200
            header "Host" "example.com"
            header "User-Agent" "HAProxy-HealthCheck"
        }

        servers {
            server app1 {
                address: "10.0.1.1"
                port: 8080
                check: true
                inter: 5s  // Check every 5 seconds
                rise: 3    // 3 successful checks to be UP
                fall: 2    // 2 failed checks to be DOWN
            }
        }
    }
}
```

### Multi-Environment Configuration

```haproxy-dsl
config multi_env {
    let env = env("ENVIRONMENT", "development")
    let is_prod = env == "production"

    global {
        daemon: is_prod
        maxconn: is_prod ? 10000 : 100
    }

    defaults {
        mode: http
        retries: is_prod ? 3 : 1
        timeout: {
            connect: 5s
            client: is_prod ? 50s : 10s
            server: is_prod ? 50s : 10s
        }
    }

    frontend web {
        bind *:80
        default_backend: servers
    }

    if is_prod {
        backend servers {
            balance: leastconn
            servers {
                for i in [1..10] {
                    server "prod${i}" {
                        address: "10.0.1.${i}"
                        port: 8080
                        check: true
                    }
                }
            }
        }
    } else {
        backend servers {
            balance: roundrobin
            servers {
                server dev1 { address: "localhost", port: 8080 }
            }
        }
    }
}
```

---

## Advanced Features

### Compression

```haproxy-dsl
backend api {
    balance: roundrobin

    compression {
        algo: "gzip"
        type: [
            "text/html",
            "text/plain",
            "text/css",
            "text/javascript",
            "application/json",
            "application/javascript"
        ]
    }

    servers {
        server api1 { address: "10.0.1.1", port: 8080, check: true }
    }
}
```

### Cookie-Based Session Persistence

```haproxy-dsl
backend app {
    balance: roundrobin
    cookie: "SERVERID insert indirect nocache"

    servers {
        server app1 {
            address: "10.0.1.1"
            port: 8080
            check: true
            cookie: "app1"  // Cookie value for this server
        }
        server app2 {
            address: "10.0.1.2"
            port: 8080
            check: true
            cookie: "app2"
        }
    }
}
```

**Note**: Server cookie values are supported via the `options` dict in the current implementation.

### Backup Servers

```haproxy-dsl
backend app {
    balance: roundrobin

    servers {
        // Primary servers
        server app1 { address: "10.0.1.1", port: 8080, check: true }
        server app2 { address: "10.0.1.2", port: 8080, check: true }

        // Backup server (only used if all primaries are down)
        server backup1 {
            address: "10.0.2.1"
            port: 8080
            check: true
            backup: true
        }
    }
}
```

### Send PROXY Protocol

```haproxy-dsl
backend app {
    servers {
        server app1 {
            address: "10.0.1.1"
            port: 8080
            check: true
            send-proxy: true  // Send PROXY protocol v1
        }
    }
}
```

### Complex HTTP Rules

```haproxy-dsl
frontend api {
    bind *:80

    acl {
        is_post method POST
        is_api path_beg "/api/"
        rate_limited sc0_http_req_rate gt 100
        has_token hdr(Authorization) -m found
        is_internal src 10.0.0.0/8 192.168.0.0/16
    }

    http-request {
        // Deny if rate limited
        deny deny_status: 429 if rate_limited

        // Require auth for API
        deny deny_status: 401 if is_api !has_token

        // Add headers
        set-header "X-Forwarded-Proto" "http"
        add-header "X-Request-Start" "%[date()]"

        // Redirect POST to HTTPS
        redirect scheme: https code: 301 if is_post !{ ssl_fc }

        // Custom Lua processing
        lua.rate_limit if is_api
        lua.authenticate if is_api has_token
    }

    default_backend: api_backend
}
```

---

## Troubleshooting

### Validation Errors

**Undefined backend reference:**
```
Error: Frontend 'web' references undefined backend 'servers'
```

**Solution**: Ensure all referenced backends exist:
```haproxy-dsl
frontend web {
    default_backend: servers  // Must exist
}

backend servers {  // ✓ Defined
    balance: roundrobin
}
```

**Undefined variable:**
```
Error: Undefined variable: ${port}
```

**Solution**: Define variable before use:
```haproxy-dsl
let port = 8080  // ✓ Define first

server web1 {
    address: "10.0.1.1"
    port: port  // ✓ Use after definition
}
```

### Parse Errors

**Invalid syntax:**
```
Error: Syntax error at line 15, column 10
```

**Solution**: Check for:
- Missing colons: `mode: http` not `mode http`
- Missing commas in arrays: `["a", "b"]` not `["a" "b"]`
- Unmatched braces: `{ ... }`
- Invalid keywords

**Enable debug mode to see parse tree:**
```bash
haproxy-translate config.hap --debug
```

### Type Errors

**Invalid mode value:**
```
Error: Invalid mode 'httpx', expected 'http' or 'tcp'
```

**Solution**: Use valid enum values:
```haproxy-dsl
mode: http  // ✓ Valid
mode: tcp   // ✓ Valid
mode: httpx // ✗ Invalid
```

### Semantic Validation Errors

**Invalid health check:**
```
Error: Invalid health check expect status 999
```

**Solution**: Use valid HTTP status codes (100-599):
```haproxy-dsl
health-check {
    method: "GET"
    uri: "/health"
    expect: status 200  // ✓ Valid
}
```

### Common Mistakes

**❌ Wrong:**
```haproxy-dsl
// Missing config wrapper
frontend web {
    bind *:80
}
```

**✓ Correct:**
```haproxy-dsl
config my_config {
    frontend web {
        bind *:80
        default_backend: servers
    }
    backend servers {
        balance: roundrobin
    }
}
```

**❌ Wrong:**
```haproxy-dsl
// Reference before definition
frontend web {
    default_backend: servers
}

backend servers {  // Defined after use
    balance: roundrobin
}
```

**✓ Correct:**
```haproxy-dsl
// Order doesn't matter in same config block
config my_config {
    frontend web {
        default_backend: servers  // ✓ Can reference
    }

    backend servers {  // ✓ Defined in same config
        balance: roundrobin
    }
}
```

---

## Best Practices

### 1. Use Variables for Configuration Values

**❌ Avoid hardcoding:**
```haproxy-dsl
server web1 { address: "10.0.1.1", port: 8080 }
server web2 { address: "10.0.1.2", port: 8080 }
```

**✓ Use variables:**
```haproxy-dsl
let base_ip = env("BASE_IP", "10.0.1")
let app_port = env("APP_PORT", "8080")

server web1 { address: "${base_ip}.1", port: app_port }
server web2 { address: "${base_ip}.2", port: app_port }
```

### 2. Use Templates for Repeated Configuration

**❌ Repetitive:**
```haproxy-dsl
server web1 {
    address: "10.0.1.1"
    port: 8080
    check: true
    inter: 3s
    rise: 2
    fall: 3
}
server web2 {
    address: "10.0.1.2"
    port: 8080
    check: true
    inter: 3s
    rise: 2
    fall: 3
}
```

**✓ Use templates:**
```haproxy-dsl
template server_defaults {
    check: true
    inter: 3s
    rise: 2
    fall: 3
}

server web1 { address: "10.0.1.1", port: 8080, @server_defaults }
server web2 { address: "10.0.1.2", port: 8080, @server_defaults }
```

### 3. Use Loops for Scalability

**❌ Manual repetition:**
```haproxy-dsl
server web1 { address: "10.0.1.1", port: 8080 }
server web2 { address: "10.0.1.2", port: 8080 }
server web3 { address: "10.0.1.3", port: 8080 }
// ... what if we need 50 servers?
```

**✓ Use loops:**
```haproxy-dsl
servers {
    for i in [1..50] {
        server "web${i}" { address: "10.0.1.${i}", port: 8080 }
    }
}
```

### 4. Validate Before Deploying

Always validate configuration before deploying:

```bash
# Validate syntax and semantics
haproxy-translate config.hap --validate

# If valid, generate
haproxy-translate config.hap -o haproxy.cfg

# Validate with HAProxy
haproxy -c -f haproxy.cfg
```

### 5. Use Environment Variables for Secrets

**❌ Don't hardcode secrets:**
```haproxy-dsl
stats {
    enable: true
    auth: "admin:password123"  // ✗ Bad!
}
```

**✓ Use environment variables:**
```haproxy-dsl
stats {
    enable: true
    auth: env("HAPROXY_STATS_AUTH")  // ✓ Good!
}
```

### 6. Organize Complex Configurations

**Use meaningful section names:**
```haproxy-dsl
config production_lb {
    // Global configuration
    global { ... }

    // Defaults
    defaults { ... }

    // Public-facing frontend
    frontend public_https { ... }

    // API backend
    backend api_servers { ... }

    // Web application backend
    backend web_servers { ... }

    // Static content backend
    backend cdn_servers { ... }
}
```

### 7. Comment Your Configuration

```haproxy-dsl
config my_config {
    // Global HAProxy settings
    global {
        daemon: true
        maxconn: 4096  // Allow up to 4096 concurrent connections
    }

    // API backend with leastconn for long-running requests
    backend api {
        balance: leastconn  // Best for varying request times

        servers {
            // Production API servers
            for i in [1..5] {
                server "api${i}" {
                    address: "10.0.1.${i}"
                    port: 8080
                    check: true  // Enable health checks
                }
            }
        }
    }
}
```

### 8. Use Semantic Names

**❌ Generic names:**
```haproxy-dsl
frontend fe1 { ... }
backend be1 { ... }
server s1 { ... }
```

**✓ Descriptive names:**
```haproxy-dsl
frontend public_https { ... }
backend api_servers { ... }
server api_primary_1 { ... }
```

### 9. Test Health Checks

Always configure health checks for production:

```haproxy-dsl
backend app {
    balance: roundrobin

    health-check {
        method: "GET"
        uri: "/health"
        expect: status 200
    }

    servers {
        server app1 {
            address: "10.0.1.1"
            port: 8080
            check: true  // ✓ Always enable for production
            inter: 5s    // ✓ Check every 5 seconds
            rise: 2      // ✓ 2 successful checks to mark UP
            fall: 3      // ✓ 3 failed checks to mark DOWN
        }
    }
}
```

### 10. Use Watch Mode for Development

During development, use watch mode for instant feedback:

```bash
haproxy-translate config.hap -o haproxy.cfg --watch --verbose
```

Changes to `config.hap` will automatically regenerate `haproxy.cfg`.

---

## Next Steps

- Review [FEATURES.md](FEATURES.md) for feature parity details
- Check [examples/](examples/) for more complex configurations
- Read [PROJECT_PLAN.md](PROJECT_PLAN.md) for roadmap
- Contribute at [GitHub](https://github.com/haproxy/config-translator)

---

**Questions or Issues?**
- Report bugs: https://github.com/haproxy/config-translator/issues
- Discussions: https://github.com/haproxy/config-translator/discussions
- HAProxy docs: https://docs.haproxy.org/
