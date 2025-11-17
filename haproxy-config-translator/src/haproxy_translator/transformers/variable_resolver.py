"""Variable resolution transformer - resolves variables and env() calls."""

import os
import re
from dataclasses import replace
from typing import Any

from ..ir.nodes import (
    ACL,
    Backend,
    Bind,
    ConfigIR,
    DefaultsConfig,
    Frontend,
    GlobalConfig,
    HealthCheck,
    Listen,
    Server,
    Variable,
)
from ..utils.errors import ParseError


class VariableResolver:
    """Resolves variable references and environment variables in the configuration."""

    def __init__(self, config: ConfigIR):
        self.config = config
        self.variables = config.variables
        # Pattern for ${var_name} in strings
        self.var_pattern = re.compile(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

    def resolve(self) -> ConfigIR:
        """Resolve all variables and env() calls in the configuration."""
        # First, resolve env() calls in variable values
        resolved_variables = self._resolve_variable_values()

        # Then substitute variable references throughout the config
        resolved_global = self._resolve_global(self.config.global_config) if self.config.global_config else None
        resolved_defaults = self._resolve_defaults(self.config.defaults) if self.config.defaults else None
        resolved_frontends = [self._resolve_frontend(f) for f in self.config.frontends]
        resolved_backends = [self._resolve_backend(b) for b in self.config.backends]
        resolved_listens = [self._resolve_listen(listen) for listen in self.config.listens]

        return replace(
            self.config,
            variables=resolved_variables,
            global_config=resolved_global,
            defaults=resolved_defaults,
            frontends=resolved_frontends,
            backends=resolved_backends,
            listens=resolved_listens,
        )

    def _resolve_variable_values(self) -> dict[str, Variable]:
        """Resolve env() calls and variable references in variable values."""
        resolved = {}
        for name, var in self.variables.items():
            resolved_value = self._resolve_value(var.value)
            resolved[name] = replace(var, value=resolved_value)
        return resolved

    def _resolve_value(self, value: Any) -> Any:
        """Resolve a single value (handles strings, numbers, bools, etc.)."""
        if isinstance(value, str):
            # Substitute ${var} references
            return self._substitute_variables(value)
        if isinstance(value, dict):
            # Recursively resolve dictionary values
            return {k: self._resolve_value(v) for k, v in value.items()}
        if isinstance(value, list):
            # Recursively resolve list items
            return [self._resolve_value(item) for item in value]
        # Numbers, booleans, None, etc. - return as-is
        return value

    def _substitute_variables(self, text: str) -> str:
        """Substitute ${var_name} references in a string."""

        def replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            if var_name in self.variables:
                var_value = self.variables[var_name].value
                # Convert value to string
                if isinstance(var_value, bool):
                    return "true" if var_value else "false"
                return str(var_value)
            # Leave unresolved variables as-is (or raise error)
            raise ParseError(f"Undefined variable: {var_name}")

        return self.var_pattern.sub(replacer, text)

    def _resolve_global(self, global_config: GlobalConfig) -> GlobalConfig:
        """Resolve variables in global config."""
        # For now, global config doesn't need variable resolution
        # Most fields are primitives or fixed values
        return global_config

    def _resolve_defaults(self, defaults: DefaultsConfig) -> DefaultsConfig:
        """Resolve variables in defaults config."""
        # Resolve log if it's a string
        resolved_log = self._resolve_value(defaults.log) if isinstance(defaults.log, str) else defaults.log
        return replace(defaults, log=resolved_log)

    def _resolve_frontend(self, frontend: Frontend) -> Frontend:
        """Resolve variables in frontend."""
        # Resolve bind addresses
        resolved_binds = [self._resolve_bind(b) for b in frontend.binds]

        # Resolve default_backend if it's a variable reference
        resolved_default_backend = (
            self._resolve_value(frontend.default_backend)
            if frontend.default_backend
            else None
        )

        # Resolve ACLs
        resolved_acls = [self._resolve_acl(acl) for acl in frontend.acls]

        return replace(
            frontend,
            binds=resolved_binds,
            default_backend=resolved_default_backend,
            acls=resolved_acls,
        )

    def _resolve_backend(self, backend: Backend) -> Backend:
        """Resolve variables in backend."""
        # Resolve servers
        resolved_servers = [self._resolve_server(s) for s in backend.servers]

        # Resolve health check if present
        resolved_health_check = (
            self._resolve_health_check(backend.health_check)
            if backend.health_check
            else None
        )

        return replace(
            backend,
            servers=resolved_servers,
            health_check=resolved_health_check,
        )

    def _resolve_listen(self, listen: Listen) -> Listen:
        """Resolve variables in listen section."""
        # Resolve binds
        resolved_binds = [self._resolve_bind(b) for b in listen.binds]

        # Resolve servers
        resolved_servers = [self._resolve_server(s) for s in listen.servers]

        return replace(
            listen,
            binds=resolved_binds,
            servers=resolved_servers,
        )

    def _resolve_bind(self, bind: Bind) -> Bind:
        """Resolve variables in bind directive."""
        resolved_address = self._resolve_value(bind.address)
        resolved_ssl_cert = self._resolve_value(bind.ssl_cert) if bind.ssl_cert else None
        return replace(bind, address=resolved_address, ssl_cert=resolved_ssl_cert)

    def _resolve_server(self, server: Server) -> Server:
        """Resolve variables in server."""
        resolved_address = self._resolve_value(server.address)
        resolved_ssl_verify = (
            self._resolve_value(server.ssl_verify) if server.ssl_verify else None
        )
        return replace(
            server,
            address=resolved_address,
            ssl_verify=resolved_ssl_verify,
        )

    def _resolve_acl(self, acl: ACL) -> ACL:
        """Resolve variables in ACL."""
        resolved_criterion = self._resolve_value(acl.criterion)
        resolved_values = [self._resolve_value(v) for v in acl.values]
        return replace(acl, criterion=resolved_criterion, values=resolved_values)

    def _resolve_health_check(self, health_check: HealthCheck) -> HealthCheck:
        """Resolve variables in health check."""
        resolved_uri = str(self._resolve_value(health_check.uri))
        return replace(health_check, uri=resolved_uri)


def resolve_env_variable(var_name: str, default: Any = None) -> Any:
    """Resolve an environment variable.

    Args:
        var_name: Name of the environment variable
        default: Default value if variable is not set

    Returns:
        Value of the environment variable or default
    """
    value = os.environ.get(var_name)
    if value is None:
        if default is not None:
            return default
        raise ParseError(f"Environment variable not set: {var_name}")
    return value
