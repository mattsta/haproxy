# HAProxy Configuration Translator Architecture

## Executive Summary

A multi-layer, pluggable configuration translation system that converts modern, powerful DSL formats into native HAProxy configuration files. The system is designed with clean separation of concerns, allowing multiple input formats (DSL, YAML, HCL, etc.) to share validation and code generation logic.

**Key Principles**:
- **Zero HAProxy modifications**: Pure translation layer
- **Pluggable parsers**: Easy to add new input formats
- **Shared IR**: Common intermediate representation
- **Powerful DSL**: First-class Lua, templates, composition, logic
- **Type safety**: Validation at every layer
- **Extensible**: Clean abstractions for future features

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Layer (Pluggable)                  │
├───────────────┬─────────────┬──────────────┬────────────────┤
│  DSL Parser   │ YAML Parser │  HCL Parser  │  TOML Parser   │
│   (Lark)      │  (PyYAML)   │  (python-hcl)│   (tomli)      │
└───────┬───────┴──────┬──────┴──────┬───────┴────────┬───────┘
        │              │             │                │
        └──────────────┴─────────────┴────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────────┐
        │      Intermediate Representation (IR)    │
        │                                          │
        │  - Global, Defaults, Frontend, Backend   │
        │  - ACLs, Rules, Servers, Lua Scripts     │
        │  - Variables, Templates, Functions       │
        └──────────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │         Transformation Layer             │
        │                                          │
        │  - Template Expansion                    │
        │  - Variable Resolution                   │
        │  - Function Evaluation                   │
        │  - Loop Unrolling                        │
        └──────────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │           Validation Layer               │
        │                                          │
        │  - Semantic Validation                   │
        │  - Reference Resolution                  │
        │  - Type Checking                         │
        │  - Constraint Validation                 │
        └──────────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │         Lua Extraction Layer             │
        │                                          │
        │  - Extract inline Lua scripts            │
        │  - Generate .lua files                   │
        │  - Template variable interpolation       │
        │  - Dependency tracking                   │
        └──────────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │        Code Generation Layer             │
        │                                          │
        │  - Generate native HAProxy sections      │
        │  - Format output with correct syntax     │
        │  - Add lua-load directives               │
        │  - Preserve comments & metadata          │
        └──────────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────┐
        │         Output Files                     │
        │                                          │
        │  haproxy.cfg  +  lua/*.lua  +  metadata  │
        └──────────────────────────────────────────┘
```

---

## Layer 1: Parser Plugin System

### Parser Interface

All parsers implement a common interface for pluggability:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from .ir import ConfigIR

class ConfigParser(ABC):
    """Base class for all configuration format parsers."""

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the name of this format (e.g., 'dsl', 'yaml', 'hcl')."""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Return supported file extensions (e.g., ['.hap', '.haproxy'])."""
        pass

    @abstractmethod
    def parse(self, source: str, filepath: Path = None) -> ConfigIR:
        """
        Parse source code into intermediate representation.

        Args:
            source: Source code as string
            filepath: Optional path for error reporting and imports

        Returns:
            ConfigIR: Intermediate representation

        Raises:
            ParseError: If source cannot be parsed
        """
        pass

    @abstractmethod
    def validate_syntax(self, source: str) -> list[SyntaxError]:
        """
        Validate syntax without full parsing.

        Returns:
            List of syntax errors (empty if valid)
        """
        pass
```

### Parser Registry

Dynamic parser registration system:

```python
class ParserRegistry:
    """Registry for all available parsers."""

    _parsers: Dict[str, type[ConfigParser]] = {}
    _extension_map: Dict[str, str] = {}

    @classmethod
    def register(cls, parser_class: type[ConfigParser]):
        """Register a parser class."""
        parser = parser_class()
        cls._parsers[parser.format_name] = parser_class

        for ext in parser.file_extensions:
            cls._extension_map[ext] = parser.format_name

    @classmethod
    def get_parser(cls, format_name: str = None,
                   filepath: Path = None) -> ConfigParser:
        """Get parser by format name or auto-detect from file extension."""
        if format_name:
            return cls._parsers[format_name]()

        if filepath:
            ext = filepath.suffix
            if ext in cls._extension_map:
                format_name = cls._extension_map[ext]
                return cls._parsers[format_name]()

        raise ValueError("Cannot determine parser format")

    @classmethod
    def list_formats(cls) -> list[str]:
        """List all registered format names."""
        return list(cls._parsers.keys())
```

### DSL Parser Implementation (Lark)

Primary focus: powerful, feature-rich DSL parser.

**Architecture**:
- Lark grammar defines syntax
- Transformer converts parse tree to IR
- Support for all advanced features (templates, functions, Lua, etc.)

---

## Layer 2: Intermediate Representation (IR)

### IR Design Philosophy

The IR is the heart of the system:
- **Format-agnostic**: Represents HAProxy concepts, not syntax
- **Immutable**: IR objects are frozen after construction
- **Typed**: Full type annotations for validation
- **Hierarchical**: Mirrors HAProxy's structure but enriched
- **Extensible**: Can represent features from any input format

### Core IR Classes

```python
from dataclasses import dataclass, field
from typing import Optional, Union, List, Dict, Any
from enum import Enum

# Enums for type safety
class Mode(Enum):
    HTTP = "http"
    TCP = "tcp"

class BalanceAlgorithm(Enum):
    ROUNDROBIN = "roundrobin"
    LEASTCONN = "leastconn"
    SOURCE = "source"
    URI = "uri"
    URL_PARAM = "url_param"

# Base classes
@dataclass(frozen=True)
class IRNode:
    """Base class for all IR nodes."""
    location: Optional['SourceLocation'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class SourceLocation:
    """Source code location for error reporting."""
    filepath: str
    line: int
    column: int
    length: int = 1

# Configuration sections
@dataclass(frozen=True)
class GlobalConfig(IRNode):
    """Global configuration section."""
    daemon: bool = True
    maxconn: int = 2000
    user: Optional[str] = None
    group: Optional[str] = None
    chroot: Optional[str] = None
    log_targets: List['LogTarget'] = field(default_factory=list)
    lua_scripts: List['LuaScript'] = field(default_factory=list)
    stats: Optional['StatsConfig'] = None
    tuning: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DefaultsConfig(IRNode):
    """Defaults section."""
    mode: Mode = Mode.HTTP
    retries: int = 3
    timeout_connect: str = "5s"
    timeout_client: str = "50s"
    timeout_server: str = "50s"
    log: Optional[str] = "global"
    options: List[str] = field(default_factory=list)
    errorfiles: Dict[int, str] = field(default_factory=dict)

@dataclass(frozen=True)
class ACL(IRNode):
    """ACL definition."""
    name: str
    criterion: str  # e.g., "path_beg", "src", "hdr(host)"
    flags: List[str] = field(default_factory=list)  # e.g., ["-i", "-m", "str"]
    values: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class HttpRequestRule(IRNode):
    """HTTP request rule."""
    action: str  # deny, allow, redirect, set-header, etc.
    condition: Optional[str] = None  # ACL condition
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Bind(IRNode):
    """Bind directive."""
    address: str  # "*:80", "127.0.0.1:8080", etc.
    ssl: bool = False
    ssl_cert: Optional[str] = None
    alpn: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Server(IRNode):
    """Backend server definition."""
    name: str
    address: str
    port: int
    check: bool = False
    check_interval: Optional[str] = None
    rise: int = 2
    fall: int = 3
    weight: int = 1
    maxconn: Optional[int] = None
    ssl: bool = False
    ssl_verify: Optional[str] = None
    backup: bool = False
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ServerTemplate(IRNode):
    """Server template for dynamic generation."""
    prefix: str
    count: int
    fqdn_pattern: str  # e.g., "api-{id}.example.com"
    port: int
    base_server: Server

@dataclass(frozen=True)
class HealthCheck(IRNode):
    """Health check configuration."""
    method: str = "GET"
    uri: str = "/"
    expect_status: Optional[int] = 200
    expect_string: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    interval: Optional[str] = None

@dataclass(frozen=True)
class Frontend(IRNode):
    """Frontend section."""
    name: str
    binds: List[Bind]
    mode: Mode = Mode.HTTP
    acls: List[ACL] = field(default_factory=list)
    http_request_rules: List[HttpRequestRule] = field(default_factory=list)
    http_response_rules: List['HttpResponseRule'] = field(default_factory=list)
    use_backend_rules: List['UseBackendRule'] = field(default_factory=list)
    default_backend: Optional[str] = None
    options: List[str] = field(default_factory=list)
    timeout_client: Optional[str] = None

@dataclass(frozen=True)
class Backend(IRNode):
    """Backend section."""
    name: str
    mode: Mode = Mode.HTTP
    balance: BalanceAlgorithm = BalanceAlgorithm.ROUNDROBIN
    servers: List[Server] = field(default_factory=list)
    server_templates: List[ServerTemplate] = field(default_factory=list)
    health_check: Optional[HealthCheck] = None
    options: List[str] = field(default_factory=list)
    http_request_rules: List[HttpRequestRule] = field(default_factory=list)
    compression: Optional['CompressionConfig'] = None
    cookie: Optional[str] = None
    timeout_server: Optional[str] = None
    timeout_connect: Optional[str] = None

# DSL-specific IR nodes (for advanced features)

@dataclass(frozen=True)
class Variable(IRNode):
    """Variable definition (let x = ...)."""
    name: str
    value: Any
    type_hint: Optional[str] = None

@dataclass(frozen=True)
class Template(IRNode):
    """Template definition for reuse."""
    name: str
    parameters: Dict[str, Any]
    applies_to: str  # "server", "backend", "frontend", etc.

@dataclass(frozen=True)
class LuaScript(IRNode):
    """Lua script definition."""
    name: Optional[str] = None
    source_type: str = "inline"  # "inline" or "file"
    content: str = ""  # Inline Lua code or file path
    parameters: Dict[str, Any] = field(default_factory=dict)  # Template params

@dataclass(frozen=True)
class FunctionCall(IRNode):
    """Function call (for DSL functions)."""
    function_name: str
    arguments: List[Any]
    keyword_arguments: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class IfBlock(IRNode):
    """Conditional block (if/else)."""
    condition: str
    then_config: 'ConfigIR'
    else_config: Optional['ConfigIR'] = None

@dataclass(frozen=True)
class ForLoop(IRNode):
    """For loop for generating config."""
    variable: str
    iterable: Any  # range, list, etc.
    body: 'ConfigIR'

# Top-level configuration
@dataclass(frozen=True)
class ConfigIR(IRNode):
    """Complete HAProxy configuration in IR form."""
    version: str = "2.0"
    global_config: Optional[GlobalConfig] = None
    defaults: Optional[DefaultsConfig] = None
    frontends: List[Frontend] = field(default_factory=list)
    backends: List[Backend] = field(default_factory=list)
    listens: List['Listen'] = field(default_factory=list)

    # DSL-specific features
    variables: Dict[str, Variable] = field(default_factory=dict)
    templates: Dict[str, Template] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)
```

---

## Layer 3: DSL Grammar (Lark)

### Complete Grammar Specification

```lark
// haproxy_dsl.lark - Complete grammar for HAProxy DSL

?start: config

// Top-level configuration
config: "config" identifier "{" statement* "}"

// Statements
?statement: global_section
          | defaults_section
          | frontend_section
          | backend_section
          | listen_section
          | acl_definition
          | template_definition
          | variable_declaration
          | function_definition
          | import_statement
          | if_statement
          | for_statement
          | lua_section

// Global section
global_section: "global" "{" global_property* "}"

?global_property: simple_property
                | log_target
                | lua_subsection
                | stats_subsection

log_target: "log" string log_facility log_level

lua_subsection: "lua" "{" lua_item* "}"

?lua_item: lua_load | lua_script

lua_load: "load" string

lua_script: "script" identifier ("{" LUA_CODE "}" | "(" parameter_list ")" "{" LUA_CODE "}")

LUA_CODE: /(.|\n)*?(?=\n\s*\})/  // Lua code until closing brace

// Defaults section
defaults_section: "defaults" "{" defaults_property* "}"

?defaults_property: simple_property
                  | timeout_block
                  | option_list

timeout_block: "timeout" "{" timeout_item* "}"
timeout_item: identifier ":" duration

// Frontend section
frontend_section: "frontend" identifier "{" frontend_property* "}"

?frontend_property: bind_directive
                  | acl_definition
                  | http_request_block
                  | http_response_block
                  | use_backend_rule
                  | routing_block
                  | simple_property
                  | use_acl_directive

bind_directive: "bind" bind_address bind_option*

bind_address: string | HOST_PORT
HOST_PORT: /[a-zA-Z0-9.*:-]+/

?bind_option: "ssl" ssl_block?
            | identifier value

ssl_block: "{" ssl_property* "}"
?ssl_property: simple_property

use_acl_directive: "use" "acl" ":" "[" identifier_list "]"

http_request_block: "http-request" "{" http_rule* "}"
http_response_block: "http-response" "{" http_rule* "}"

http_rule: action_name http_rule_params if_condition?

action_name: identifier ("." identifier)*  // Allow "lua.function_name"

http_rule_params: (identifier ":" value)*

if_condition: "if" expression

routing_block: "route" "{" route_rule* "}"

route_rule: "to" identifier if_condition?
          | "default" ":" identifier

// Backend section
backend_section: "backend" identifier "{" backend_property* "}"

?backend_property: simple_property
                 | health_check_block
                 | servers_block
                 | server_template_block
                 | compression_block
                 | http_request_block

health_check_block: "health-check" "{" health_check_property* "}"

?health_check_property: simple_property
                      | header_definition

header_definition: "header" string string

servers_block: "servers" "{" server_item* "}"

?server_item: server_definition
            | for_statement

server_definition: "server" identifier "{" server_property* "}"
                 | "server" identifier server_inline_params

server_inline_params: (identifier ":" value)+

?server_property: simple_property
                | template_spread

template_spread: "@" identifier  // Spread template properties

server_template_block: "server-template" identifier "[" range "]" "{" server_property* "}"

range: NUMBER ".." NUMBER

compression_block: "compression" "{" compression_property* "}"

?compression_property: simple_property

// ACL definition
acl_definition: "acl" identifier "{" acl_criterion "}"

acl_criterion: identifier (string | expression)*

// Template definition
template_definition: "template" identifier "{" template_property* "}"

?template_property: simple_property

// Variable declaration
variable_declaration: "let" identifier "=" expression

// Function definition
function_definition: "fn" identifier "(" parameter_list? ")" "->" type_hint block

parameter_list: parameter ("," parameter)*
parameter: identifier (":" type_hint)?

type_hint: identifier ("<" type_hint_list ">")?
type_hint_list: type_hint ("," type_hint)*

block: "{" statement* "}"

// Import
import_statement: "import" string

// Control flow
if_statement: "if" expression block ("else" (if_statement | block))?

for_statement: "for" identifier "in" expression block
             | "for" "(" identifier "," identifier ")" "in" identifier "(" expression ")" block

// Listen section (combined frontend/backend)
listen_section: "listen" identifier "{" listen_property* "}"

?listen_property: frontend_property | backend_property

// Use backend rule
use_backend_rule: "use_backend" identifier if_condition?

// Generic property
simple_property: identifier ":" value

// Values
?value: string
      | number
      | boolean
      | array
      | object
      | expression
      | template_reference

template_reference: "@" identifier

array: "[" [value_list] "]"
value_list: value ("," value)*

object: "{" [property_list] "}"
property_list: object_pair ("," object_pair)*
object_pair: (identifier | string) ":" value

// Expressions
?expression: or_expr

?or_expr: and_expr ("||" and_expr)*

?and_expr: comparison (("&&" | "and") comparison)*

?comparison: add_expr ((">=" | "<=" | ">" | "<" | "==" | "!=" | "eq" | "ne") add_expr)*

?add_expr: mul_expr (("+" | "-") mul_expr)*

?mul_expr: unary_expr (("*" | "/" | "%") unary_expr)*

?unary_expr: ("!" | "-" | "not") unary_expr
           | postfix_expr

?postfix_expr: primary ("." identifier | "[" expression "]" | "(" argument_list? ")")*

?primary: identifier
        | number
        | string
        | boolean
        | "(" expression ")"
        | array
        | object
        | env_var
        | ternary

ternary: expression "?" expression ":" expression

env_var: "env" "(" string ("," value)? ")"  // env("VAR", default)

argument_list: expression ("," expression)*

// Primitives
identifier: /[a-zA-Z_][a-zA-Z0-9_]*/

