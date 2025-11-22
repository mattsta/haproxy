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
config my_loadbalancer {
  global {
    daemon: true
    maxconn: 4096
    log "/dev/log" local0 info
  }

  defaults {
    mode: http
    retries: 3
    timeout: {
      connect: 5s
      client: 30s
      server: 30s
    }
    option: ["httplog", "dontlognull"]
  }

  frontend web {
    bind *:80
    default_backend: servers
  }

  backend servers {
    balance: roundrobin

    servers {
      server web1 {
        address: "192.168.1.10"
        port: 8080
        check: true
      }
      server web2 {
        address: "192.168.1.11"
        port: 8080
        check: true
      }
      server web3 {
        address: "192.168.1.12"
        port: 8080
        check: true
      }
    }
  }
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
    log /dev/log local0 info

defaults
    mode http
    retries 3
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

## DSL Syntax Essentials

### Config Wrapper
All DSL files must be wrapped in a `config name { }` block:

```javascript
config my_config {
  // All sections go inside here
  global { ... }
  defaults { ... }
  frontend name { ... }
  backend name { ... }
}
```

### Mode Values
Mode values are identifiers, not strings:

```javascript
// Correct
mode: http
mode: tcp

// Incorrect
mode: "http"  // Don't quote mode values
```

### Bind Directive
Bind addresses are specified without quotes:

```javascript
// Correct
bind *:80
bind 0.0.0.0:443

// With SSL
bind *:443 ssl { cert: "/path/to/cert.pem" }
```

### Server Definitions
Servers are defined inside a `servers { }` block:

```javascript
backend api {
  servers {
    server api1 {
      address: "10.0.1.1"
      port: 8080
      check: true
      weight: 10
    }
  }
}
```

## Why Use the DSL?

The DSL dramatically reduces configuration complexity. Here's a real example:

### Before: Native HAProxy (12 lines of repetition)
```haproxy
backend api_servers
    balance roundrobin
    server api01 10.0.1.1:8080 check inter 3s fall 3 rise 2 weight 100
    server api02 10.0.1.2:8080 check inter 3s fall 3 rise 2 weight 100
    server api03 10.0.1.3:8080 check inter 3s fall 3 rise 2 weight 100
    server api04 10.0.1.4:8080 check inter 3s fall 3 rise 2 weight 100
    server api05 10.0.1.5:8080 check inter 3s fall 3 rise 2 weight 100
    server api06 10.0.1.6:8080 check inter 3s fall 3 rise 2 weight 100
    server api07 10.0.1.7:8080 check inter 3s fall 3 rise 2 weight 100
    server api08 10.0.1.8:8080 check inter 3s fall 3 rise 2 weight 100
    server api09 10.0.1.9:8080 check inter 3s fall 3 rise 2 weight 100
    server api10 10.0.1.10:8080 check inter 3s fall 3 rise 2 weight 100
```

### After: DSL with Templates + Loops (60% less code)
```javascript
config api_cluster {
  template standard_server {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    weight: 100
  }

  backend api_servers {
    balance: roundrobin
    servers {
      for i in [1..10] {
        server "api${i}" {
          address: "10.0.1.${i}"
          port: 8080
          @standard_server
        }
      }
    }
  }
}
```

**Change the template once, all 10 servers update. No copy-paste errors possible.**

---

### Key Features

#### 1. **Templates** - Define Once, Use Everywhere
```javascript
template production_server {
  check: true
  inter: 3s
  fall: 3
  rise: 2
  maxconn: 500
}

// Apply with @template_name
server web1 { address: "10.0.1.1", port: 8080, @production_server }
```

#### 2. **Loops** - Generate Servers Dynamically
```javascript
// Range syntax: [start..end] inclusive
for i in [1..5] {
  server "node${i}" {
    address: "10.0.1.${i}"
    port: 8080
  }
}

// With arithmetic: ${10 + i} = 11, 12, 13...
for i in [1..3] {
  server "node${i}" { address: "10.0.1.${10 + i}", port: 8080 }
}
```

#### 3. **Variables** - DRY Configuration
```javascript
let app_port = 8080
let check_interval = 3s
let api_host = "api.internal"

server api1 {
  address: "${api_host}"
  port: ${app_port}
  inter: ${check_interval}
}
```

#### 4. **Environment Variables** - CI/CD Ready
```javascript
// With defaults for safety
let server_count = env("SERVER_COUNT", 3)
let api_host = env("API_HOST", "localhost")
let timeout = env("TIMEOUT_SECONDS", 30s)

// Deploy different environments from same config
// PRODUCTION:  SERVER_COUNT=10 API_HOST=api.prod.internal
// STAGING:     SERVER_COUNT=3  API_HOST=api.staging.internal
// DEVELOPMENT: (uses defaults)
```

#### 5. **Multi-Pass Variable Resolution**
```javascript
let port = 8080
let host = "10.0.1.1"
let endpoint = "${host}:${port}"     // Resolves to "10.0.1.1:8080"
let full_url = "${endpoint}/api"     // Resolves to "10.0.1.1:8080/api"
```

---

### Real-World Patterns

See **[PATTERNS.md](PATTERNS.md)** for comprehensive examples:
- Multi-environment deployments (dev/staging/prod from one config)
- Microservices routing with templates
- Blue-green deployments with weight variables
- Standardized health checks across teams

## Next Steps

- **[Syntax Reference](SYNTAX_REFERENCE.md)** - Complete DSL syntax documentation
- **[Migration Guide](MIGRATION_GUIDE.md)** - Convert existing HAProxy configs
- **[Architecture Guide](ARCHITECTURE.md)** - How the translator works internally

## Common Commands

```bash
# Translate a config file
uv run haproxy-translate config.hap -o output.cfg

# Validate only (no output)
uv run haproxy-translate config.hap --validate

# Show verbose output
uv run haproxy-translate config.hap -v
```

## Getting Help

```bash
# Show help
uv run haproxy-translate --help

# Show version
uv run haproxy-translate --version
```
