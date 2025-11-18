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
    LuaScript,
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
        resolved_lua_scripts = [self._resolve_lua_script(script) for script in self.config.lua_scripts]

        return replace(
            self.config,
            variables=resolved_variables,
            global_config=resolved_global,
            defaults=resolved_defaults,
            frontends=resolved_frontends,
            backends=resolved_backends,
            listens=resolved_listens,
            lua_scripts=resolved_lua_scripts,
        )

    def _resolve_variable_values(self) -> dict[str, Variable]:
        """Resolve env() calls and variable references in variable values.

        Performs multiple passes to resolve nested variable references.
        For example: port=8080, addr="10.0.1.1:${port}" -> addr="10.0.1.1:8080"
        """
        # Start with original variables
        resolved = dict(self.variables)

        # Keep resolving until no more changes occur (max 10 passes to prevent infinite loops)
        max_passes = 10
        for _ in range(max_passes):
            changed = False
            new_resolved = {}

            for name, var in resolved.items():
                # Temporarily update self.variables to use partially resolved values
                old_variables = self.variables
                self.variables = resolved

                try:
                    resolved_value = self._resolve_value(var.value)
                    new_resolved[name] = replace(var, value=resolved_value)

                    # Check if value changed
                    if resolved_value != var.value:
                        changed = True
                finally:
                    self.variables = old_variables

            resolved = new_resolved

            # If nothing changed, we're done
            if not changed:
                break

        # Update self.variables with final resolved values for use in config resolution
        self.variables = resolved
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
        # Resolve Lua scripts in global config
        resolved_lua_scripts = []
        if global_config.lua_scripts:
            resolved_lua_scripts = [self._resolve_lua_script(script) for script in global_config.lua_scripts]

        return replace(global_config, lua_scripts=resolved_lua_scripts)

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

        # Resolve port if it's a string with variable reference
        resolved_port = server.port
        if isinstance(server.port, str):
            resolved_port_str = self._resolve_value(server.port)
            # Try to convert to int if possible
            try:
                resolved_port = int(resolved_port_str)
            except ValueError:
                # Keep as string if not a valid integer
                resolved_port = resolved_port_str

        # Resolve ALPN list (may contain variable references)
        resolved_alpn = self._resolve_value(server.alpn) if server.alpn else []

        # Resolve other server options that may contain variables
        resolved_sni = self._resolve_value(server.sni) if server.sni else None
        resolved_source = self._resolve_value(server.source) if server.source else None
        resolved_ca_file = self._resolve_value(server.ca_file) if server.ca_file else None
        resolved_crt = self._resolve_value(server.crt) if server.crt else None

        return replace(
            server,
            address=resolved_address,
            port=resolved_port,
            ssl_verify=resolved_ssl_verify,
            alpn=resolved_alpn,
            sni=resolved_sni,
            source=resolved_source,
            ca_file=resolved_ca_file,
            crt=resolved_crt,
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

    def _resolve_lua_script(self, script: "LuaScript") -> "LuaScript":
        """Resolve variables in Lua script."""
        # Do NOT resolve content - it may contain Lua template parameters like ${user}
        # which should be preserved for Lua manager interpolation
        # Only resolve if it's a file path (source_type == "file")
        resolved_content = script.content
        if script.source_type == "file" and script.content:
            resolved_content = self._resolve_value(script.content)

        # Resolve parameters (template parameters might reference config variables)
        resolved_parameters = {
            key: self._resolve_value(value)
            for key, value in script.parameters.items()
        }

        return replace(
            script,
            content=resolved_content,
            parameters=resolved_parameters,
        )


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