string: ESCAPED_STRING | TEMPLATE_STRING

TEMPLATE_STRING: /\$\{[^}]+\}/  // "${variable}"

number: NUMBER | FLOAT
NUMBER: /\d+/
FLOAT: /\d+\.\d+/

boolean: "true" | "false"

duration: NUMBER TIME_UNIT
TIME_UNIT: "s" | "ms" | "m" | "h" | "d"

log_facility: "local0" | "local1" | "local2" | "local3" | "local4" | "local5" | "local6" | "local7" | "user" | "daemon"

log_level: "emerg" | "alert" | "crit" | "err" | "warning" | "notice" | "info" | "debug"

identifier_list: identifier ("," identifier)*

// Whitespace and comments
%import common.ESCAPED_STRING
%import common.WS
%import common.CPP_COMMENT
%import common.C_COMMENT

%ignore WS
%ignore CPP_COMMENT
%ignore C_COMMENT
```

### Lark Transformer

Converts parse tree to IR:

```python
from lark import Transformer, Token
from .ir import *

class DSLTransformer(Transformer):
    """Transform Lark parse tree to ConfigIR."""

    def __init__(self):
        self.variables = {}
        self.templates = {}

    def config(self, items):
        """Transform top-level config."""
        name = str(items[0])
        statements = items[1:]

        global_config = None
        defaults = None
        frontends = []
        backends = []

        for stmt in statements:
            if isinstance(stmt, GlobalConfig):
                global_config = stmt
            elif isinstance(stmt, DefaultsConfig):
                defaults = stmt
            elif isinstance(stmt, Frontend):
                frontends.append(stmt)
            elif isinstance(stmt, Backend):
                backends.append(stmt)
            elif isinstance(stmt, Variable):
                self.variables[stmt.name] = stmt
            elif isinstance(stmt, Template):
                self.templates[stmt.name] = stmt

        return ConfigIR(
            global_config=global_config,
            defaults=defaults,
            frontends=frontends,
            backends=backends,
            variables=self.variables,
            templates=self.templates
        )

    def global_section(self, items):
        """Transform global section."""
        properties = {}
        log_targets = []
        lua_scripts = []

        for item in items:
            if isinstance(item, tuple) and item[0] == 'log':
                log_targets.append(item[1])
            elif isinstance(item, LuaScript):
                lua_scripts.append(item)
            elif isinstance(item, tuple):
                properties[item[0]] = item[1]

        return GlobalConfig(
            daemon=properties.get('daemon', True),
            maxconn=properties.get('maxconn', 2000),
            log_targets=log_targets,
            lua_scripts=lua_scripts
        )

    def frontend_section(self, items):
        """Transform frontend section."""
        name = str(items[0])
        properties = items[1:]

        binds = []
        acls = []
        http_request_rules = []
        use_backend_rules = []
        default_backend = None

        for prop in properties:
            if isinstance(prop, Bind):
                binds.append(prop)
            elif isinstance(prop, ACL):
                acls.append(prop)
            elif isinstance(prop, HttpRequestRule):
                http_request_rules.append(prop)
            # ... handle other property types

        return Frontend(
            name=name,
            binds=binds,
            acls=acls,
            http_request_rules=http_request_rules,
            use_backend_rules=use_backend_rules,
            default_backend=default_backend
        )

    def backend_section(self, items):
        """Transform backend section."""
        name = str(items[0])
        properties = items[1:]

        servers = []
        balance = BalanceAlgorithm.ROUNDROBIN
        health_check = None

        for prop in properties:
            if isinstance(prop, Server):
                servers.append(prop)
            elif isinstance(prop, tuple) and prop[0] == 'balance':
                balance = BalanceAlgorithm(prop[1])
            elif isinstance(prop, HealthCheck):
                health_check = prop

        return Backend(
            name=name,
            balance=balance,
            servers=servers,
            health_check=health_check
        )

    def lua_script(self, items):
        """Transform Lua script definition."""
        name = str(items[0])
        code = str(items[1])

        return LuaScript(
            name=name,
            source_type="inline",
            content=code
        )

    def variable_declaration(self, items):
        """Transform variable declaration."""
        name = str(items[0])
        value = items[1]

        return Variable(name=name, value=value)

    def for_statement(self, items):
        """Transform for loop."""
        var = str(items[0])
        iterable = items[1]
        body = items[2:]

        return ForLoop(
            variable=var,
            iterable=iterable,
            body=body
        )

    # ... many more transformation methods

    def identifier(self, items):
        """Transform identifier."""
        return str(items[0])

    def string(self, items):
        """Transform string literal."""
        value = items[0]
        if isinstance(value, Token):
            # Remove quotes
            return value.value[1:-1]
        return str(value)

    def number(self, items):
        """Transform number."""
        value = items[0]
        if '.' in str(value):
            return float(value)
        return int(value)

    def boolean(self, items):
        """Transform boolean."""
        return str(items[0]) == "true"
