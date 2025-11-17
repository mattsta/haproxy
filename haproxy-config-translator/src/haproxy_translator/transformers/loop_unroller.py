"""Loop unrolling transformer - expands for loops into server definitions."""

import re
from dataclasses import replace
from typing import Any

from ..ir.nodes import Backend, ConfigIR, ForLoop, Server
from ..utils.errors import ParseError


class LoopUnroller:
    """Expands for loops in server definitions."""

    def __init__(self, config: ConfigIR):
        self.config = config

    def unroll(self) -> ConfigIR:
        """Unroll all for loops in the configuration."""
        # Process each backend's servers
        expanded_backends = [self._unroll_backend(backend) for backend in self.config.backends]

        return replace(
            self.config,
            backends=expanded_backends,
        )

    def _unroll_backend(self, backend: Backend) -> Backend:
        """Unroll for loops in a backend's servers."""
        # Check if backend has loops in metadata
        if "server_loops" not in backend.metadata:
            return backend

        loops = backend.metadata["server_loops"]
        if not isinstance(loops, list):
            loops = [loops]

        # Expand each loop into servers
        expanded_servers = list(backend.servers)  # Start with existing servers

        for loop in loops:
            if not isinstance(loop, ForLoop):
                continue

            # Expand this loop
            loop_servers = self._expand_loop(loop)
            expanded_servers.extend(loop_servers)

        # Remove loops from metadata
        new_metadata = {k: v for k, v in backend.metadata.items() if k != "server_loops"}

        return replace(backend, servers=expanded_servers, metadata=new_metadata)

    def _expand_loop(self, loop: ForLoop) -> list[Server]:
        """Expand a single for loop into a list of servers."""
        # Evaluate the iterable to get the range/list
        values = self._evaluate_iterable(loop.iterable)

        servers = []
        for value in values:
            # Create a context with the loop variable
            context = {loop.variable: value}

            # Expand each item in the loop body
            for body_item in loop.body:
                if isinstance(body_item, Server):
                    # Clone the server and substitute variables
                    expanded_server = self._expand_server(body_item, context)
                    servers.append(expanded_server)
                elif isinstance(body_item, list):
                    # Handle list of servers (from nested structures)
                    for item in body_item:
                        if isinstance(item, Server):
                            expanded_server = self._expand_server(item, context)
                            servers.append(expanded_server)

        return servers

    def _evaluate_iterable(self, iterable: Any) -> list[int | str]:
        """Evaluate an iterable (range, list, etc.) to a list of values."""
        # Handle range tuple (start, end)
        if isinstance(iterable, tuple) and len(iterable) == 2:
            start, end = iterable
            if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                return list(range(int(start), int(end) + 1))  # Inclusive range

        # Handle list literal
        if isinstance(iterable, list):
            return iterable

        # Handle other types
        raise ParseError(f"Unsupported iterable type: {type(iterable)}")

    def _expand_server(self, server: Server, context: dict[str, Any]) -> Server:
        """Expand a server template with variable substitution."""
        # Substitute variables in name
        name = self._substitute_variables(server.name, context)

        # Substitute variables in address
        address = self._substitute_variables(server.address, context)

        # Create new server with substituted values
        return replace(
            server,
            name=name,
            address=address,
        )

    def _substitute_variables(self, text: str, context: dict[str, Any]) -> str:
        """Substitute ${var} and ${expr} in a string."""
        # Pattern for ${...}
        pattern = re.compile(r"\$\{([^}]+)\}")

        def replacer(match: re.Match[str]) -> str:
            expr = match.group(1).strip()

            # Check if it's a simple variable reference
            if expr in context:
                return str(context[expr])

            # Try to evaluate as an expression
            try:
                # Create a safe evaluation context with loop variables
                eval_context = dict(context)
                # Evaluate the expression
                result = eval(expr, {"__builtins__": {}}, eval_context)
                return str(result)
            except Exception as e:
                raise ParseError(f"Failed to evaluate expression '{expr}': {e}") from e

        return pattern.sub(replacer, text)
