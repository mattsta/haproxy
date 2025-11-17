"""Test monitor-uri parsing and generation."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestMonitorURI:
    """Test monitor-uri health check endpoint."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_monitor_uri_in_frontend(self, parser, codegen):
        """Test monitor-uri in frontend."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor_uri: "/health"
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
        assert frontend.monitor_uri == "/health"

        # Test code generation
        output = codegen.generate(ir)
        assert "monitor-uri /health" in output

    def test_monitor_uri_with_path(self, parser, codegen):
        """Test monitor-uri with different paths."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor_uri: "/status/healthz"
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
        frontend = ir.frontends[0]
        assert frontend.monitor_uri == "/status/healthz"

        # Test code generation
        output = codegen.generate(ir)
        assert "monitor-uri /status/healthz" in output