```

---

## Layer 4: Transformation Layer

### Template Expansion

```python
class TemplateExpander:
    """Expand templates and spreads in IR."""

    def __init__(self, templates: Dict[str, Template]):
        self.templates = templates

    def expand(self, ir: ConfigIR) -> ConfigIR:
        """Expand all templates in configuration."""
        expanded_backends = [
            self._expand_backend(backend) for backend in ir.backends
        ]

        return dataclasses.replace(ir, backends=expanded_backends)

    def _expand_backend(self, backend: Backend) -> Backend:
        """Expand templates in backend."""
        expanded_servers = []

        for server in backend.servers:
            if hasattr(server, 'template_ref') and server.template_ref:
                template = self.templates[server.template_ref]
                # Merge template properties with server properties
                expanded = self._merge_template(server, template)
                expanded_servers.append(expanded)
            else:
                expanded_servers.append(server)

        return dataclasses.replace(backend, servers=expanded_servers)

    def _merge_template(self, server: Server, template: Template) -> Server:
        """Merge template into server."""
        # Template properties as defaults, server properties override
        merged_props = {**template.parameters, **self._server_to_dict(server)}
        return Server(**merged_props)
```

### Variable Resolution

```python
class VariableResolver:
    """Resolve variable references and environment variables."""

    def __init__(self, variables: Dict[str, Variable], env: Dict[str, str] = None):
        self.variables = variables
        self.env = env or os.environ

    def resolve(self, ir: ConfigIR) -> ConfigIR:
        """Resolve all variables in IR."""
        # Walk entire IR tree and resolve variable references
        return self._walk_ir(ir)

    def _walk_ir(self, node):
        """Recursively walk IR and resolve variables."""
        if isinstance(node, str):
            return self._resolve_string(node)
        elif isinstance(node, (list, tuple)):
            return [self._walk_ir(item) for item in node]
        elif isinstance(node, dict):
            return {k: self._walk_ir(v) for k, v in node.items()}
        elif dataclasses.is_dataclass(node):
            # Reconstruct dataclass with resolved fields
            fields = {}
            for field in dataclasses.fields(node):
                value = getattr(node, field.name)
                fields[field.name] = self._walk_ir(value)
            return type(node)(**fields)
        else:
            return node

    def _resolve_string(self, s: str) -> str:
        """Resolve ${var} and env() in strings."""
        import re

        # Resolve ${VAR:default}
        def replace_var(match):
            parts = match.group(1).split(':', 1)
            var_name = parts[0]
            default = parts[1] if len(parts) > 1 else None

            if var_name in self.variables:
                return str(self.variables[var_name].value)
            elif var_name in self.env:
                return self.env[var_name]
            elif default is not None:
                return default
            else:
                raise ValueError(f"Undefined variable: {var_name}")

        result = re.sub(r'\$\{([^}]+)\}', replace_var, s)

        # Resolve env("VAR", "default")
        result = re.sub(
            r'env\("([^"]+)"(?:,\s*"([^"]+)")?\)',
            lambda m: self.env.get(m.group(1), m.group(2) or ''),
            result
        )

        return result
