"""Security validation for HAProxy configuration.

This module provides security-focused validation for HAProxy configurations,
checking for common security issues and misconfigurations.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from re import Pattern
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from ..ir.nodes import Bind, ConfigIR, StatsConfig


class SecurityLevel(Enum):
    """Security issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityIssue:
    """Represents a security issue found during validation."""

    level: SecurityLevel
    message: str
    location: str
    recommendation: str


@dataclass
class SecurityReport:
    """Results of security validation."""

    issues: list[SecurityIssue] = field(default_factory=list)
    passed: bool = True

    def add_issue(self, issue: SecurityIssue) -> None:
        """Add an issue to the report."""
        self.issues.append(issue)
        if issue.level in (SecurityLevel.CRITICAL, SecurityLevel.HIGH):
            self.passed = False


class SecurityValidator:
    """Validates security aspects of HAProxy configuration.

    Checks for:
    - Hardcoded credentials and secrets
    - Path traversal vulnerabilities
    - Dangerous resource limits
    - Insecure SSL/TLS configuration
    - Exposed management interfaces
    - Unsafe options and directives
    """

    # Patterns that might indicate hardcoded secrets
    SECRET_PATTERNS: ClassVar[list[tuple[Pattern[str], str]]] = [
        (re.compile(r"password\s*[:=]\s*['\"]?[^'\"]+['\"]?", re.I), "password"),
        (re.compile(r"secret\s*[:=]\s*['\"]?[^'\"]+['\"]?", re.I), "secret"),
        (re.compile(r"api[_-]?key\s*[:=]\s*['\"]?[^'\"]+['\"]?", re.I), "API key"),
        (re.compile(r"token\s*[:=]\s*['\"]?[^'\"]+['\"]?", re.I), "token"),
        (re.compile(r"auth\s*[:=]\s*['\"]?[^'\"]+['\"]?", re.I), "auth credential"),
    ]

    # Path patterns that might indicate traversal
    PATH_TRAVERSAL_PATTERN = re.compile(r"\.\./|\.\.\\")

    # Known insecure SSL options
    INSECURE_SSL_OPTIONS = frozenset(
        {
            "no-sslv3",  # This is actually good, but if missing it's bad
            "force-sslv3",
            "force-tlsv10",
            "force-tlsv11",
        }
    )

    # Weak ciphers
    WEAK_CIPHERS = frozenset(
        {
            "RC4",
            "DES",
            "3DES",
            "MD5",
            "NULL",
            "EXPORT",
            "ANON",
        }
    )

    def __init__(self, config: ConfigIR):
        self.config = config
        self.report = SecurityReport()

    def validate(self) -> SecurityReport:
        """Run all security validations and return a report."""
        self._check_global_security()
        self._check_frontend_security()
        self._check_backend_security()
        self._check_listen_security()
        self._check_resource_limits()

        return self.report

    def _check_global_security(self) -> None:
        """Check global section for security issues."""
        global_config = self.config.global_config
        if global_config is None:
            return

        # Check for insecure user/group
        if global_config.user == "root":
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.HIGH,
                    message="HAProxy running as root user",
                    location="global",
                    recommendation="Run HAProxy as a non-privileged user (e.g., 'haproxy')",
                )
            )

        # Check chroot
        if not global_config.chroot:
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.MEDIUM,
                    message="No chroot configured",
                    location="global",
                    recommendation="Configure chroot for additional isolation (e.g., /var/lib/haproxy)",
                )
            )
        elif self.PATH_TRAVERSAL_PATTERN.search(global_config.chroot):
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.CRITICAL,
                    message="Path traversal pattern in chroot path",
                    location="global.chroot",
                    recommendation="Use absolute paths without '..' sequences",
                )
            )

        # Check SSL settings
        if global_config.ssl_default_bind_ciphers:
            self._check_cipher_strength(
                global_config.ssl_default_bind_ciphers, "global.ssl-default-bind-ciphers"
            )

        if global_config.ssl_default_server_ciphers:
            self._check_cipher_strength(
                global_config.ssl_default_server_ciphers, "global.ssl-default-server-ciphers"
            )

        # Check stats socket security
        for socket in global_config.stats_sockets:
            socket_str = str(socket).lower()
            if (
                "admin" in socket_str
                and "level admin" in socket_str
                and "mode 600" not in socket_str
            ):
                self.report.add_issue(
                    SecurityIssue(
                        level=SecurityLevel.HIGH,
                        message="Stats socket with admin level may be world-accessible",
                        location="global.stats socket",
                        recommendation="Add 'mode 600' or 'mode 660' to restrict access",
                    )
                )

    def _check_frontend_security(self) -> None:
        """Check frontend sections for security issues."""
        for frontend in self.config.frontends:
            context = f"frontend '{frontend.name}'"

            # Check bind addresses
            for bind in frontend.binds:
                self._check_bind_security(bind, context)

            # Check for exposed stats
            if frontend.stats_config and frontend.stats_config.enable:
                self._check_stats_security(frontend.stats_config, context)

            # Check HTTP request rules for dangerous patterns
            for rule in frontend.http_request_rules:
                if rule.action in ("set-header", "set_header") and rule.parameters:
                    header_name = rule.parameters.get("name", "").lower()
                    if header_name in ("authorization", "x-api-key", "cookie"):
                        self.report.add_issue(
                            SecurityIssue(
                                level=SecurityLevel.MEDIUM,
                                message=f"Setting sensitive header '{header_name}' in rule",
                                location=f"{context}.http-request",
                                recommendation="Avoid hardcoding sensitive headers; use variables or secrets management",
                            )
                        )

    def _check_backend_security(self) -> None:
        """Check backend sections for security issues."""
        for backend in self.config.backends:
            context = f"backend '{backend.name}'"

            # Check server configurations
            for server in backend.servers:
                # Check for hardcoded credentials in server options
                secret_keywords = {"password", "secret", "api_key", "apikey", "token", "auth"}
                if server.options:
                    for key in server.options:
                        if key.lower() in secret_keywords:
                            self.report.add_issue(
                                SecurityIssue(
                                    level=SecurityLevel.CRITICAL,
                                    message=f"Possible hardcoded {key} in server configuration",
                                    location=f"{context}.server '{server.name}'",
                                    recommendation="Use environment variables or secrets management",
                                )
                            )

                # Check SSL options
                if server.ssl and not server.ssl_verify:
                    self.report.add_issue(
                        SecurityIssue(
                            level=SecurityLevel.MEDIUM,
                            message="SSL enabled without certificate verification",
                            location=f"{context}.server '{server.name}'",
                            recommendation="Add 'verify required' and specify ca-file",
                        )
                    )

    def _check_listen_security(self) -> None:
        """Check listen sections for security issues."""
        for listen in self.config.listens:
            context = f"listen '{listen.name}'"

            # Check bind addresses
            for bind in listen.binds:
                self._check_bind_security(bind, context)

            # Check for exposed stats
            if listen.stats and listen.stats.enable:
                self._check_stats_security(listen.stats, context)

    def _check_bind_security(self, bind: Bind, context: str) -> None:
        """Check bind directive for security issues."""
        address = bind.address

        # Check for wildcard binds on all interfaces
        if address.startswith("*:") or address.startswith("0.0.0.0:"):
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.INFO,
                    message=f"Bind on all interfaces: {address}",
                    location=f"{context}.bind",
                    recommendation="Consider binding to specific interfaces for better security",
                )
            )

        # Check for privileged ports without proper context
        port_match = re.search(r":(\d+)", address)
        if port_match:
            port = int(port_match.group(1))
            if port < 1024:
                self.report.add_issue(
                    SecurityIssue(
                        level=SecurityLevel.INFO,
                        message=f"Binding to privileged port {port}",
                        location=f"{context}.bind",
                        recommendation="Ensure HAProxy has appropriate capabilities or is started as root and drops privileges",
                    )
                )

        # Check SSL configuration
        if bind.ssl:
            if not bind.ssl_cert:
                self.report.add_issue(
                    SecurityIssue(
                        level=SecurityLevel.HIGH,
                        message="SSL enabled without certificate",
                        location=f"{context}.bind",
                        recommendation="Specify ssl certificate with 'crt' option",
                    )
                )

            # Check for weak SSL options
            ssl_options = bind.options
            for opt in self.INSECURE_SSL_OPTIONS:
                if opt in ssl_options:
                    self.report.add_issue(
                        SecurityIssue(
                            level=SecurityLevel.HIGH,
                            message=f"Insecure SSL option: {opt}",
                            location=f"{context}.bind",
                            recommendation="Use modern TLS versions (TLSv1.2+)",
                        )
                    )

    def _check_stats_security(self, stats_config: StatsConfig, context: str) -> None:
        """Check stats configuration for security issues."""
        # Check for missing authentication
        has_auth = bool(stats_config.auth)
        if not has_auth:
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.HIGH,
                    message="Stats page enabled without authentication",
                    location=f"{context}.stats",
                    recommendation="Add 'auth' with username:password for stats access",
                )
            )

        # Check for admin mode without authentication
        has_admin = bool(stats_config.admin_rules)
        if has_admin and not has_auth:
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.CRITICAL,
                    message="Stats admin mode enabled without authentication",
                    location=f"{context}.stats",
                    recommendation="Admin mode allows server manipulation; always require authentication",
                )
            )

        # Check for common/weak credentials (auth is a list of user:password pairs)
        if stats_config.auth:
            weak_creds = ["admin:admin", "admin:password", "stats:stats", "haproxy:haproxy"]
            for auth_entry in stats_config.auth:
                auth_lower = auth_entry.lower()
                for weak in weak_creds:
                    if weak in auth_lower:
                        self.report.add_issue(
                            SecurityIssue(
                                level=SecurityLevel.HIGH,
                                message="Weak/default credentials for stats authentication",
                                location=f"{context}.stats",
                                recommendation="Use strong, unique credentials for stats access",
                            )
                        )
                        break

    def _check_cipher_strength(self, ciphers: str, location: str) -> None:
        """Check cipher string for weak algorithms."""
        ciphers_upper = ciphers.upper()
        for weak in self.WEAK_CIPHERS:
            if weak in ciphers_upper and f"!{weak}" not in ciphers_upper:
                self.report.add_issue(
                    SecurityIssue(
                        level=SecurityLevel.HIGH,
                        message=f"Weak cipher algorithm enabled: {weak}",
                        location=location,
                        recommendation=f"Disable {weak} by adding '!{weak}' to cipher string",
                    )
                )

    def _check_resource_limits(self) -> None:
        """Check resource limits for potential issues."""
        global_config = self.config.global_config
        if global_config is None:
            return

        # Check maxconn limits
        maxconn = global_config.maxconn
        if maxconn is not None and isinstance(maxconn, int) and maxconn > 100000:
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.LOW,
                    message=f"Very high maxconn value: {global_config.maxconn}",
                    location="global.maxconn",
                    recommendation="Ensure system resources can handle this connection limit",
                )
            )

        # Check timeouts (from defaults section)
        defaults = self.config.defaults
        if defaults is None or not defaults.timeout_client:
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.MEDIUM,
                    message="No client timeout configured",
                    location="defaults",
                    recommendation="Configure timeout client to prevent resource exhaustion",
                )
            )

        if defaults is None or not defaults.timeout_server:
            self.report.add_issue(
                SecurityIssue(
                    level=SecurityLevel.MEDIUM,
                    message="No server timeout configured",
                    location="defaults",
                    recommendation="Configure timeout server to prevent hanging connections",
                )
            )
