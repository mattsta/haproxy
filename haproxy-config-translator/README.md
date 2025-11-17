# HAProxy Configuration Translator

A modern, powerful configuration translation system for HAProxy with pluggable parsers, supporting multiple input formats including a custom DSL with first-class Lua support, templates, variables, and composition.

## Project Status

**Version**: 0.3.0 (Phase 3-4)
**Test Coverage**: 86% (186 tests passing)
**HAProxy Compatibility**: 3.0+ (85% feature parity)
**Production Ready**: ✅ Core features stable

See [FEATURES.md](FEATURES.md) for detailed feature parity analysis.

## Features

### Core Capabilities

- 🎯 **Powerful DSL**: Modern syntax with variables, templates, loops, conditionals, and functions
- 🔌 **Pluggable Architecture**: Easy to add new input formats (YAML, HCL, TOML, etc.)
- 🐛 **First-Class Lua**: Inline Lua scripts with parameter interpolation
- ✅ **Comprehensive Validation**: Semantic validation, type checking, reference resolution
- 🎨 **Clean Code Generation**: Generates clean, idiomatic HAProxy configuration
- 🔄 **Zero HAProxy Changes**: Pure translation layer, no HAProxy modifications needed
- 📝 **Type Safe**: Full type annotations and validation throughout
- 🧪 **Well Tested**: Comprehensive test suite with 86% coverage

### Transformation Pipeline

The translator features an **integrated 6-step transformation pipeline**:

1. **Parse** - Source → AST (Lark parser with Earley algorithm)
2. **Transform** - AST → Intermediate Representation (IR)
3. **Expand Templates** - Apply reusable configuration templates
4. **Resolve Variables** - Multi-pass variable interpolation
5. **Unroll Loops** - Generate repeated configurations
6. **Validate** - Semantic validation and reference checking

All steps are automatically executed in a single `parse()` call.

## Quick Start

### Installation

**Using uv (recommended):**
```bash
# From source
git clone https://github.com/haproxy/config-translator
cd config-translator/haproxy-config-translator
uv pip install -e .
```

**Using pip:**
```bash
pip install haproxy-config-translator
```

**Development installation:**
```bash
uv pip install -e ".[dev]"
```

### Basic Usage

```bash
# Translate DSL config to HAProxy format
haproxy-translate config.hap -o /etc/haproxy/haproxy.cfg

# Validate configuration
haproxy-translate config.hap --validate

# Watch mode (auto-regenerate on changes)
haproxy-translate config.hap -o haproxy.cfg --watch

# Debug mode (show IR and transformation steps)
haproxy-translate config.hap --debug

# Verbose output
haproxy-translate config.hap -o haproxy.cfg --verbose

# List supported formats
haproxy-translate config.hap --list-formats
```

See [USAGE.md](USAGE.md) for comprehensive usage examples and patterns.

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

## Supported HAProxy Features

The translator supports **~85% of common HAProxy use cases**, including:

### ✅ Fully Supported

- **Load Balancing**: roundrobin, leastconn, source, uri, url_param, random
- **Health Checks**: HTTP, TCP, with custom methods/URIs/headers
- **SSL/TLS**: Certificate configuration, ALPN, ciphers, bind options
- **ACLs**: All criteria types, flags, values, conditions
- **HTTP Processing**: Full request/response rule support
- **Session Persistence**: Cookie-based persistence
- **Compression**: Algorithm and type configuration
- **Lua Integration**: Inline scripts, external files, action calls
- **Server Options**: check, inter, rise, fall, weight, maxconn, ssl, backup
- **Timeouts**: connect, client, server, check, queue
- **Logging**: Syslog targets with facility and level

### ⚠️ Partially Supported

- **Listen Section**: Defined in IR, grammar support pending
- **Advanced SSL**: Basic support complete, SNI/ALPN on servers pending
- **Balance Algorithms**: Core algorithms supported, specialized variants pending

