"""Template expansion transformer - expands @template spreads into server properties."""

from dataclasses import replace
from typing import Any

from ..ir.nodes import Backend, ConfigIR, Server


class TemplateExpander:
    """Expands template spreads in server definitions."""

    def __init__(self, config: ConfigIR):
        self.config = config
        self.templates = config.templates

    def expand(self) -> ConfigIR:
        """Expand all template spreads in the configuration."""
        # Process each backend's servers
        expanded_backends = [self._expand_backend(backend) for backend in self.config.backends]

        return replace(
            self.config,
            backends=expanded_backends,
        )

    def _expand_backend(self, backend: Backend) -> Backend:
        """Expand template spreads in a backend's servers."""
        expanded_servers = [self._expand_server(server) for server in backend.servers]
        return replace(backend, servers=expanded_servers)

    def _expand_server(self, server: Server) -> Server:
        """Expand template spreads in a server definition."""
        # Check if server has template spreads in metadata
        if "template_spreads" not in server.metadata:
            return server

        # Get list of template names to apply
        template_names = server.metadata["template_spreads"]
        if not isinstance(template_names, list):
            template_names = [template_names]

        # Apply each template in order
        server_dict = self._server_to_dict(server)

        for template_name in template_names:
            if template_name not in self.templates:
                # Template not found - skip or raise error
                continue

            template = self.templates[template_name]
            # Apply template parameters, but don't override explicit server properties
            for key, value in template.parameters.items():
                # Map template parameter names to server field names
                field_name = self._map_param_to_field(key)
                if field_name and field_name not in server_dict:
                    server_dict[field_name] = value

        # Create new server with expanded properties
        return replace(server, **server_dict)

    def _server_to_dict(self, server: Server) -> dict[str, Any]:
        """Extract explicit (non-default) server properties to a dict."""
        # Only include properties that were explicitly set (not defaults)
        props: dict[str, Any] = {}

        # Check each field - only include if different from default
        if server.address:
            props["address"] = server.address
        if server.port != 8080:
            props["port"] = server.port
        if server.check is not False:
            props["check"] = server.check
        if server.check_interval is not None:
            props["check_interval"] = server.check_interval
        if server.rise != 2:
            props["rise"] = server.rise
        if server.fall != 3:
            props["fall"] = server.fall
        if server.weight != 1:
            props["weight"] = server.weight
        if server.maxconn is not None:
            props["maxconn"] = server.maxconn
        if server.ssl is not False:
            props["ssl"] = server.ssl
        if server.ssl_verify is not None:
            props["ssl_verify"] = server.ssl_verify
        if server.backup is not False:
            props["backup"] = server.backup

        return props

    def _map_param_to_field(self, param_name: str) -> str | None:
        """Map template parameter names to Server field names."""
        # Most parameters map directly
        mapping = {
            "address": "address",
            "port": "port",
            "check": "check",
            "inter": "check_interval",
            "rise": "rise",
            "fall": "fall",
            "weight": "weight",
            "maxconn": "maxconn",
            "ssl": "ssl",
            "verify": "ssl_verify",
            "backup": "backup",
        }
        return mapping.get(param_name)
