"""Test default-server directive."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestDefaultServer:
    """Test default-server directive functionality."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_default_server_basic(self, parser, codegen):
        """Test basic default-server with check options."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    check: true
                    inter: 5s
                    rise: 2
                    fall: 3
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        # Verify default-server is set
        assert backend.default_server is not None
        assert backend.default_server.check is True
        assert backend.default_server.check_interval == "5s"
        assert backend.default_server.rise == 2
        assert backend.default_server.fall == 3

        # Test code generation
        output = codegen.generate(ir)
        assert "default-server check inter 5s rise 2 fall 3" in output
        assert "server api1 10.0.1.1:8080" in output
        assert "server api2 10.0.1.2:8080" in output

    def test_default_server_weight_maxconn(self, parser, codegen):
        """Test default-server with weight and maxconn."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    weight: 100
                    maxconn: 500
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.default_server.weight == 100
        assert backend.default_server.maxconn == 500

        output = codegen.generate(ir)
        assert "default-server weight 100 maxconn 500" in output

    def test_default_server_ssl(self, parser, codegen):
        """Test default-server with SSL options."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    ssl: true
                    verify: "none"
                    sni: "api.example.com"
                    alpn: ["h2", "http/1.1"]
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.default_server.ssl is True
        assert backend.default_server.ssl_verify == "none"
        assert backend.default_server.sni == "api.example.com"
        assert backend.default_server.alpn == ["h2", "http/1.1"]

        output = codegen.generate(ir)
        assert "default-server ssl verify none sni api.example.com alpn h2,http/1.1" in output

    def test_default_server_send_proxy(self, parser, codegen):
        """Test default-server with PROXY protocol."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    send-proxy-v2: true
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.default_server.send_proxy_v2 is True

        output = codegen.generate(ir)
        assert "default-server send-proxy-v2" in output

    def test_default_server_slowstart(self, parser, codegen):
        """Test default-server with slowstart."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    slowstart: 30s
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.default_server.slowstart == "30s"

        output = codegen.generate(ir)
        assert "default-server slowstart 30s" in output

    def test_default_server_comprehensive(self, parser, codegen):
        """Test comprehensive default-server configuration."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    check: true
                    inter: 5s
                    rise: 2
                    fall: 3
                    weight: 100
                    maxconn: 500
                    slowstart: 30s
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                    }
                    server api3 {
                        address: "10.0.1.3"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        # Verify all default-server properties
        assert backend.default_server.check is True
        assert backend.default_server.check_interval == "5s"
        assert backend.default_server.rise == 2
        assert backend.default_server.fall == 3
        assert backend.default_server.weight == 100
        assert backend.default_server.maxconn == 500
        assert backend.default_server.slowstart == "30s"

        # Verify servers exist
        assert len(backend.servers) == 3

        # Test code generation
        output = codegen.generate(ir)
        assert "default-server check inter 5s rise 2 fall 3 weight 100 maxconn 500 slowstart 30s" in output
        assert "server api1 10.0.1.1:8080" in output
        assert "server api2 10.0.1.2:8080" in output
        assert "server api3 10.0.1.3:8080" in output

    def test_production_config_with_default_server(self, parser, codegen):
        """Test production configuration showing config deduplication benefits."""
        source = """
        config production {
            backend api {
                balance: leastconn

                default-server {
                    check: true
                    inter: 5s
                    rise: 2
                    fall: 3
                    weight: 100
                    maxconn: 500
                    slowstart: 30s
                    send-proxy-v2: true
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                    }
                    server api3 {
                        address: "10.0.1.3"
                        port: 8080
                    }
                    server api4 {
                        address: "10.0.1.4"
                        port: 8080
                    }
                    server api5 {
                        address: "10.0.1.5"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        # Verify default-server has all options
        assert backend.default_server.check is True
        assert backend.default_server.send_proxy_v2 is True
        assert backend.default_server.slowstart == "30s"

        # Verify 5 servers
        assert len(backend.servers) == 5

        # Test code generation
        output = codegen.generate(ir)

        # Verify default-server line exists
        assert "default-server" in output
        assert "check inter 5s rise 2 fall 3" in output
        assert "send-proxy-v2" in output

        # Verify servers are simple (no repeated options)
        assert "server api1 10.0.1.1:8080" in output
        assert "server api5 10.0.1.5:8080" in output

    def test_multiple_backends_with_different_defaults(self, parser, codegen):
        """Test multiple backends each with their own default-server."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    check: true
                    inter: 5s
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }

            backend cache {
                balance: leastconn

                default-server {
                    check: true
                    inter: 2s
                    rise: 1
                    fall: 2
                }

                servers {
                    server cache1 {
                        address: "10.0.2.1"
                        port: 6379
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Verify first backend
        api_backend = ir.backends[0]
        assert api_backend.default_server.check_interval == "5s"

        # Verify second backend
        cache_backend = ir.backends[1]
        assert cache_backend.default_server.check_interval == "2s"
        assert cache_backend.default_server.rise == 1
        assert cache_backend.default_server.fall == 2

        # Test code generation
        output = codegen.generate(ir)

        # Both default-server directives should appear
        lines = output.split('\n')
        default_server_lines = [line for line in lines if 'default-server' in line]
        assert len(default_server_lines) == 2
