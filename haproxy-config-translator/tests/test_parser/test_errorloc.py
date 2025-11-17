"""Test errorloc directive parsing and generation."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestErrorloc:
    """Test errorloc error redirect directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_errorloc_in_defaults(self, parser, codegen):
        """Test errorloc (302) redirect."""
        source = """
        config test {
            defaults {
                mode: http
                errorloc 503 "https://example.com/maintenance"
                errorloc 404 "https://example.com/notfound"
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
        assert ir.defaults.errorloc[503] == "https://example.com/maintenance"
        assert ir.defaults.errorloc[404] == "https://example.com/notfound"

        # Test code generation
        output = codegen.generate(ir)
        assert "errorloc 503 https://example.com/maintenance" in output
        assert "errorloc 404 https://example.com/notfound" in output

    def test_errorloc302(self, parser, codegen):
        """Test explicit errorloc302."""
        source = """
        config test {
            defaults {
                mode: http
                errorloc302 500 "https://example.com/error"
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
        assert ir.defaults.errorloc302[500] == "https://example.com/error"

        # Test code generation
        output = codegen.generate(ir)
        assert "errorloc302 500 https://example.com/error" in output

    def test_errorloc303(self, parser, codegen):
        """Test errorloc303 (303 See Other)."""
        source = """
        config test {
            defaults {
                mode: http
                errorloc303 502 "https://example.com/badgateway"
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
        assert ir.defaults.errorloc303[502] == "https://example.com/badgateway"

        # Test code generation
        output = codegen.generate(ir)
        assert "errorloc303 502 https://example.com/badgateway" in output