```

### Loop Unroller

```python
class LoopUnroller:
    """Unroll for loops to generate concrete config items."""

    def unroll(self, ir: ConfigIR) -> ConfigIR:
        """Unroll all loops in IR."""
        expanded_backends = []

        for backend in ir.backends:
            expanded = self._unroll_backend(backend)
            expanded_backends.append(expanded)

        return dataclasses.replace(ir, backends=expanded_backends)

    def _unroll_backend(self, backend: Backend) -> Backend:
        """Unroll loops in backend servers."""
        concrete_servers = []

        for item in backend.servers:
            if isinstance(item, ForLoop):
                # Unroll the loop
                for value in self._evaluate_iterable(item.iterable):
                    # Bind loop variable
                    scope = {item.variable: value}
                    # Generate servers from loop body
                    servers = self._execute_loop_body(item.body, scope)
                    concrete_servers.extend(servers)
            else:
                concrete_servers.append(item)

        return dataclasses.replace(backend, servers=concrete_servers)

    def _evaluate_iterable(self, iterable):
        """Evaluate loop iterable (range, list, etc.)."""
        if isinstance(iterable, range):
            return iterable
        elif isinstance(iterable, list):
            return iterable
        elif isinstance(iterable, tuple) and iterable[0] == 'range':
            # Range expression like 1..10
            return range(iterable[1], iterable[2] + 1)
        else:
            raise ValueError(f"Invalid iterable: {iterable}")
