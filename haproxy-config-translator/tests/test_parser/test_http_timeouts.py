"""Test HTTP timeouts parsing and generation."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestHTTPTimeouts:
    """Test HTTP timeout configurations."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_timeouts_in_defaults(self, parser, codegen):
        """Test HTTP timeouts in defaults section."""
        source = """
        config test {
            defaults {
                mode: http
                timeout: {
                    connect: 5s
                    client: 50s
                    server: 50s
                    http_request: 10s
                    http_keep_alive: 30s
                }
            }

            frontend web {
                bind *:80
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert ir.defaults is not None
        assert ir.defaults.timeout_http_request == "10s"
        assert ir.defaults.timeout_http_keep_alive == "30s"

        # Test code generation
        output = codegen.generate(ir)
        assert "timeout http-request 10s" in output
        assert "timeout http-keep-alive 30s" in output

    def test_http_timeouts_in_frontend(self, parser, codegen):
        """Test HTTP timeouts in frontend section."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                timeout_http_request: 15s
                timeout_http_keep_alive: 60s
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.frontends) == 1
        frontend = ir.frontends[0]
        assert frontend.timeout_http_request == "15s"
        assert frontend.timeout_http_keep_alive == "60s"

        # Test code generation
        output = codegen.generate(ir)
        assert "timeout http-request 15s" in output
        assert "timeout http-keep-alive 60s" in output

    def test_http_timeouts_combined(self, parser, codegen):
        """Test HTTP timeouts in both defaults and frontend."""
        source = """
        config test {
            defaults {
                mode: http
                timeout: {
                    connect: 5s
                    client: 50s
                    server: 50s
                    http_request: 10s
                }
            }

            frontend web {
                bind *:80
                timeout_http_request: 20s
                timeout_http_keep_alive: 120s
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Check defaults
        assert ir.defaults is not None
        assert ir.defaults.timeout_http_request == "10s"

        # Check frontend overrides
        assert len(ir.frontends) == 1
        frontend = ir.frontends[0]
        assert frontend.timeout_http_request == "20s"
        assert frontend.timeout_http_keep_alive == "120s"

        # Test code generation - both should appear
        output = codegen.generate(ir)
        assert output.count("timeout http-request") == 2  # One in defaults, one in frontend
