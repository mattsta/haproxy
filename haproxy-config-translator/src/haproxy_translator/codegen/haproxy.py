"""HAProxy native configuration code generator."""

from typing import Optional
from pathlib import Path

from ..ir.nodes import *
from ..utils.errors import CodeGenerationError


class HAProxyCodeGenerator:
    """Generate native HAProxy configuration from IR."""

    def __init__(self, indent: str = "    "):
        self.indent_str = indent
        self.lua_files: list[str] = []

    def generate(self, ir: ConfigIR, output_path: Optional[Path] = None) -> str:
        """
        Generate complete HAProxy configuration.

        Args:
            ir: Configuration IR
            output_path: Optional output file path

        Returns:
            Generated configuration as string
        """
        lines = []

        # Header comment
        lines.append(f"# Generated HAProxy configuration: {ir.name}")
        lines.append(f"# Version: {ir.version}")
        lines.append("")

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

        # Generate listens
        for listen in ir.listens:
            lines.extend(self._generate_listen(listen))
            lines.append("")

        config = "\n".join(lines)

        # Write to file if output_path specified
        if output_path:
            output_path.write_text(config, encoding="utf-8")

        return config

    def _generate_global(self, global_config: GlobalConfig) -> list[str]:
        """Generate global section."""
        lines = ["global"]

        if global_config.daemon:
            lines.append(self._indent("daemon"))

        lines.append(self._indent(f"maxconn {global_config.maxconn}"))

        if global_config.user:
            lines.append(self._indent(f"user {global_config.user}"))

        if global_config.group:
            lines.append(self._indent(f"group {global_config.group}"))

        if global_config.chroot:
            lines.append(self._indent(f"chroot {global_config.chroot}"))

        if global_config.pidfile:
            lines.append(self._indent(f"pidfile {global_config.pidfile}"))

        # Log targets
        for log in global_config.log_targets:
            log_line = f"log {log.address} {log.facility.value} {log.level.value}"
            if log.minlevel:
                log_line += f" {log.minlevel.value}"
            lines.append(self._indent(log_line))

        # SSL configuration
        if global_config.ssl_default_bind_ciphers:
            lines.append(
                self._indent(f"ssl-default-bind-ciphers {global_config.ssl_default_bind_ciphers}")
            )

        for option in global_config.ssl_default_bind_options:
            lines.append(self._indent(f"ssl-default-bind-options {option}"))

        # Lua scripts
        for script in global_config.lua_scripts:
            if script.source_type == "file":
                lines.append(self._indent(f"lua-load {script.content}"))
                self.lua_files.append(script.content)

        # Stats
        if global_config.stats and global_config.stats.enable:
            lines.append(self._indent(f"stats socket /var/run/haproxy.sock mode 660 level admin"))

        # Tuning
        for key, value in global_config.tuning.items():
            lines.append(self._indent(f"{key} {value}"))

        return lines

    def _generate_defaults(self, defaults: DefaultsConfig) -> list[str]:
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

        if defaults.timeout_check:
            lines.append(self._indent(f"timeout check {defaults.timeout_check}"))

        if defaults.timeout_queue:
            lines.append(self._indent(f"timeout queue {defaults.timeout_queue}"))

        # Options
        for option in defaults.options:
            lines.append(self._indent(f"option {option}"))

        # Error files
        for code, file in defaults.errorfiles.items():
            lines.append(self._indent(f"errorfile {code} {file}"))

        # HTTP check
        if defaults.http_check:
            lines.extend(self._generate_http_check(defaults.http_check, indent=True))

        return lines

    def _generate_frontend(self, frontend: Frontend) -> list[str]:
        """Generate frontend section."""
        lines = [f"frontend {frontend.name}"]

        # Bind directives
        for bind in frontend.binds:
            lines.append(self._indent(self._format_bind(bind)))

        # Mode
        lines.append(self._indent(f"mode {frontend.mode.value}"))

        # Max connections
        if frontend.maxconn:
            lines.append(self._indent(f"maxconn {frontend.maxconn}"))

        # Timeout
        if frontend.timeout_client:
            lines.append(self._indent(f"timeout client {frontend.timeout_client}"))

        # ACLs
        for acl in frontend.acls:
            lines.append(self._indent(self._format_acl(acl)))

        # HTTP request rules
        for rule in frontend.http_request_rules:
            lines.append(self._indent(self._format_http_request_rule(rule)))

        # HTTP response rules
        for rule in frontend.http_response_rules:
            lines.append(self._indent(self._format_http_response_rule(rule)))

        # Use backend rules
        for rule in frontend.use_backend_rules:
            use_line = f"use_backend {rule.backend}"
            if rule.condition:
                use_line += f" if {rule.condition}"
            lines.append(self._indent(use_line))

        # Default backend
        if frontend.default_backend:
            lines.append(self._indent(f"default_backend {frontend.default_backend}"))

        # Options
        for option in frontend.options:
            lines.append(self._indent(f"option {option}"))

        return lines

    def _generate_backend(self, backend: Backend) -> list[str]:
        """Generate backend section."""
        lines = [f"backend {backend.name}"]

        # Mode
        lines.append(self._indent(f"mode {backend.mode.value}"))

        # Balance algorithm
        lines.append(self._indent(f"balance {backend.balance.value}"))

        # Retries
        if backend.retries is not None:
            lines.append(self._indent(f"retries {backend.retries}"))

        # Timeouts
        if backend.timeout_connect:
            lines.append(self._indent(f"timeout connect {backend.timeout_connect}"))

        if backend.timeout_server:
            lines.append(self._indent(f"timeout server {backend.timeout_server}"))

        if backend.timeout_check:
            lines.append(self._indent(f"timeout check {backend.timeout_check}"))

        # Options
        for option in backend.options:
            lines.append(self._indent(f"option {option}"))

        # Cookie
        if backend.cookie:
            lines.append(self._indent(f"cookie {backend.cookie}"))

        # Health check
        if backend.health_check:
            lines.extend(self._generate_http_check(backend.health_check, indent=True))

        # HTTP request rules
        for rule in backend.http_request_rules:
            lines.append(self._indent(self._format_http_request_rule(rule)))

        # HTTP response rules
        for rule in backend.http_response_rules:
            lines.append(self._indent(self._format_http_response_rule(rule)))

        # Compression
        if backend.compression:
            lines.append(self._indent(f"compression algo {backend.compression.algo}"))
            if backend.compression.types:
                types_str = " ".join(backend.compression.types)
                lines.append(self._indent(f"compression type {types_str}"))

        # Servers
        for server in backend.servers:
            lines.append(self._indent(self._format_server(server)))

        # Server templates
        for template in backend.server_templates:
            lines.append(self._indent(self._format_server_template(template)))

        return lines

    def _generate_listen(self, listen: Listen) -> list[str]:
        """Generate listen section (combined frontend/backend)."""
        lines = [f"listen {listen.name}"]

        # Bind directives
        for bind in listen.binds:
            lines.append(self._indent(self._format_bind(bind)))

        # Mode
        lines.append(self._indent(f"mode {listen.mode.value}"))

        # Balance
        lines.append(self._indent(f"balance {listen.balance.value}"))

        # ACLs
        for acl in listen.acls:
            lines.append(self._indent(self._format_acl(acl)))

        # Options
        for option in listen.options:
            lines.append(self._indent(f"option {option}"))

        # Servers
        for server in listen.servers:
            lines.append(self._indent(self._format_server(server)))

        return lines

    def _generate_http_check(self, health_check: HealthCheck, indent: bool = False) -> list[str]:
        """Generate HTTP health check directives."""
        lines = []
        ind = self._indent if indent else lambda x: x

        check_line = f"http-check send meth {health_check.method} uri {health_check.uri}"

        # Add headers
        for name, value in health_check.headers.items():
            check_line += f' hdr {name} "{value}"'

        lines.append(ind(check_line))

        # Expect
        if health_check.expect_status:
            lines.append(ind(f"http-check expect status {health_check.expect_status}"))
        elif health_check.expect_string:
            lines.append(ind(f"http-check expect string {health_check.expect_string}"))

        return lines

    def _format_bind(self, bind: Bind) -> str:
        """Format bind directive."""
        parts = [f"bind {bind.address}"]

        if bind.ssl:
            parts.append("ssl")
            if bind.ssl_cert:
                parts.append(f"crt {bind.ssl_cert}")
            if bind.alpn:
                parts.append(f"alpn {','.join(bind.alpn)}")

        for key, value in bind.options.items():
            if isinstance(value, bool) and value:
                parts.append(key)
            elif value:
                parts.append(f"{key} {value}")

        return " ".join(parts)

    def _format_acl(self, acl: ACL) -> str:
        """Format ACL definition."""
        parts = [f"acl {acl.name} {acl.criterion}"]

        if acl.flags:
            parts.extend(acl.flags)

        if acl.values:
            parts.extend(acl.values)

        return " ".join(parts)

    def _format_http_request_rule(self, rule: HttpRequestRule) -> str:
        """Format HTTP request rule."""
        parts = [f"http-request {rule.action}"]

        for key, value in rule.parameters.items():
            if key in ["header", "name"]:
                parts.append(value)
            elif key == "status":
                parts.append(f"status {value}")
            elif key == "deny_status":
                parts.append(f"deny status {value}")
            elif isinstance(value, str) and " " in value:
                parts.append(f'{key} "{value}"')
            else:
                parts.append(f"{key} {value}")

        if rule.condition:
            parts.append(f"if {rule.condition}")

        return " ".join(parts)

    def _format_http_response_rule(self, rule: HttpResponseRule) -> str:
        """Format HTTP response rule."""
        parts = [f"http-response {rule.action}"]

        for key, value in rule.parameters.items():
            if isinstance(value, str) and " " in value:
                parts.append(f'{key} "{value}"')
            else:
                parts.append(f"{key} {value}")

        if rule.condition:
            parts.append(f"if {rule.condition}")

        return " ".join(parts)

    def _format_server(self, server: Server) -> str:
        """Format server definition."""
        parts = [f"server {server.name} {server.address}:{server.port}"]

        if server.check:
            parts.append("check")
            if server.check_interval:
                parts.append(f"inter {server.check_interval}")
            parts.append(f"rise {server.rise}")
            parts.append(f"fall {server.fall}")

        if server.weight != 1:
            parts.append(f"weight {server.weight}")

        if server.maxconn:
            parts.append(f"maxconn {server.maxconn}")

        if server.ssl:
            parts.append("ssl")
            if server.ssl_verify:
                parts.append(f"verify {server.ssl_verify}")

        if server.backup:
            parts.append("backup")

        if server.disabled:
            parts.append("disabled")

        if server.send_proxy:
            parts.append("send-proxy")

        for key, value in server.options.items():
            if isinstance(value, bool) and value:
                parts.append(key)
            elif value:
                parts.append(f"{key} {value}")

        return " ".join(parts)

    def _format_server_template(self, template: ServerTemplate) -> str:
        """Format server template."""
        base = template.base_server
        parts = [
            f"server-template {template.prefix} {template.count}",
            f"{template.fqdn_pattern}:{template.port}",
        ]

        if base.check:
            parts.append("check")
            if base.check_interval:
                parts.append(f"inter {base.check_interval}")
            parts.append(f"rise {base.rise}")
            parts.append(f"fall {base.fall}")

        if base.weight != 1:
            parts.append(f"weight {base.weight}")

        if base.maxconn:
            parts.append(f"maxconn {base.maxconn}")

        if base.ssl:
            parts.append("ssl")
            if base.ssl_verify:
                parts.append(f"verify {base.ssl_verify}")

        return " ".join(parts)

    def _indent(self, line: str) -> str:
        """Add indentation to line."""
        return self.indent_str + line

    def get_lua_files(self) -> list[str]:
        """Get list of Lua files referenced in configuration."""
        return self.lua_files