```

---

## Layer 5: Validation Layer

### Semantic Validator

```python
class SemanticValidator:
    """Validate semantic correctness of configuration."""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []

    def validate(self, ir: ConfigIR) -> ValidationResult:
        """Run all validation checks."""
        self.errors = []
        self.warnings = []

        self._validate_backend_references(ir)
        self._validate_acl_references(ir)
        self._validate_server_configs(ir)
        self._validate_lua_scripts(ir)
        self._validate_health_checks(ir)
        self._check_mode_compatibility(ir)

        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings
        )

    def _validate_backend_references(self, ir: ConfigIR):
        """Ensure all referenced backends exist."""
        backend_names = {b.name for b in ir.backends}

        for frontend in ir.frontends:
            # Check default_backend
            if frontend.default_backend and frontend.default_backend not in backend_names:
                self.errors.append(ValidationError(
                    message=f"Frontend '{frontend.name}' references undefined backend '{frontend.default_backend}'",
                    location=frontend.location
                ))

            # Check use_backend rules
            for rule in frontend.use_backend_rules:
                if rule.backend not in backend_names:
                    self.errors.append(ValidationError(
                        message=f"Frontend '{frontend.name}' use_backend references undefined backend '{rule.backend}'",
                        location=rule.location
                    ))

    def _validate_server_configs(self, ir: ConfigIR):
        """Validate server configurations."""
        for backend in ir.backends:
            if not backend.servers and not backend.server_templates:
                self.warnings.append(ValidationWarning(
                    message=f"Backend '{backend.name}' has no servers defined",
                    location=backend.location
                ))

            for server in backend.servers:
                if server.ssl and not server.ssl_verify:
                    self.warnings.append(ValidationWarning(
                        message=f"Server '{server.name}' uses SSL without verification",
                        location=server.location
                    ))

    def _validate_lua_scripts(self, ir: ConfigIR):
        """Validate Lua script syntax."""
        if not ir.global_config:
            return

        for lua_script in ir.global_config.lua_scripts:
            if lua_script.source_type == "inline":
                # Basic Lua syntax check
                errors = self._check_lua_syntax(lua_script.content)
                for error in errors:
                    self.errors.append(ValidationError(
                        message=f"Lua syntax error in script '{lua_script.name}': {error}",
                        location=lua_script.location
                    ))

    def _check_lua_syntax(self, lua_code: str) -> List[str]:
        """Check Lua syntax (basic validation)."""
        # Could integrate with Lua parser or use subprocess to call luac
        errors = []

        # Check for balanced braces
        if lua_code.count('{') != lua_code.count('}'):
            errors.append("Unbalanced braces")

        # Check for basic Lua keywords
        if 'function' in lua_code:
            # Ensure proper function syntax
            import re
            func_pattern = r'function\s+\w+\s*\([^)]*\)'
            if not re.search(func_pattern, lua_code):
                errors.append("Invalid function syntax")

        return errors
