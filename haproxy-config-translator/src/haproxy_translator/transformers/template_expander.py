"""Template expansion transformer - expands @template spreads into properties."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ..ir.nodes import BalanceAlgorithm, Mode

if TYPE_CHECKING:
    from ..ir.nodes import ACL, Backend, ConfigIR, Frontend, HealthCheck, Listen, Server


class TemplateExpander:
    """Expands template spreads in server, health check, and ACL definitions."""

    def __init__(self, config: ConfigIR):
        self.config = config
        self.templates = config.templates

    def expand(self) -> ConfigIR:
        """Expand all template spreads in the configuration."""
        # Process each backend's servers, health checks, and ACLs
        expanded_backends = [self._expand_backend(backend) for backend in self.config.backends]

        # Process each frontend's ACLs
        expanded_frontends = [self._expand_frontend(frontend) for frontend in self.config.frontends]

        # Process each listen section
        expanded_listens = [self._expand_listen(listen) for listen in self.config.listens]

        return replace(
            self.config,
            backends=expanded_backends,
            frontends=expanded_frontends,
            listens=expanded_listens,
        )

    def _expand_frontend(self, frontend: Frontend) -> Frontend:
        """Expand template spreads in a frontend's ACLs."""
        expanded_acls = [self._expand_acl(acl) for acl in frontend.acls]
        return replace(frontend, acls=expanded_acls)

    def _expand_listen(self, listen: Listen) -> Listen:
        """Expand template spreads in a listen section."""
        expanded_servers = [self._expand_server(server) for server in listen.servers]
        expanded_acls = [self._expand_acl(acl) for acl in listen.acls]
        expanded_health_check = (
            self._expand_health_check(listen.health_check) if listen.health_check else None
        )

        return replace(
            listen,
            servers=expanded_servers,
            acls=expanded_acls,
            health_check=expanded_health_check,
        )

    def _expand_backend(self, backend: Backend) -> Backend:
        """Expand template spreads in a backend's servers, health check, ACLs, and backend-level properties."""
        # First expand child elements
        expanded_servers = [self._expand_server(server) for server in backend.servers]
        expanded_acls = [self._expand_acl(acl) for acl in backend.acls]
        expanded_health_check = (
            self._expand_health_check(backend.health_check) if backend.health_check else None
        )

        # Check if backend has template spreads
        if "template_spreads" not in backend.metadata:
            return replace(
                backend,
                servers=expanded_servers,
                acls=expanded_acls,
                health_check=expanded_health_check,
            )

        # Get list of template names to apply
        template_names = backend.metadata["template_spreads"]
        if not isinstance(template_names, list):
            template_names = [template_names]

        # Extract explicit properties from the backend
        backend_dict = self._backend_to_dict(backend)

        for template_name in template_names:
            if template_name not in self.templates:
                continue

            template = self.templates[template_name]
            # Apply template parameters, but don't override explicit properties
            for key, value in template.parameters.items():
                field_name = self._map_backend_param_to_field(key)
                if field_name and field_name not in backend_dict:
                    # Convert string values to appropriate types
                    converted_value = self._convert_backend_value(field_name, value)
                    backend_dict[field_name] = converted_value

        # Create new backend with expanded properties
        return replace(
            backend,
            servers=expanded_servers,
            acls=expanded_acls,
            health_check=expanded_health_check,
            **backend_dict,
        )

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
                field_name = self._map_server_param_to_field(key)
                if field_name and field_name not in server_dict:
                    server_dict[field_name] = value

        # Create new server with expanded properties
        return replace(server, **server_dict)

    def _expand_health_check(self, health_check: HealthCheck) -> HealthCheck:
        """Expand template spreads in a health check definition."""
        # Check if health check has template spreads in metadata
        if "template_spreads" not in health_check.metadata:
            return health_check

        # Get list of template names to apply
        template_names = health_check.metadata["template_spreads"]
        if not isinstance(template_names, list):
            template_names = [template_names]

        # Extract explicit properties from the health check
        hc_dict = self._health_check_to_dict(health_check)

        for template_name in template_names:
            if template_name not in self.templates:
                continue

            template = self.templates[template_name]
            # Apply template parameters, but don't override explicit properties
            for key, value in template.parameters.items():
                field_name = self._map_health_check_param_to_field(key)
                if field_name and field_name not in hc_dict:
                    hc_dict[field_name] = value

        # Create new health check with expanded properties
        return replace(health_check, **hc_dict)

    def _expand_acl(self, acl: ACL) -> ACL:
        """Expand template spreads in an ACL definition."""
        # Check if ACL has template spreads in metadata
        if "template_spreads" not in acl.metadata:
            return acl

        # Get list of template names to apply
        template_names = acl.metadata["template_spreads"]
        if not isinstance(template_names, list):
            template_names = [template_names]

        # Extract explicit properties from the ACL
        acl_dict = self._acl_to_dict(acl)

        for template_name in template_names:
            if template_name not in self.templates:
                continue

            template = self.templates[template_name]
            # Apply template parameters, but don't override explicit properties
            for key, value in template.parameters.items():
                field_name = self._map_acl_param_to_field(key)
                if field_name and field_name not in acl_dict:
                    acl_dict[field_name] = value

        # Create new ACL with expanded properties
        return replace(acl, **acl_dict)

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

    def _health_check_to_dict(self, hc: HealthCheck) -> dict[str, Any]:
        """Extract explicit (non-default) health check properties to a dict."""
        props: dict[str, Any] = {}

        # Only include properties that differ from defaults
        if hc.method != "GET":
            props["method"] = hc.method
        if hc.uri != "/":
            props["uri"] = hc.uri
        if hc.expect_status is not None and hc.expect_status != 200:
            props["expect_status"] = hc.expect_status
        if hc.expect_string is not None:
            props["expect_string"] = hc.expect_string
        if hc.expect_rstatus is not None:
            props["expect_rstatus"] = hc.expect_rstatus
        if hc.expect_rstring is not None:
            props["expect_rstring"] = hc.expect_rstring
        if hc.expect_negate:
            props["expect_negate"] = hc.expect_negate
        if hc.headers:
            props["headers"] = hc.headers
        if hc.interval is not None:
            props["interval"] = hc.interval

        return props

    def _acl_to_dict(self, acl: ACL) -> dict[str, Any]:
        """Extract explicit (non-default) ACL properties to a dict."""
        props: dict[str, Any] = {}

        # Name should always be preserved
        if acl.name:
            props["name"] = acl.name
        if acl.criterion:
            props["criterion"] = acl.criterion
        if acl.flags:
            props["flags"] = acl.flags
        if acl.values:
            props["values"] = acl.values

        return props

    def _map_server_param_to_field(self, param_name: str) -> str | None:
        """Map template parameter names to Server field names."""
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

    def _map_health_check_param_to_field(self, param_name: str) -> str | None:
        """Map template parameter names to HealthCheck field names."""
        mapping = {
            "method": "method",
            "uri": "uri",
            "expect_status": "expect_status",
            "expect_string": "expect_string",
            "expect_rstatus": "expect_rstatus",
            "expect_rstring": "expect_rstring",
            "expect_negate": "expect_negate",
            "headers": "headers",
            "interval": "interval",
        }
        return mapping.get(param_name)

    def _map_acl_param_to_field(self, param_name: str) -> str | None:
        """Map template parameter names to ACL field names."""
        mapping = {
            "criterion": "criterion",
            "flags": "flags",
            "values": "values",
        }
        return mapping.get(param_name)

    def _backend_to_dict(self, backend: Backend) -> dict[str, Any]:
        """Extract explicit (non-default) backend properties to a dict."""
        props: dict[str, Any] = {}

        # Only include properties that differ from defaults
        if backend.mode != Mode.HTTP:
            props["mode"] = backend.mode
        if backend.balance != BalanceAlgorithm.ROUNDROBIN:
            props["balance"] = backend.balance
        if backend.options:
            props["options"] = backend.options
        if backend.cookie:
            props["cookie"] = backend.cookie
        if backend.retries is not None:
            props["retries"] = backend.retries
        if backend.maxconn is not None:
            props["maxconn"] = backend.maxconn
        if backend.timeout_server:
            props["timeout_server"] = backend.timeout_server
        if backend.timeout_connect:
            props["timeout_connect"] = backend.timeout_connect
        if backend.timeout_check:
            props["timeout_check"] = backend.timeout_check
        if backend.log_tag:
            props["log_tag"] = backend.log_tag

        return props

    def _map_backend_param_to_field(self, param_name: str) -> str | None:
        """Map template parameter names to Backend field names."""
        mapping = {
            "mode": "mode",
            "balance": "balance",
            "option": "options",
            "options": "options",
            "cookie": "cookie",
            "retries": "retries",
            "maxconn": "maxconn",
            "timeout_server": "timeout_server",
            "timeout_connect": "timeout_connect",
            "timeout_check": "timeout_check",
            "log_tag": "log_tag",
        }
        return mapping.get(param_name)

    def _convert_backend_value(self, field_name: str, value: Any) -> Any:
        """Convert template value to appropriate type for backend field."""
        # Define converters for specific field types
        converters: dict[str, type] = {
            "balance": BalanceAlgorithm,
            "mode": Mode,
        }
        numeric_fields = {"retries", "maxconn"}

        # Handle enum conversions
        if field_name in converters and isinstance(value, str):
            return converters[field_name](value)

        # Handle options as list
        if field_name == "options":
            return value if isinstance(value, list) else [value]

        # Handle numeric conversions
        if field_name in numeric_fields and isinstance(value, str):
            return int(value)

        return value
