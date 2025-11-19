"""Tests for dispatch directive (simple dispatch target for load balancing)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestBackendDispatch:
    """Test backend dispatch directive."""

    def test_backend_dispatch(self):
        """Test backend dispatch directive parsing."""
        config = """
        config test {
            backend app {
                mode: http
                dispatch: "192.168.1.100:8080"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].dispatch == "192.168.1.100:8080"

    def test_backend_dispatch_codegen(self):
        """Test backend dispatch code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                dispatch: "192.168.1.100:8080"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "dispatch 192.168.1.100:8080" in output
        assert "backend app" in output

    def test_backend_without_dispatch(self):
        """Test backend without dispatch (should be None)."""
        config = """
        config test {
            backend app {
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].dispatch is None

    def test_backend_dispatch_ipv4(self):
        """Test dispatch with IPv4 address."""
        config = """
        config test {
            backend web {
                mode: http
                dispatch: "10.0.0.1:80"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].dispatch == "10.0.0.1:80"

    def test_backend_dispatch_ipv6(self):
        """Test dispatch with IPv6 address."""
        config = """
        config test {
            backend web {
                mode: http
                dispatch: "[::1]:8080"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].dispatch == "[::1]:8080"

    def test_backend_dispatch_hostname(self):
        """Test dispatch with hostname."""
        config = """
        config test {
            backend api {
                mode: http
                dispatch: "backend.example.com:443"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].dispatch == "backend.example.com:443"


class TestDispatchIntegration:
    """Integration tests for dispatch directive."""

    def test_multiple_backends_different_dispatch(self):
        """Test multiple backends with different dispatch targets."""
        config = """
        config test {
            backend app1 {
                mode: http
                dispatch: "10.0.1.1:8080"
            }

            backend app2 {
                mode: http
                dispatch: "10.0.2.1:9090"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].dispatch == "10.0.1.1:8080"
        assert ir.backends[1].dispatch == "10.0.2.1:9090"

    def test_dispatch_codegen_complete(self):
        """Test complete dispatch configuration code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                dispatch: "192.168.100.50:8080"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend app" in output
        assert "mode http" in output
        assert "balance roundrobin" in output
        assert "dispatch 192.168.100.50:8080" in output

    def test_dispatch_with_balance_algorithm(self):
        """Test dispatch with different balance algorithms."""
        config = """
        config test {
            backend lb {
                mode: http
                balance: leastconn
                dispatch: "10.10.10.10:3000"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "balance leastconn" in output
        assert "dispatch 10.10.10.10:3000" in output

    def test_dispatch_with_timeouts(self):
        """Test dispatch with timeout configuration."""
        config = """
        config test {
            backend app {
                mode: http
                dispatch: "10.0.0.50:8888"
                timeout_connect: 5s
                timeout_server: 30s
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].dispatch == "10.0.0.50:8888"
        assert ir.backends[0].timeout_connect == "5s"
        assert ir.backends[0].timeout_server == "30s"

    def test_dispatch_standard_ports(self):
        """Test dispatch with standard HTTP/HTTPS ports."""
        configs = [
            ('dispatch: "web.example.com:80"', "web.example.com:80"),
            ('dispatch: "api.example.com:443"', "api.example.com:443"),
            ('dispatch: "ws.example.com:8080"', "ws.example.com:8080"),
        ]

        for dispatch_config, expected_value in configs:
            config = f"""
            config test {{
                backend app {{
                    mode: http
                    {dispatch_config}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.backends[0].dispatch == expected_value