```

---

## Layer 6: Lua Extraction Layer

### Lua Manager

```python
class LuaManager:
    """Manage Lua script extraction and generation."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir / "lua"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.script_map: Dict[str, Path] = {}

    def extract_lua_scripts(self, ir: ConfigIR) -> ConfigIR:
        """Extract inline Lua to files and update IR with references."""
        if not ir.global_config:
            return ir

        updated_scripts = []

        for script in ir.global_config.lua_scripts:
            if script.source_type == "inline":
                # Generate file for inline script
                filepath = self._generate_lua_file(script)
                self.script_map[script.name or "unnamed"] = filepath

                # Create new script pointing to file
                updated_script = dataclasses.replace(
                    script,
                    source_type="file",
                    content=str(filepath)
                )
                updated_scripts.append(updated_script)
            else:
                updated_scripts.append(script)

        updated_global = dataclasses.replace(
            ir.global_config,
            lua_scripts=updated_scripts
        )

        return dataclasses.replace(ir, global_config=updated_global)

    def _generate_lua_file(self, script: LuaScript) -> Path:
        """Generate Lua file from inline script."""
        # Create filename from script name or hash
        if script.name:
            filename = f"{script.name}.lua"
        else:
            import hashlib
            hash_val = hashlib.sha256(script.content.encode()).hexdigest()[:8]
            filename = f"generated_{hash_val}.lua"

        filepath = self.output_dir / filename

        # Interpolate template variables if present
        content = self._interpolate_lua_template(script)

        # Write Lua file
        filepath.write_text(content)

        return filepath

    def _interpolate_lua_template(self, script: LuaScript) -> str:
        """Interpolate ${param} in Lua code."""
        content = script.content

        for param_name, param_value in script.parameters.items():
            placeholder = f"${{{param_name}}}"
            content = content.replace(placeholder, str(param_value))

        return content

    def get_lua_load_directives(self) -> List[str]:
        """Get list of lua-load directives for generated config."""
        return [f"lua-load {path}" for path in self.script_map.values()]
```

---

## Layer 7: Code Generation Layer

### HAProxy Code Generator

```python
class HAProxyCodeGenerator:
    """Generate native HAProxy configuration from IR."""

    def __init__(self, lua_manager: LuaManager = None):
        self.lua_manager = lua_manager
        self.indent_level = 0
        self.indent_str = "    "  # 4 spaces

    def generate(self, ir: ConfigIR) -> str:
        """Generate complete HAProxy configuration."""
        lines = []

        # Generate global section
        if ir.global_config:
            lines.extend(self._generate_global(ir.global_config))
            lines.append("")

        # Generate defaults section
        if ir.defaults:
            lines.extend(self._generate_defaults(ir.defaults))
            lines.append("")

        # Generate frontends
        for frontend in ir.frontends:
            lines.extend(self._generate_frontend(frontend))
            lines.append("")

        # Generate backends
        for backend in ir.backends:
            lines.extend(self._generate_backend(backend))
            lines.append("")

        return "\n".join(lines)

    def _generate_global(self, global_config: GlobalConfig) -> List[str]:
        """Generate global section."""
        lines = ["global"]

        if global_config.daemon:
            lines.append(self._indent("daemon"))

        lines.append(self._indent(f"maxconn {global_config.maxconn}"))

        if global_config.user:
            lines.append(self._indent(f"user {global_config.user}"))

        if global_config.group:
            lines.append(self._indent(f"group {global_config.group}"))

        # Log targets
        for log in global_config.log_targets:
            lines.append(self._indent(f"log {log.address} {log.facility} {log.level}"))

        # Lua scripts
        for script in global_config.lua_scripts:
            if script.source_type == "file":
                lines.append(self._indent(f"lua-load {script.content}"))

        return lines

    def _generate_frontend(self, frontend: Frontend) -> List[str]:
        """Generate frontend section."""
        lines = [f"frontend {frontend.name}"]

        # Bind directives
        for bind in frontend.binds:
            bind_line = f"bind {bind.address}"

            if bind.ssl:
                bind_line += " ssl"
                if bind.ssl_cert:
                    bind_line += f" crt {bind.ssl_cert}"
                if bind.alpn:
                    bind_line += f" alpn {','.join(bind.alpn)}"

            lines.append(self._indent(bind_line))

        # Mode
        lines.append(self._indent(f"mode {frontend.mode.value}"))

        # ACLs
        for acl in frontend.acls:
            acl_line = f"acl {acl.name} {acl.criterion}"
            if acl.flags:
                acl_line += " " + " ".join(acl.flags)
            if acl.values:
                acl_line += " " + " ".join(acl.values)
            lines.append(self._indent(acl_line))

        # HTTP request rules
        for rule in frontend.http_request_rules:
            rule_line = f"http-request {rule.action}"

            for key, value in rule.parameters.items():
                if key == "status":
                    rule_line += f" status {value}"
                elif key == "header":
                    rule_line += f" {value}"
                else:
                    rule_line += f" {key} {value}"

            if rule.condition:
                rule_line += f" if {rule.condition}"

            lines.append(self._indent(rule_line))

        # Use backend rules
        for rule in frontend.use_backend_rules:
            use_line = f"use_backend {rule.backend}"
            if rule.condition:
                use_line += f" if {rule.condition}"
            lines.append(self._indent(use_line))

        # Default backend
        if frontend.default_backend:
            lines.append(self._indent(f"default_backend {frontend.default_backend}"))

        return lines

    def _generate_backend(self, backend: Backend) -> List[str]:
        """Generate backend section."""
        lines = [f"backend {backend.name}"]

        # Mode
        lines.append(self._indent(f"mode {backend.mode.value}"))

        # Balance algorithm
        lines.append(self._indent(f"balance {backend.balance.value}"))

        # Options
        for option in backend.options:
            lines.append(self._indent(f"option {option}"))

        # Cookie
        if backend.cookie:
            lines.append(self._indent(f"cookie {backend.cookie}"))

        # Health check
        if backend.health_check:
            hc = backend.health_check
            check_line = f"http-check send meth {hc.method} uri {hc.uri}"
            lines.append(self._indent(check_line))

            if hc.expect_status:
                lines.append(self._indent(f"http-check expect status {hc.expect_status}"))

        # Servers
        for server in backend.servers:
            server_line = f"server {server.name} {server.address}:{server.port}"

            if server.check:
                server_line += " check"
                if server.check_interval:
                    server_line += f" inter {server.check_interval}"
                server_line += f" rise {server.rise} fall {server.fall}"

            if server.weight != 1:
                server_line += f" weight {server.weight}"

            if server.maxconn:
                server_line += f" maxconn {server.maxconn}"

            if server.ssl:
                server_line += " ssl"
                if server.ssl_verify:
                    server_line += f" verify {server.ssl_verify}"

            if server.backup:
                server_line += " backup"

            lines.append(self._indent(server_line))

        # Server templates
        for template in backend.server_templates:
            tmpl_line = (f"server-template {template.prefix} {template.count} "
                        f"{template.fqdn_pattern}:{template.port}")

            base = template.base_server
            if base.check:
                tmpl_line += " check"

            lines.append(self._indent(tmpl_line))

        return lines

    def _generate_defaults(self, defaults: DefaultsConfig) -> List[str]:
        """Generate defaults section."""
        lines = ["defaults"]

        lines.append(self._indent(f"mode {defaults.mode.value}"))

        if defaults.log:
            lines.append(self._indent(f"log {defaults.log}"))

        lines.append(self._indent(f"retries {defaults.retries}"))

        # Timeouts
        lines.append(self._indent(f"timeout connect {defaults.timeout_connect}"))
        lines.append(self._indent(f"timeout client {defaults.timeout_client}"))
        lines.append(self._indent(f"timeout server {defaults.timeout_server}"))

        # Options
        for option in defaults.options:
            lines.append(self._indent(f"option {option}"))

        return lines

    def _indent(self, line: str) -> str:
        """Add indentation to line."""
        return self.indent_str + line
```

---

## Complete Implementation Structure

```
haproxy-config-translator/
├── pyproject.toml
├── README.md
├── LICENSE
├── setup.py
│
├── src/
│   └── haproxy_translator/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       │
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py          # ConfigParser interface, ParserRegistry
│       │   ├── dsl_parser.py    # DSL parser (Lark)
│       │   ├── yaml_parser.py   # YAML parser (optional)
│       │   └── hcl_parser.py    # HCL parser (optional)
│       │
│       ├── ir/
│       │   ├── __init__.py
│       │   ├── nodes.py         # All IR dataclasses
│       │   ├── builder.py       # IR builder helpers
│       │   └── visitors.py      # IR visitor pattern
│       │
│       ├── grammars/
│       │   ├── haproxy_dsl.lark # DSL grammar
│       │   └── README.md
│       │
│       ├── transformers/
│       │   ├── __init__.py
│       │   ├── dsl_transformer.py    # Lark transformer
│       │   ├── template_expander.py  # Template expansion
│       │   ├── variable_resolver.py  # Variable resolution
│       │   └── loop_unroller.py      # Loop unrolling
│       │
│       ├── validators/
│       │   ├── __init__.py
│       │   ├── semantic.py      # Semantic validation
│       │   ├── type_checker.py  # Type checking
│       │   └── rules.py         # Validation rules
│       │
│       ├── lua/
│       │   ├── __init__.py
│       │   ├── manager.py       # Lua extraction and management
│       │   └── validator.py     # Lua syntax validation
│       │
│       ├── codegen/
│       │   ├── __init__.py
│       │   ├── haproxy.py       # HAProxy code generator
│       │   ├── formatter.py     # Output formatting
│       │   └── templates/       # Code generation templates
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py          # CLI implementation
│       │   ├── commands.py      # CLI commands
│       │   └── utils.py         # CLI utilities
│       │
│       └── utils/
│           ├── __init__.py
│           ├── errors.py        # Error classes
│           ├── locations.py     # Source location tracking
│           └── helpers.py       # Utility functions
│
├── tests/
│   ├── __init__.py
│   ├── test_parsers/
│   ├── test_transformers/
│   ├── test_validators/
│   ├── test_codegen/
│   └── fixtures/
│       ├── configs/             # Example configs
│       └── expected/            # Expected outputs
│
├── examples/
│   ├── basic.hap                # Basic DSL example
│   ├── advanced.hap             # Advanced features
│   ├── lua_integration.hap      # Lua examples
│   └── migration/               # Migration examples
│
└── docs/
    ├── architecture.md
    ├── dsl_reference.md
    ├── api.md
    └── migration_guide.md
```

---

## CLI Interface

```bash
# Translate config
haproxy-translate config.hap -o haproxy.cfg

# Validate without generating
haproxy-translate config.hap --validate

# Specify input format
haproxy-translate config.yaml --format yaml -o haproxy.cfg

# Watch mode (regenerate on change)
haproxy-translate config.hap -o haproxy.cfg --watch

# Debug mode (show IR, validation)
haproxy-translate config.hap --debug

# List available parsers
haproxy-translate --list-formats
```

---

## Summary

This architecture provides:

1. **Pluggable Parsers**: Easy to add new input formats
2. **Powerful DSL**: Modern features (templates, loops, Lua, variables)
3. **Clean Separation**: Each layer has single responsibility
4. **Type Safety**: Full typing throughout
5. **Extensibility**: New features added at appropriate layer
6. **Testability**: Each component independently testable
7. **Error Reporting**: Source location tracking for precise errors

**Next Steps**: Ready to implement! We'll build this iteratively, starting with:
1. IR data structures
2. DSL parser with Lark
3. Basic code generator
4. Then add transformation and validation layers

Ready to start coding?
