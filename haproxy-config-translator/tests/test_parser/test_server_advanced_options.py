"""Test advanced server options: send-proxy-v2, slowstart."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestServerAdvancedOptions:
    """Test advanced server-level options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_server_send_proxy(self, parser, codegen):
        """Test send-proxy on individual server."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        send-proxy: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]

        assert server.send_proxy is True

        output = codegen.generate(ir)
        assert "server api1 10.0.1.1:8080 send-proxy" in output

    def test_server_send_proxy_v2(self, parser, codegen):
        """Test send-proxy-v2 on individual server."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        send-proxy-v2: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]

        assert server.send_proxy_v2 is True

        output = codegen.generate(ir)
        assert "server api1 10.0.1.1:8080 send-proxy-v2" in output

    def test_server_slowstart(self, parser, codegen):
        """Test slowstart on individual server."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        slowstart: 30s
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]

        assert server.slowstart == "30s"

        output = codegen.generate(ir)
        assert "server api1 10.0.1.1:8080 slowstart 30s" in output

    def test_server_combined_advanced_options(self, parser, codegen):
        """Test combining send-proxy-v2 and slowstart."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                        send-proxy-v2: true
                        slowstart: 30s
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]

        assert server.check is True
        assert server.send_proxy_v2 is True
        assert server.slowstart == "30s"

        output = codegen.generate(ir)
        assert "server api1 10.0.1.1:8080" in output
        assert "check" in output
        assert "send-proxy-v2" in output
        assert "slowstart 30s" in output

    def test_server_vs_default_server_options(self, parser, codegen):
        """Test that server-specific options override default-server."""
        source = """
        config test {
            backend api {
                balance: roundrobin

                default-server {
                    slowstart: 60s
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        slowstart: 30s
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

        # Verify default-server has slowstart
        assert backend.default_server is not None
        assert backend.default_server.slowstart == "60s"

        # Verify api1 has its own slowstart
        api1 = backend.servers[0]
        assert api1.slowstart == "30s"

        # Verify api2 doesn't have slowstart set (will inherit from default-server)
        api2 = backend.servers[1]
        assert api2.slowstart is None

        output = codegen.generate(ir)
        # default-server should have slowstart 60s
        assert "default-server slowstart 60s" in output
        # api1 should have its own slowstart 30s
        assert "server api1 10.0.1.1:8080 slowstart 30s" in output
        # api2 should be simple (inherits from default-server)
        assert "server api2 10.0.1.2:8080" in output

    def test_multiple_servers_different_options(self, parser, codegen):
        """Test multiple servers with different advanced options."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        send-proxy-v2: true
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                        slowstart: 45s
                    }
                    server api3 {
                        address: "10.0.1.3"
                        port: 8080
                        send-proxy-v2: true
                        slowstart: 30s
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        # Verify each server
        api1 = backend.servers[0]
        assert api1.send_proxy_v2 is True
        assert api1.slowstart is None

        api2 = backend.servers[1]
        assert api2.send_proxy_v2 is False
        assert api2.slowstart == "45s"

        api3 = backend.servers[2]
        assert api3.send_proxy_v2 is True
        assert api3.slowstart == "30s"

        output = codegen.generate(ir)
        assert "server api1 10.0.1.1:8080 send-proxy-v2" in output
        assert "server api2 10.0.1.2:8080 slowstart 45s" in output
        assert "server api3 10.0.1.3:8080 send-proxy-v2 slowstart 30s" in output

    def test_production_config_with_server_options(self, parser, codegen):
        """Test production configuration with individual server options."""
        source = """
        config production {
            backend api {
                balance: leastconn

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
                        send-proxy-v2: true
                        slowstart: 30s
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                        send-proxy-v2: true
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

        # Verify default-server
        assert backend.default_server.check is True
        assert backend.default_server.check_interval == "5s"

        # Verify servers
        assert len(backend.servers) == 3
        assert backend.servers[0].send_proxy_v2 is True
        assert backend.servers[0].slowstart == "30s"
        assert backend.servers[1].send_proxy_v2 is True
        assert backend.servers[1].slowstart is None
        assert backend.servers[2].send_proxy_v2 is False
        assert backend.servers[2].slowstart is None

        output = codegen.generate(ir)

        # Verify default-server is present
        assert "default-server check inter 5s rise 2 fall 3" in output

        # Verify each server with their specific options
        assert "server api1 10.0.1.1:8080 send-proxy-v2 slowstart 30s" in output
        assert "server api2 10.0.1.2:8080 send-proxy-v2" in output
        assert "server api3 10.0.1.3:8080" in output

    def test_slowstart_with_different_durations(self, parser, codegen):
        """Test slowstart with different time durations."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        slowstart: 30s
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                        slowstart: 2m
                    }
                    server api3 {
                        address: "10.0.1.3"
                        port: 8080
                        slowstart: 1h
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.servers[0].slowstart == "30s"
        assert backend.servers[1].slowstart == "2m"
        assert backend.servers[2].slowstart == "1h"

        output = codegen.generate(ir)
        assert "slowstart 30s" in output
        assert "slowstart 2m" in output
        assert "slowstart 1h" in output