### ❌ Not Yet Supported

- HTTP/2 and HTTP/3 configuration
- Stick tables for advanced session persistence
- TCP-level request/response rules
- Custom log formats
- DNS resolvers
- Specialized health checks (MySQL, Redis, etc.)
- Filters and SPOE

See [FEATURES.md](FEATURES.md) for complete feature parity analysis.

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/haproxy/config-translator
cd config-translator/haproxy-config-translator

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=haproxy_translator --cov-report=html --cov-report=term

# Specific test file
pytest tests/test_parser/test_grammar.py -v

# Watch mode (requires pytest-watch)
ptw
```

**Current Status**: 186 tests passing, 86% coverage

### Code Quality

```bash
# Format code
ruff format src tests

# Lint
ruff check src tests

# Type checking
mypy src

# All checks (run before committing)
ruff check src tests && mypy src && pytest
```

### Project Structure

```
haproxy-config-translator/
├── src/haproxy_translator/
│   ├── ir/              # Intermediate Representation
│   │   ├── nodes.py     # IR node definitions
│   │   └── __init__.py
│   ├── grammars/        # Lark grammar files
│   │   └── haproxy_dsl.lark
│   ├── parsers/         # Input format parsers
│   │   ├── base.py      # Parser base class & registry
│   │   └── dsl_parser.py
│   ├── transformers/    # IR transformation passes
│   │   ├── dsl_transformer.py
│   │   ├── template_expander.py
│   │   ├── variable_resolver.py
│   │   └── loop_unroller.py
│   ├── validators/      # Validation layer
│   │   └── semantic.py
│   ├── codegen/         # Code generators
│   │   └── haproxy.py
│   ├── lua/             # Lua script management
│   │   └── manager.py
│   ├── cli/             # Command-line interface
│   │   └── main.py
│   └── utils/           # Utilities
│       └── errors.py
├── tests/               # Test suite (86% coverage)
│   ├── test_parser/
│   ├── test_transformers/
│   ├── test_validators/
│   ├── test_codegen/
│   ├── test_cli/
│   └── test_lua/
├── docs/                # Documentation
│   └── examples/        # Example configurations
├── FEATURES.md          # Feature parity analysis
├── USAGE.md             # Usage guide
├── PROJECT_PLAN.md      # Development roadmap
├── pyproject.toml       # Project configuration
└── README.md            # This file
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

## Roadmap

### Phase 4 (Current)
- ✅ Core transformation pipeline integration
- ✅ Comprehensive validation
- ✅ 86% test coverage
- ⏳ Advanced HTTP/2 support
- ⏳ Stick tables and session persistence

### Phase 5 (Next)
- TCP-level processing rules
- Custom log formats
- DNS resolvers
- Additional balance algorithms
- Advanced SSL features

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed roadmap.

## Documentation

- **[FEATURES.md](FEATURES.md)** - Complete feature parity analysis vs HAProxy 3.0
- **[USAGE.md](USAGE.md)** - Comprehensive usage guide with examples
- **[ARCHITECTURE.md](../HAPROXY_CONFIG_TRANSLATOR_ARCHITECTURE.md)** - System architecture
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Development roadmap
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development workflow

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

### Areas for Contribution

**High Priority:**
- HTTP/2 configuration support
- Stick table implementation
- TCP request/response rules
- Custom log formats
- DNS resolver configuration

**Medium Priority:**
- Additional balance algorithms (hdr, static-rr, first)
- Advanced SSL options (SNI, ALPN on servers)
- Monitor URI support
- More specialized health checks

**Documentation:**
- More example configurations
- Tutorial content
- Best practices guide

## Support

- **Issues**: https://github.com/haproxy/config-translator/issues
- **Discussions**: https://github.com/haproxy/config-translator/discussions
- **HAProxy Documentation**: https://docs.haproxy.org/3.0/configuration.html
