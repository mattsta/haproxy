# HAProxy Config Translator - Architecture Guide

This document explains how the HAProxy Config Translator works internally.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HAProxy Config Translator                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌────────────┐   ┌───────────────┐  │
│  │  Source  │──▶│    Parser    │──▶│ Transformer│──▶│   Code Gen    │  │
│  │  (.hap)  │   │  (Lark AST)  │   │    (IR)    │   │ (HAProxy cfg) │  │
│  └──────────┘   └──────────────┘   └────────────┘   └───────────────┘  │
│                        │                  │                  │          │
│                        ▼                  ▼                  ▼          │
│                 haproxy_dsl.lark   IR Node Classes    haproxy.py        │
│                                    (nodes.py)                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Stages

### Stage 1: Parsing (Lark Grammar)

The DSL is defined in a Lark grammar file that specifies the syntax:

**Location:** `src/haproxy_translator/grammars/haproxy_dsl.lark`

```lark
// Example grammar rules
config: statement+

statement: global_section
         | defaults_section
         | frontend_section
         | backend_section
         | listen_section
         | variables_section

global_section: "global" "{" global_property* "}"

global_property: "daemon" ":" boolean     -> global_daemon
               | "maxconn" ":" number     -> global_maxconn
               | "log" ":" string         -> global_log
               // ... 165+ global directives
```

**Key Features:**
- Declarative grammar definition
- Automatic AST generation
- Priority-based token resolution
- Error recovery and reporting

### Stage 2: Transformation (AST to IR)

The transformer converts Lark's AST into our Intermediate Representation:

**Location:** `src/haproxy_translator/transformers/dsl_transformer.py`

```python
class DSLTransformer(Transformer):
    """Transform Lark AST to IR nodes."""

    def global_daemon(self, items):
        """Transform daemon directive."""
        return ("daemon", items[0])

    def global_maxconn(self, items):
        """Transform maxconn directive."""
        return ("maxconn", int(items[0]))

    def config(self, items):
        """Build complete ConfigIR from all sections."""
        ir = ConfigIR()
        for item in items:
            if isinstance(item, GlobalConfig):
                ir.globals = item
            elif isinstance(item, Frontend):
                ir.frontends.append(item)
            # ...
        return ir
```

**Transformer Pipeline:**
1. **Variable Resolution** - Expands `${var}` references
2. **Loop Unrolling** - Expands `for` loops into repeated elements
3. **Template Expansion** - Processes template blocks
4. **IR Construction** - Builds typed IR node tree

### Stage 3: Intermediate Representation (IR)

The IR is a typed, validated representation of the configuration:

**Location:** `src/haproxy_translator/ir/nodes.py`

```python
@dataclass
class ConfigIR:
    """Root IR node containing complete configuration."""
    globals: GlobalConfig | None = None
    defaults: list[DefaultsConfig] = field(default_factory=list)
    frontends: list[Frontend] = field(default_factory=list)
    backends: list[Backend] = field(default_factory=list)
    listens: list[Listen] = field(default_factory=list)
    resolvers: list[ResolversSection] = field(default_factory=list)
    peers: list[PeersSection] = field(default_factory=list)
    mailers: list[MailersSection] = field(default_factory=list)

@dataclass
class GlobalConfig(IRNode):
    """Global section configuration."""
    daemon: bool | None = None
    maxconn: int | None = None
    log: str | None = None
    # ... 165+ fields for all global directives

@dataclass
class Server(IRNode):
    """Server definition within a backend."""
    name: str = ""
    address: str = ""
    port: int | None = None
    check: bool | None = None
    weight: int | None = None
    maxconn: int | None = None
    # ... 55+ server options
```

**IR Benefits:**
- Type-safe configuration
- Validation at construction
- Easy to traverse and analyze
- Decoupled from syntax

### Stage 4: Code Generation

The code generator produces native HAProxy configuration:

**Location:** `src/haproxy_translator/codegen/haproxy.py`

```python
class HAProxyCodeGenerator:
    """Generate native HAProxy configuration from IR."""

    def generate(self, ir: ConfigIR) -> str:
        """Generate complete configuration."""
        lines = []

        if ir.globals:
            lines.extend(self._generate_global(ir.globals))

        for defaults in ir.defaults:
            lines.extend(self._generate_defaults(defaults))

        for frontend in ir.frontends:
            lines.extend(self._generate_frontend(frontend))

        for backend in ir.backends:
            lines.extend(self._generate_backend(backend))

        return "\n".join(lines)

    def _generate_server(self, server: Server) -> str:
        """Generate server directive."""
        parts = [f"server {server.name} {server.address}"]

        if server.port:
            parts[0] += f":{server.port}"

        if server.check:
            parts.append("check")

        if server.weight is not None:
            parts.append(f"weight {server.weight}")

        # ... 55+ server options

        return " ".join(parts)
```

