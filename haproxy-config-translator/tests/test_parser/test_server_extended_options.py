"""Test extended server options with hyphens in syntax."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestServerExtendedOptions:
    """Test extended server configuration options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_server_with_id_and_cookie(self, parser, codegen):
        """Test server with id and cookie options."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: app
            }
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        id: 1001
                        cookie: "app1"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "id 1001" in output
        assert "cookie app1" in output

    def test_server_minconn_maxqueue(self, parser, codegen):
        """Test server with connection management options."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: app
            }
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        minconn: 10
                        maxqueue: 50
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "minconn 10" in output
        assert "maxqueue 50" in output

    def test_server_disabled_enabled(self, parser, codegen):
        """Test server state management."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: app
            }
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        disabled: true
                    }
                    server app2 {
                        address: "10.0.1.11"
                        port: 8080
                        enabled: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "disabled" in output
