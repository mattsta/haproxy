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

### 1. **Type Safety**
Catch errors at translation time, not when HAProxy fails to start.

### 2. **Modern Syntax**
Clean, readable configuration with structured blocks.

### 3. **Variables & Templating**
DRY configuration with variables:

```javascript
config with_vars {
  let app_port = 8080
  let check_interval = 3s

  backend api {
    servers {
      server api1 {
        address: "10.0.1.1"
        port: ${app_port}
        check: true
        inter: ${check_interval}
      }
    }
  }
}
```

### 4. **Loops for Dynamic Configs**
Generate servers programmatically:

```javascript
config dynamic {
  backend nodes {
    servers {
      for i in [1, 2, 3, 4, 5] {
        server "node${i}" {
          address: "10.0.1.${i}"
          port: 8080
          check: true
        }
      }
    }
  }
}
```

### 5. **Templates**
Reuse common configurations:

```javascript
config templated {
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
        @server_defaults
      }
    }
  }
}
```

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