## Directory Structure

```
src/haproxy_translator/
├── __init__.py              # Package exports
├── __main__.py              # Entry point
├── cli/
│   └── main.py              # CLI argument parsing
├── grammars/
│   └── haproxy_dsl.lark     # Lark grammar (1173 lines)
├── ir/
│   ├── __init__.py          # IR exports
│   └── nodes.py             # IR dataclasses (1054 lines)
├── parsers/
│   ├── base.py              # Base parser class
│   └── dsl_parser.py        # DSL parser implementation
├── transformers/
│   ├── dsl_transformer.py   # Main transformer (5370 lines)
│   ├── loop_unroller.py     # Loop expansion
│   ├── template_expander.py # Template processing
│   └── variable_resolver.py # Variable substitution
├── codegen/
│   └── haproxy.py           # HAProxy output (1981 lines)
├── validators/
│   └── semantic.py          # Semantic validation
├── lua/
│   └── manager.py           # Lua script management
└── utils/
    └── errors.py            # Error types
```

## Extension Points

### Adding a New Global Directive

1. **Add to Grammar** (`haproxy_dsl.lark`):
```lark
global_property: ...
               | "my-new-directive" ":" string -> global_my_new_directive
```

2. **Add to IR** (`nodes.py`):
```python
@dataclass
class GlobalConfig(IRNode):
    # ...
    my_new_directive: str | None = None
```

3. **Add Transformer** (`dsl_transformer.py`):
```python
def global_my_new_directive(self, items):
    return ("my_new_directive", str(items[0]))
```

4. **Add Code Generator** (`haproxy.py`):
```python
if global_config.my_new_directive:
    lines.append(self._indent(f"my-new-directive {global_config.my_new_directive}"))
```

5. **Add Tests**:
```python
def test_my_new_directive(parser, codegen):
    source = '''
    global {
        my-new-directive: "value"
    }
    '''
    ir = parser.parse(source)
    output = codegen.generate(ir)
    assert "my-new-directive value" in output
```

### Adding a New Proxy Keyword

Same pattern applies for frontend/backend/listen keywords:

1. Add grammar rule with section prefix (e.g., `frontend_my_keyword`)
2. Add IR field to appropriate dataclass
3. Add transformer method
4. Add codegen output
5. Add tests

## Processing Pipeline Details

### Variable Resolution

```python
class VariableResolver:
    """Resolve variable references in AST."""

    def resolve(self, tree, variables):
        """
        Process variable references:
        - ${var} - Simple variable
        - ${env.VAR} - Environment variable
        - ${env.VAR:-default} - With default value
        """
```

### Loop Unrolling

```python
class LoopUnroller:
    """Expand for loops in configuration."""

    def unroll(self, ir):
        """
        Transform:
            for i in [1, 2, 3] {
                server "web${i}" "10.0.1.${i}":8080
            }

        Into:
            server web1 10.0.1.1:8080
            server web2 10.0.1.2:8080
            server web3 10.0.1.3:8080
        """
```

## Error Handling

The translator provides detailed error messages:

```python
class ParseError(TranslatorError):
    """Parsing failed."""
    def __init__(self, message, line=None, column=None, context=None):
        self.line = line
        self.column = column
        self.context = context

class ValidationError(TranslatorError):
    """Semantic validation failed."""
    pass

class CodeGenError(TranslatorError):
    """Code generation failed."""
    pass
```

Example error output:
```
ParseError: Unexpected token at line 15, column 8
  |
15|     balance: "invalid-algorithm"
  |              ^^^^^^^^^^^^^^^^^^^
  | Expected one of: roundrobin, leastconn, source, uri, ...
```

## Performance Characteristics

- **Parsing:** O(n) where n = input size
- **Transformation:** O(n) single pass
- **Code Generation:** O(m) where m = IR size
- **Memory:** Linear with configuration size
- **Typical Translation:** <100ms for 1000-line configs

## Testing Architecture

```
tests/
├── test_parser/           # Grammar and parsing tests
├── test_transformers/     # Transformer tests
├── test_codegen/          # Code generation tests
├── test_validators/       # Validation tests
├── test_cli/              # CLI tests
├── test_lua/              # Lua integration tests
└── test_*.py              # Feature-specific tests
```

**Test Count:** 1198 tests covering all features

## See Also

- [Syntax Reference](SYNTAX_REFERENCE.md) - Complete DSL syntax
- [Quick Start](QUICK_START.md) - Getting started guide
- [Migration Guide](MIGRATION_GUIDE.md) - Converting existing configs
