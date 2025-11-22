# HAProxy Configuration Translator

A modern, powerful DSL for HAProxy configuration with **templates**, **loops**, **variables**, and **environment injection** - reducing configuration complexity by up to 60%.

## Project Status

| Metric                | Value                    |
| --------------------- | ------------------------ |
| **HAProxy Version**   | 3.3                      |
| **Tests**             | 1,430 passing            |
| **Global Directives** | 95.9% coverage (158/165) |
| **Proxy Keywords**    | 100% coverage (78/78)    |
| **Production Ready**  | Yes                      |

## Why Use the DSL?

### Before: Native HAProxy (repetitive, error-prone)

```haproxy
backend api_servers
    balance roundrobin
    server api01 10.0.1.1:8080 check inter 3s fall 3 rise 2 weight 100
    server api02 10.0.1.2:8080 check inter 3s fall 3 rise 2 weight 100
    server api03 10.0.1.3:8080 check inter 3s fall 3 rise 2 weight 100
    server api04 10.0.1.4:8080 check inter 3s fall 3 rise 2 weight 100
    server api05 10.0.1.5:8080 check inter 3s fall 3 rise 2 weight 100
    # ... 5 more lines of copy-paste
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

## Key Features

### Templates - Define Once, Use Everywhere

```javascript
template production_server {
  check: true
  inter: 3s
  fall: 3
  rise: 2
  maxconn: 500
}

server web1 { address: "10.0.1.1", port: 8080, @production_server }
```

### Loops - Generate Servers Dynamically

```javascript
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

### Environment Variables - CI/CD Ready

```javascript
// With safe defaults
let server_count = env("SERVER_COUNT", 3);
let api_host = env("API_HOST", "localhost");

// Deploy different environments from same config
// PRODUCTION:  SERVER_COUNT=10 API_HOST=api.prod.internal
// STAGING:     SERVER_COUNT=3  API_HOST=api.staging.internal
// DEVELOPMENT: (uses defaults)
```

## Quick Start

### Installation

```bash
# Install uv (if not already installed)
pip install uv -U

# Clone and install
git clone https://github.com/mattsta/haproxy-translate.git
cd haproxy-translate
uv sync
```

### Basic Usage

```bash
# Translate DSL config to HAProxy format
uv run haconf config.hap -o haproxy.cfg

# Validate configuration
uv run haconf config.hap --validate

# Run security validation
uv run haconf config.hap --security-check

# With environment variables
SERVER_COUNT=10 API_HOST=api.prod.internal \
  uv run haconf config.hap -o haproxy.cfg
```

### Example Configuration

```javascript
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
    bind *:443 ssl { cert: "/etc/ssl/cert.pem", alpn: ["h2", "http/1.1"] }
    default_backend: servers
  }

  backend servers {
    balance: roundrobin
    servers {
      for i in [1..3] {
        server "web${i}" {
          address: "192.168.1.${i}"
          port: 8080
          check: true
        }
      }
    }
  }
}
```

## Security Validation

Run security checks on your configuration to detect common issues:

```bash
uv run haconf config.hap --security-check
```

The security validator checks for:

- **Hardcoded credentials** - Passwords, API keys, tokens in configuration
- **Unsafe user settings** - Running as root, missing chroot
- **SSL/TLS issues** - Weak ciphers, missing certificates, insecure options
- **Authentication gaps** - Stats pages without auth, admin access exposed
- **Resource limits** - Missing timeouts, extreme connection limits

Example output:

```
Security Check Report
  critical: 1 | high: 2 | medium: 3 | info: 1

┌──────────┬─────────────────┬──────────────────────────┬────────────────────────┐
│ Level    │ Location        │ Issue                    │ Recommendation         │
├──────────┼─────────────────┼──────────────────────────┼────────────────────────┤
│ high     │ global          │ HAProxy running as root  │ Run as non-privileged  │
│ high     │ frontend.stats  │ Stats without auth       │ Add auth credentials   │
└──────────┴─────────────────┴──────────────────────────┴────────────────────────┘
```

## Documentation

| Guide                                            | Description                                       |
| ------------------------------------------------ | ------------------------------------------------- |
| **[Quick Start](docs/QUICK_START.md)**           | Get running in 5 minutes                          |
| **[Patterns Guide](docs/PATTERNS.md)**           | Real-world examples with before/after comparisons |
| **[Syntax Reference](docs/SYNTAX_REFERENCE.md)** | Complete DSL syntax                               |
| **[Migration Guide](docs/MIGRATION_GUIDE.md)**   | Convert existing HAProxy configs                  |
| **[Architecture](docs/ARCHITECTURE.md)**         | How the translator works internally               |

## Real-World Patterns

The DSL excels at common HAProxy patterns:

| Pattern           | Native Lines | DSL Lines | Reduction |
| ----------------- | ------------ | --------- | --------- |
| 10-Server Pool    | 30           | 18        | 40%       |
| Multi-Environment | 3 files      | 1 file    | 67%       |
| 5 Microservices   | 75           | 55        | 27%       |
| Blue-Green Deploy | 50           | 35        | 30%       |

See **[PATTERNS.md](docs/PATTERNS.md)** for detailed examples.

## Feature Coverage

### Global Directives (95.9% - 158/165)

All production-critical directives including:

- Process management (daemon, user, chroot, pidfile)
- Connection limits (maxconn, maxsslconn, maxconnrate)
- SSL/TLS defaults (ciphers, options, certificates)
- Performance tuning (tune.\*, buffers, threading)
- QUIC/HTTP3 configuration

### Proxy Keywords (100% - 78/78)

Complete coverage of frontend/backend/listen/defaults:

- Load balancing algorithms
- Health checks (HTTP, TCP, agent)
- Server options (55+ parameters)
- ACLs and routing rules
- HTTP/TCP request/response rules
- Stick tables and session persistence

## Development

```bash
# Run tests
uv run pytest -n 20

# Type checking
uv run mypy src --ignore-missing-imports

# Linting
uv run ruff check .

# All checks
uv run pytest -n 20 && uv run mypy src --ignore-missing-imports
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HAProxy Config Translator                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌────────────┐   ┌───────────────┐  │
│  │  Source  │──▶│    Parser    │──▶│ Transformer│──▶│   Code Gen    │  │
│  │  (.hap)  │   │  (Lark AST)  │   │    (IR)    │   │ (HAProxy cfg) │  │
│  └──────────┘   └──────────────┘   └────────────┘   └───────────────┘  │
│                                                                          │
│  Transformation Pipeline:                                                │
│  1. Parse DSL → AST                                                      │
│  2. Transform → IR                                                       │
│  3. Unroll Loops → Expand for loops                                      │
│  4. Expand Templates → Apply @template spreads                          │
│  5. Resolve Variables → Multi-pass ${var} resolution                    │
│  6. Generate → Native HAProxy config                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Areas of interest:

- Additional example configurations
- Performance optimizations
- Documentation improvements
- New transformer features
