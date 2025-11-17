"""Test Server SSL options parsing and generation."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestServerSSLOptions:
    """Test server SSL options (SNI, ALPN)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_server_with_sni(self, parser, codegen):
        """Test server with SNI."""
        source = """
        config test {
            backend servers {
                balance: roundrobin

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 443
                        ssl: true
                        verify: "none"
                        sni: "example.com"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.backends) == 1
        backend = ir.backends[0]
        assert len(backend.servers) == 1
        server = backend.servers[0]
        assert server.name == "web1"
        assert server.ssl is True
        assert server.sni == "example.com"

        # Test code generation
        output = codegen.generate(ir)
        assert "server web1 10.0.1.1:443 ssl verify none sni example.com" in output

    def test_server_with_alpn(self, parser, codegen):
        """Test server with ALPN."""
        source = """
        config test {
            backend servers {
                balance: roundrobin

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 443
                        ssl: true
                        alpn: ["h2", "http/1.1"]
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.backends) == 1
        backend = ir.backends[0]
        assert len(backend.servers) == 1
        server = backend.servers[0]
        assert server.name == "web1"
        assert server.ssl is True
        assert server.alpn == ["h2", "http/1.1"]

        # Test code generation
        output = codegen.generate(ir)
        assert "server web1 10.0.1.1:443 ssl alpn h2,http/1.1" in output

    def test_server_with_sni_and_alpn(self, parser, codegen):
        """Test server with both SNI and ALPN."""
        source = """
        config test {
            backend servers {
                balance: roundrobin

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 443
                        ssl: true
                        verify: "required"
                        sni: "api.example.com"
                        alpn: ["h2"]
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.backends) == 1
        backend = ir.backends[0]
        assert len(backend.servers) == 1
        server = backend.servers[0]
        assert server.name == "web1"
        assert server.ssl is True
        assert server.ssl_verify == "required"
        assert server.sni == "api.example.com"
        assert server.alpn == ["h2"]

        # Test code generation
        output = codegen.generate(ir)
        assert "server web1 10.0.1.1:443 ssl verify required sni api.example.com alpn h2" in output
