"""Semantic validation for HAProxy configuration."""

from typing import Any

from ..ir.nodes import Backend, ConfigIR, Frontend, Mode
from ..utils.errors import ValidationError


class SemanticValidator:
    """Validates semantic correctness of HAProxy configuration."""

    def __init__(self, config: ConfigIR):
        self.config = config
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> ConfigIR:
        """Validate the configuration and return it if valid."""
        self.errors = []
        self.warnings = []

        # Collect all backend names for reference validation
        backend_names = {backend.name for backend in self.config.backends}

        # Collect all ACL names
        acl_names = self._collect_acl_names()

        # Validate frontends
        for frontend in self.config.frontends:
            self._validate_frontend(frontend, backend_names, acl_names)

        # Validate backends
        for backend in self.config.backends:
            self._validate_backend(backend)

        # Raise error if any validation errors occurred
        if self.errors:
            error_msg = "\n".join(self.errors)
            raise ValidationError(f"Semantic validation failed:\n{error_msg}")

        return self.config

    def _collect_acl_names(self) -> set[str]:
        """Collect all ACL names from the configuration."""
        acl_names = set()

        # Frontend ACLs
        for frontend in self.config.frontends:
            for acl in frontend.acls:
                acl_names.add(acl.name)

        # Listen ACLs
        for listen in self.config.listens:
            for acl in listen.acls:
                acl_names.add(acl.name)

        return acl_names

    def _validate_frontend(
        self, frontend: Frontend, backend_names: set[str], acl_names: set[str]
    ) -> None:
        """Validate a frontend section."""
        # Validate default_backend reference
        if frontend.default_backend and frontend.default_backend not in backend_names:
            self.errors.append(
                f"Frontend '{frontend.name}': "
                f"default_backend '{frontend.default_backend}' does not exist"
            )

        # Validate use_backend rules
        for rule in frontend.use_backend_rules:
            if rule.backend not in backend_names:
                self.errors.append(
                    f"Frontend '{frontend.name}': "
                    f"use_backend references non-existent backend '{rule.backend}'"
                )

            # Validate ACL reference in condition
            if rule.condition and rule.condition not in acl_names:
                self.warnings.append(
                    f"Frontend '{frontend.name}': "
                    f"use_backend rule references undefined ACL '{rule.condition}'"
                )

        # Validate mode-specific options
        self._validate_mode_options(frontend.mode, frontend.options, f"Frontend '{frontend.name}'")

        # Check for binds
        if not frontend.binds:
            self.warnings.append(f"Frontend '{frontend.name}': no bind directives defined")

    def _validate_backend(self, backend: Backend) -> None:
        """Validate a backend section."""
        # Validate mode-specific options
        self._validate_mode_options(backend.mode, backend.options, f"Backend '{backend.name}'")

        # Validate servers
        if not backend.servers and not backend.server_templates:
            self.warnings.append(f"Backend '{backend.name}': no servers defined")

        # Validate server names are unique
        server_names = [server.name for server in backend.servers]
        duplicates = {name for name in server_names if server_names.count(name) > 1}
        if duplicates:
            self.errors.append(
                f"Backend '{backend.name}': duplicate server names: {', '.join(sorted(duplicates))}"
            )

        # Validate health check
        if backend.health_check:
            self._validate_health_check(backend.health_check, f"Backend '{backend.name}'")

    def _validate_mode_options(self, mode: Mode, options: list[str], context: str) -> None:
        """Validate that options are compatible with the mode."""
        http_only_options = {
            "httplog",
            "http-server-close",
            "http-keep-alive",
            "forwardfor",
            "httpchk",
        }

        tcp_only_options = {
            "tcplog",
            "tcp-check",
        }

        for option in options:
            if mode == Mode.TCP and option in http_only_options:
                self.errors.append(f"{context}: HTTP option '{option}' used in TCP mode")
            elif mode == Mode.HTTP and option in tcp_only_options:
                self.warnings.append(f"{context}: TCP option '{option}' used in HTTP mode")

    def _validate_health_check(self, health_check: Any, context: str) -> None:
        """Validate health check configuration."""
        # Validate method
        valid_methods = {"GET", "POST", "HEAD", "OPTIONS", "PUT", "DELETE", "PATCH"}
        if health_check.method and health_check.method.upper() not in valid_methods:
            self.errors.append(f"{context}: invalid health check method '{health_check.method}'")

        # Validate URI is present for HTTP checks
        if health_check.method and not health_check.uri:
            self.warnings.append(f"{context}: health check has method but no URI")

        # Validate expect status is valid
        if health_check.expect_status:
            status = health_check.expect_status
            if not (100 <= status <= 599):
                self.errors.append(
                    f"{context}: invalid health check expect status {status} (must be 100-599)"
                )
