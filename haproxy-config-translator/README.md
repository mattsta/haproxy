# HAProxy Configuration Translator

A modern, powerful configuration translation system for HAProxy with pluggable parsers, supporting multiple input formats including a custom DSL with first-class Lua support, templates, variables, and composition.

## Features

- 🎯 **Powerful DSL**: Modern syntax with variables, templates, loops, conditionals, and functions
- 🔌 **Pluggable Architecture**: Easy to add new input formats (YAML, HCL, TOML, etc.)
- 🐛 **First-Class Lua**: Inline Lua scripts with parameter interpolation
- ✅ **Comprehensive Validation**: Semantic validation, type checking, reference resolution
- 🎨 **Clean Code Generation**: Generates clean, idiomatic HAProxy configuration
- 🔄 **Zero HAProxy Changes**: Pure translation layer, no HAProxy modifications needed
- 📝 **Type Safe**: Full type annotations and validation throughout
- 🧪 **Well Tested**: Comprehensive test suite

## Quick Start

### Installation

```bash
pip install haproxy-config-translator
```

### Basic Usage

```bash
# Translate DSL config to HAProxy format
haproxy-translate config.hap -o /etc/haproxy/haproxy.cfg

# Validate configuration
haproxy-translate config.hap --validate

# Watch mode (auto-regenerate on changes)
haproxy-translate config.hap -o haproxy.cfg --watch
```

### Example DSL Configuration

```haproxy-dsl
config my_loadbalancer {
  version: "2.0"

  // Variables
  let backend_port = env("BACKEND_PORT") ?? 8080
  let ssl_cert = "/etc/ssl/haproxy.pem"

  // Template for reusable server config
  template server_defaults {
    check: true
    inter: 3s
    rise: 2
    fall: 3
    maxconn: 100
  }

  global {
    daemon: true
    maxconn: 4096
    log "/dev/log" local0 info

    // Inline Lua with first-class support
    lua {
      script custom_auth {
        core.register_action("custom_auth", {"http-req"}, function(txn)
          local token = txn.http:req_get_headers()["Authorization"][0]
          if token and token:match("^Bearer%s+%w+") then
            return ACT_ALLOW
          end
          return ACT_DENY
        end)
      }
    }
  }

  defaults {
    mode: http
    retries: 3
    timeout: {
      connect: 5s
      client: 50s
      server: 50s
    }
    log: global
    option: [httplog, dontlognull]
  }

  acl is_api {
    path_beg "/api/"
  }

  frontend http_front {
    bind *:80
    bind *:443 ssl {
      cert: ssl_cert
      alpn: [h2, http/1.1]
    }

    use acl: [is_api]

    http-request {
      lua.custom_auth if is_api
      set-header "X-Forwarded-Proto" "https"
    }

    route {
      to api_backend if is_api
      default: web_backend
    }
  }

  backend web_backend {
    balance: roundrobin
    option: [httpchk, forwardfor]

    health-check {
      method: GET
      uri: "/health"
      expect: status 200
    }

    // Generate servers with loop
    servers {
      for i in 1..3 {
        server "web${i}" {
          address: "192.168.1.${10 + i}"
          port: backend_port
          @server_defaults  // Spread template
          weight: 100
        }
      }
    }
  }

  backend api_backend {
    balance: leastconn

    server-template api[1..5] {
      fqdn: "api-{id}.example.com"
      port: 8080
      @server_defaults
    }
  }
}
```

**Generated HAProxy Config:**

```
global
    daemon
    maxconn 4096
    log /dev/log local0 info
    lua-load /etc/haproxy/lua/custom_auth.lua

defaults
    mode http
    log global
    retries 3
    timeout connect 5s
    timeout client 50s
    timeout server 50s
    option httplog
    option dontlognull

frontend http_front
    bind *:80
    bind *:443 ssl crt /etc/ssl/haproxy.pem alpn h2,http/1.1
    mode http
    acl is_api path_beg /api/
    http-request lua.custom_auth if is_api
    http-request set-header X-Forwarded-Proto https
    use_backend api_backend if is_api
    default_backend web_backend

backend web_backend
    mode http
    balance roundrobin
    option httpchk
    option forwardfor
    http-check send meth GET uri /health
    http-check expect status 200
    server web1 192.168.1.11:8080 check inter 3s rise 2 fall 3 maxconn 100 weight 100
    server web2 192.168.1.12:8080 check inter 3s rise 2 fall 3 maxconn 100 weight 100
    server web3 192.168.1.13:8080 check inter 3s rise 2 fall 3 maxconn 100 weight 100

backend api_backend
    mode http
    balance leastconn
    server-template api 5 api-{id}.example.com:8080 check inter 3s rise 2 fall 3 maxconn 100
```

## Architecture

The translator uses a multi-layer architecture:

```
Input (DSL/YAML/HCL)
    ↓
Parser Layer (Pluggable)
    ↓
Intermediate Representation (IR)
    ↓
Transformation Layer (Templates, Variables, Loops)
    ↓
Validation Layer (Semantic, Type Checking)
    ↓
Lua Extraction Layer
    ↓
Code Generation Layer
    ↓
HAProxy Native Config
```

See [ARCHITECTURE.md](../HAPROXY_CONFIG_TRANSLATOR_ARCHITECTURE.md) for detailed design.

## DSL Features

### Variables

```haproxy-dsl
let port = 8080
let host = env("BACKEND_HOST") ?? "localhost"
let servers = ["web1", "web2", "web3"]
```

### Templates

```haproxy-dsl
template server_defaults {
  check: true
  inter: 3s
  rise: 2
  fall: 3
}

server myserver {
  address: "10.0.1.5"
  port: 8080
  @server_defaults  // Spread template
}
```

### Loops

```haproxy-dsl
servers {
  for i in 1..10 {
    server "web${i}" {
      address: "10.0.1.${i}"
      port: 8080
    }
  }
}
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

### Inline Lua

```haproxy-dsl
lua {
  script rate_limiter(max_rate: ${max_rate}) {
    core.register_fetches("rate_limit", function(txn)
      local rate = txn.sc:get_gpc0(0)
      return rate > ${max_rate} and "blocked" or "allowed"
    end)
  }
}
```

## CLI Reference

```bash
haproxy-translate [OPTIONS] CONFIG_FILE

Options:
  -o, --output PATH          Output file path (default: stdout)
  -f, --format FORMAT        Input format (dsl, yaml, hcl, auto)
  --validate                 Validate only, don't generate
  --debug                    Show debug information
  --watch                    Watch for changes and regenerate
  --lua-dir PATH             Output directory for Lua scripts
  --list-formats             List available input formats
  -v, --verbose              Verbose output
  --version                  Show version
  --help                     Show help message
```

## Development

### Setup

```bash
git clone https://github.com/haproxy/config-translator
cd config-translator
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
black src tests
ruff check src tests
mypy src
```

## Adding New Input Formats

Create a parser class implementing `ConfigParser`:

```python
from haproxy_translator.parsers.base import ConfigParser, ParserRegistry
from haproxy_translator.ir import ConfigIR

class MyFormatParser(ConfigParser):
    @property
    def format_name(self) -> str:
        return "myformat"

    @property
    def file_extensions(self) -> list[str]:
        return [".myformat"]

    def parse(self, source: str, filepath: Path = None) -> ConfigIR:
        # Parse source and return IR
        ...

# Register parser
ParserRegistry.register(MyFormatParser)
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.
