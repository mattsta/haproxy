# HAProxy Config Translator - Quick Start Guide

Get up and running with the HAProxy Config Translator in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/haproxy-config-translator.git
cd haproxy-config-translator

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Your First Configuration

Create a file called `my-config.hap`:

```javascript
// my-config.hap - A simple load balancer
global {
    daemon: true
    maxconn: 4096
    log: "127.0.0.1 local0"
}

defaults {
    mode: "http"
    timeouts: {
        connect: "5s"
        client: "30s"
        server: "30s"
    }
    options: ["httplog", "dontlognull"]
}

frontend web {
    bind: "*:80"
    default_backend: "servers"
}

backend servers {
    balance: "roundrobin"
    servers: [
        { name: "web1", address: "192.168.1.10", port: 8080, check: true },
        { name: "web2", address: "192.168.1.11", port: 8080, check: true },
        { name: "web3", address: "192.168.1.12", port: 8080, check: true }
    ]
}
```

## Generate HAProxy Configuration

```bash
# Translate to native HAProxy config
uv run haproxy-translate my-config.hap -o haproxy.cfg

# Or output to stdout
uv run haproxy-translate my-config.hap

# Validate without generating
uv run haproxy-translate my-config.hap --validate
```

## Output

The translator generates standard HAProxy configuration:

```haproxy
global
    daemon
    maxconn 4096
    log 127.0.0.1 local0

defaults
    mode http
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    option httplog
    option dontlognull

frontend web
    bind *:80
    default_backend servers

backend servers
    balance roundrobin
    server web1 192.168.1.10:8080 check
    server web2 192.168.1.11:8080 check
    server web3 192.168.1.12:8080 check
```

## Why Use the DSL?

### 1. **Type Safety**
Catch errors at translation time, not when HAProxy fails to start:

```javascript
// ❌ HAProxy: Typos silently ignored
// option htplog  <-- typo not caught until runtime

// ✅ DSL: Structured syntax prevents common errors
options: ["httplog"]
```

### 2. **Modern Syntax**
Clean, readable configuration:

```javascript
// ❌ HAProxy: Repetitive, positional arguments
server web1 192.168.1.10:8080 check weight 10 maxconn 100
server web2 192.168.1.11:8080 check weight 10 maxconn 100
server web3 192.168.1.12:8080 check weight 10 maxconn 100

// ✅ DSL: Structured, explicit properties
servers: [
    { name: "web1", address: "192.168.1.10", port: 8080,
      check: true, weight: 10, maxconn: 100 },
    { name: "web2", address: "192.168.1.11", port: 8080,
      check: true, weight: 10, maxconn: 100 },
    { name: "web3", address: "192.168.1.12", port: 8080,
      check: true, weight: 10, maxconn: 100 }
]
```

### 3. **Variables & Templating**
DRY configuration with variables:

```javascript
variables {
    app_port = 8080
    check_interval = "3s"
    server_weight = 10
}

backend api {
    servers: [
        { name: "api1", address: "10.0.1.1", port: ${app_port},
          check: true, inter: ${check_interval}, weight: ${server_weight} },
        { name: "api2", address: "10.0.1.2", port: ${app_port},
          check: true, inter: ${check_interval}, weight: ${server_weight} }
    ]
}
```

### 4. **Loops for Dynamic Configs**
Generate servers programmatically:

```javascript
backend dynamic {
    for i in [1, 2, 3, 4, 5] {
        server "node${i}" "10.0.1.${i}":8080 check
    }
}
```

### 5. **Environment Variables**
Inject runtime configuration:

```javascript
global {
    // Uses $HAPROXY_MAXCONN or defaults to 4096
    maxconn: ${env.HAPROXY_MAXCONN:-4096}
}

backend api {
    servers: [
        { name: "api", address: "${env.API_HOST}", port: ${env.API_PORT:-8080} }
    ]
}
```

## Next Steps

- **[Syntax Reference](SYNTAX_REFERENCE.md)** - Complete DSL syntax documentation
- **[Migration Guide](MIGRATION_GUIDE.md)** - Convert existing HAProxy configs
- **[Architecture Guide](ARCHITECTURE.md)** - How the translator works internally
- **[Examples](examples/)** - Real-world configuration examples

## Common Commands

```bash
# Translate a config file
uv run haproxy-translate config.hap -o output.cfg

# Validate only (no output)
uv run haproxy-translate config.hap --validate

# Show verbose output
uv run haproxy-translate config.hap -v

# Multiple input files
uv run haproxy-translate main.hap includes/*.hap -o output.cfg

# Watch mode (re-translate on changes)
uv run haproxy-translate config.hap -o output.cfg --watch
```

## Getting Help

```bash
# Show help
uv run haproxy-translate --help

# Show version
uv run haproxy-translate --version
```
