"""Intermediate Representation (IR) node definitions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from ..utils.errors import SourceLocation


# Enums for type safety
class Mode(Enum):
    """HAProxy mode."""

    HTTP = "http"
    TCP = "tcp"


class BalanceAlgorithm(Enum):
    """Load balancing algorithm."""

    ROUNDROBIN = "roundrobin"
    LEASTCONN = "leastconn"
    SOURCE = "source"
    URI = "uri"
    URL_PARAM = "url_param"
    RANDOM = "random"


class LogLevel(Enum):
    """Log level."""

    EMERG = "emerg"
    ALERT = "alert"
    CRIT = "crit"
    ERR = "err"
    WARNING = "warning"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"


class LogFacility(Enum):
    """Syslog facility."""

    LOCAL0 = "local0"
    LOCAL1 = "local1"
    LOCAL2 = "local2"
    LOCAL3 = "local3"
    LOCAL4 = "local4"
    LOCAL5 = "local5"
    LOCAL6 = "local6"
    LOCAL7 = "local7"
    USER = "user"
    DAEMON = "daemon"


# Base classes
@dataclass(frozen=True)
class IRNode:
    """Base class for all IR nodes."""

    location: SourceLocation | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# Configuration components
@dataclass(frozen=True)
class LogTarget(IRNode):
    """Log target configuration."""

    address: str = field(default="")
    facility: LogFacility = LogFacility.LOCAL0
    level: LogLevel = LogLevel.INFO
    minlevel: LogLevel | None = None


@dataclass(frozen=True)
class LuaScript(IRNode):
    """Lua script definition."""

    name: str | None = None
    source_type: str = "inline"  # "inline" or "file"
    content: str = ""  # Inline Lua code or file path
    parameters: dict[str, Any] = field(default_factory=dict)  # Template params


@dataclass(frozen=True)
class StatsConfig(IRNode):
    """Stats configuration."""

    enable: bool = True
    uri: str = "/stats"
    auth: str | None = None
    refresh: str | None = None


@dataclass(frozen=True)
class GlobalConfig(IRNode):
    """Global configuration section."""

    daemon: bool = True
    maxconn: int = 2000
    user: str | None = None
    group: str | None = None
    chroot: str | None = None
    pidfile: str | None = None
    log_targets: list[LogTarget] = field(default_factory=list)
    lua_scripts: list[LuaScript] = field(default_factory=list)
    stats: StatsConfig | None = None
    tuning: dict[str, Any] = field(default_factory=dict)
    ssl_default_bind_ciphers: str | None = None
    ssl_default_bind_options: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DefaultsConfig(IRNode):
    """Defaults section."""

    mode: Mode = Mode.HTTP
    retries: int = 3
    timeout_connect: str = "5s"
    timeout_client: str = "50s"
    timeout_server: str = "50s"
    timeout_check: str | None = None
    timeout_queue: str | None = None
    log: str | None = "global"
    options: list[str] = field(default_factory=list)
    errorfiles: dict[int, str] = field(default_factory=dict)
    http_check: Optional["HealthCheck"] = None


@dataclass(frozen=True)
class ACL(IRNode):
    """ACL definition."""

    name: str = ""
    criterion: str = ""  # e.g., "path_beg", "src", "hdr(host)"
    flags: list[str] = field(default_factory=list)  # e.g., ["-i", "-m", "str"]
    values: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        parts = [f"acl {self.name} {self.criterion}"]
        if self.flags:
            parts.append(" ".join(self.flags))
        if self.values:
            parts.append(" ".join(self.values))
        return " ".join(parts)


@dataclass(frozen=True)
class HttpRequestRule(IRNode):
    """HTTP request rule."""

    action: str = ""  # deny, allow, redirect, set-header, lua.xxx, etc.
    condition: str | None = None  # ACL condition
    parameters: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        parts = [f"http-request {self.action}"]
        for key, value in self.parameters.items():
            if isinstance(value, str) and " " in value:
                parts.append(f'{key} "{value}"')
            else:
                parts.append(f"{key} {value}")
        if self.condition:
            parts.append(f"if {self.condition}")
        return " ".join(parts)


@dataclass(frozen=True)
class HttpResponseRule(IRNode):
    """HTTP response rule."""

    action: str = ""
    condition: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Bind(IRNode):
    """Bind directive."""

    address: str = ""  # "*:80", "127.0.0.1:8080", etc.
    ssl: bool = False
    ssl_cert: str | None = None
    alpn: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        parts = [f"bind {self.address}"]
        if self.ssl:
            parts.append("ssl")
            if self.ssl_cert:
                parts.append(f"crt {self.ssl_cert}")
            if self.alpn:
                parts.append(f"alpn {','.join(self.alpn)}")
        for key, value in self.options.items():
            if isinstance(value, bool) and value:
                parts.append(key)
            elif value:
                parts.append(f"{key} {value}")
        return " ".join(parts)


@dataclass(frozen=True)
class Server(IRNode):
    """Backend server definition."""

    name: str = ""
    address: str = ""
    port: int = 8080
    check: bool = False
    check_interval: str | None = None  # inter
    rise: int = 2
    fall: int = 3
    weight: int = 1
    maxconn: int | None = None
    ssl: bool = False
    ssl_verify: str | None = None
    backup: bool = False
    disabled: bool = False
    send_proxy: bool = False
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ServerTemplate(IRNode):
    """Server template for dynamic generation."""

    prefix: str = ""
    count: int = 0
    fqdn_pattern: str = ""  # e.g., "api-{id}.example.com"
    port: int = 8080
    base_server: Server | None = None


@dataclass(frozen=True)
class HealthCheck(IRNode):
    """Health check configuration."""

    method: str = "GET"
    uri: str = "/"
    expect_status: int | None = 200
    expect_string: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    interval: str | None = None


@dataclass(frozen=True)
class CompressionConfig(IRNode):
    """Compression configuration."""

    algo: str = "gzip"  # gzip, deflate, raw-deflate
    types: list[str] = field(default_factory=list)
    offload: bool = False


@dataclass(frozen=True)
class UseBackendRule(IRNode):
    """Use backend rule."""

    backend: str = ""
    condition: str | None = None


@dataclass(frozen=True)
class Frontend(IRNode):
    """Frontend section."""

    name: str = ""
    binds: list[Bind] = field(default_factory=list)
    mode: Mode = Mode.HTTP
    acls: list[ACL] = field(default_factory=list)
    http_request_rules: list[HttpRequestRule] = field(default_factory=list)
    http_response_rules: list[HttpResponseRule] = field(default_factory=list)
    use_backend_rules: list[UseBackendRule] = field(default_factory=list)
    default_backend: str | None = None
    options: list[str] = field(default_factory=list)
    timeout_client: str | None = None
    maxconn: int | None = None


@dataclass(frozen=True)
class Backend(IRNode):
    """Backend section."""

    name: str = ""
    mode: Mode = Mode.HTTP
    balance: BalanceAlgorithm = BalanceAlgorithm.ROUNDROBIN
    servers: list[Server] = field(default_factory=list)
    server_templates: list[ServerTemplate] = field(default_factory=list)
    health_check: HealthCheck | None = None
    options: list[str] = field(default_factory=list)
    http_request_rules: list[HttpRequestRule] = field(default_factory=list)
    http_response_rules: list[HttpResponseRule] = field(default_factory=list)
    compression: CompressionConfig | None = None
    cookie: str | None = None
    timeout_server: str | None = None
    timeout_connect: str | None = None
    timeout_check: str | None = None
    retries: int | None = None


@dataclass(frozen=True)
class Listen(IRNode):
    """Listen section (combined frontend/backend)."""

    name: str = ""
    binds: list[Bind] = field(default_factory=list)
    mode: Mode = Mode.HTTP
    balance: BalanceAlgorithm = BalanceAlgorithm.ROUNDROBIN
    servers: list[Server] = field(default_factory=list)
    acls: list[ACL] = field(default_factory=list)
    options: list[str] = field(default_factory=list)


# DSL-specific IR nodes (for advanced features)
@dataclass(frozen=True)
class Variable(IRNode):
    """Variable definition (let x = ...)."""

    name: str = ""
    value: Any = None
    type_hint: str | None = None


@dataclass(frozen=True)
class Template(IRNode):
    """Template definition for reuse."""

    name: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    applies_to: str = ""  # "server", "backend", "frontend", etc.


@dataclass(frozen=True)
class FunctionCall(IRNode):
    """Function call (for DSL functions)."""

    function_name: str = ""
    arguments: list[Any] = field(default_factory=list)
    keyword_arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IfBlock(IRNode):
    """Conditional block (if/else)."""

    condition: str = ""
    then_config: Optional["ConfigIR"] = None
    else_config: Optional["ConfigIR"] = None


@dataclass(frozen=True)
class ForLoop(IRNode):
    """For loop for generating config."""

    variable: str = ""
    iterable: Any = None  # range, list, etc.
    body: list[Any] = field(default_factory=list)  # List of config items to generate


# Top-level configuration
@dataclass(frozen=True)
class ConfigIR(IRNode):
    """Complete HAProxy configuration in IR form."""

    version: str = "2.0"
    name: str = "haproxy_config"
    global_config: GlobalConfig | None = None
    defaults: DefaultsConfig | None = None
    frontends: list[Frontend] = field(default_factory=list)
    backends: list[Backend] = field(default_factory=list)
    listens: list[Listen] = field(default_factory=list)

    # DSL-specific features
    variables: dict[str, Variable] = field(default_factory=dict)
    templates: dict[str, Template] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)
