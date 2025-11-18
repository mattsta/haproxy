"""Test advanced timeout options: tunnel, client-fin, server-fin, tarpit."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestAdvancedTimeouts:
    """Test advanced timeout options for WebSocket, FIN handling, and security."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_timeout_tunnel(self, parser, codegen):
        """Test timeout tunnel for WebSocket/persistent connections."""
        source = """
        config test {
            backend websocket {
                balance: source
                timeout_tunnel: 3600s
                servers {
                    server ws1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.timeout_tunnel == "3600s"

        output = codegen.generate(ir)
        assert "timeout tunnel 3600s" in output

    def test_backend_timeout_server_fin(self, parser, codegen):
        """Test timeout server-fin for server FIN handling."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                timeout_server_fin: 1s
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

        assert backend.timeout_server_fin == "1s"

        output = codegen.generate(ir)
        assert "timeout server-fin 1s" in output

    def test_frontend_timeout_client_fin(self, parser, codegen):
        """Test timeout client-fin for client FIN handling."""
        source = """
        config test {
            frontend web {
                bind *:80
                timeout_client_fin: 1s
                default_backend: api
            }
            backend api {
                balance: roundrobin
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
        frontend = ir.frontends[0]

        assert frontend.timeout_client_fin == "1s"

        output = codegen.generate(ir)
        assert "timeout client-fin 1s" in output

    def test_frontend_timeout_tarpit(self, parser, codegen):
        """Test timeout tarpit for security (tarpit timeout)."""
        source = """
        config test {
            frontend web {
                bind *:80
                timeout_tarpit: 60s
                default_backend: api
            }
            backend api {
                balance: roundrobin
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
        frontend = ir.frontends[0]

        assert frontend.timeout_tarpit == "60s"

        output = codegen.generate(ir)
        assert "timeout tarpit 60s" in output

    def test_defaults_timeout_block_with_all_timeouts(self, parser, codegen):
        """Test defaults with all timeout options via timeout block."""
        source = """
        config test {
            defaults {
                mode: http
                timeout: {
                    connect: 5s
                    client: 30s
                    server: 30s
                    tunnel: 3600s
                    client_fin: 1s
                    server_fin: 1s
                    tarpit: 60s
                }
            }
            backend api {
                balance: roundrobin
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
        defaults = ir.defaults

        assert defaults.timeout_connect == "5s"
        assert defaults.timeout_client == "30s"
        assert defaults.timeout_server == "30s"
        assert defaults.timeout_tunnel == "3600s"
        assert defaults.timeout_client_fin == "1s"
        assert defaults.timeout_server_fin == "1s"
        assert defaults.timeout_tarpit == "60s"

        output = codegen.generate(ir)
        assert "timeout tunnel 3600s" in output
        assert "timeout client-fin 1s" in output
        assert "timeout server-fin 1s" in output
        assert "timeout tarpit 60s" in output

    def test_websocket_production_config(self, parser, codegen):
        """Test WebSocket production config with tunnel timeouts."""
        source = """
        config websocket_prod {
            frontend ws_frontend {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                }
                timeout_client: 3600s
                timeout_client_fin: 1s
                default_backend: ws_backend
            }

            backend ws_backend {
                balance: source
                timeout_server: 3600s
                timeout_tunnel: 3600s
                timeout_server_fin: 1s

                servers {
                    server ws1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server ws2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        backend = ir.backends[0]

        # Frontend timeouts
        assert frontend.timeout_client == "3600s"
        assert frontend.timeout_client_fin == "1s"

        # Backend timeouts
        assert backend.timeout_server == "3600s"
        assert backend.timeout_tunnel == "3600s"
        assert backend.timeout_server_fin == "1s"

        output = codegen.generate(ir)
        # Verify all timeouts are in output
        assert "timeout client 3600s" in output
        assert "timeout client-fin 1s" in output
        assert "timeout server 3600s" in output
        assert "timeout tunnel 3600s" in output
        assert "timeout server-fin 1s" in output

    def test_combined_frontend_timeouts(self, parser, codegen):
        """Test frontend with all timeout options combined."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                }
                timeout_client: 60s
                timeout_http_request: 15s
                timeout_http_keep_alive: 10s
                timeout_client_fin: 1s
                timeout_tarpit: 60s
                default_backend: api
            }

            backend api {
                balance: leastconn
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
        frontend = ir.frontends[0]

        assert frontend.timeout_client == "60s"
        assert frontend.timeout_http_request == "15s"
        assert frontend.timeout_http_keep_alive == "10s"
        assert frontend.timeout_client_fin == "1s"
        assert frontend.timeout_tarpit == "60s"

        output = codegen.generate(ir)
        assert "timeout client 60s" in output
        assert "timeout http-request 15s" in output
        assert "timeout http-keep-alive 10s" in output
        assert "timeout client-fin 1s" in output
        assert "timeout tarpit 60s" in output

    def test_combined_backend_timeouts(self, parser, codegen):
        """Test backend with all timeout options combined."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                timeout_connect: 5s
                timeout_server: 60s
                timeout_check: 3s
                timeout_tunnel: 3600s
                timeout_server_fin: 1s

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.timeout_connect == "5s"
        assert backend.timeout_server == "60s"
        assert backend.timeout_check == "3s"
        assert backend.timeout_tunnel == "3600s"
        assert backend.timeout_server_fin == "1s"

        output = codegen.generate(ir)
        assert "timeout connect 5s" in output
        assert "timeout server 60s" in output
        assert "timeout check 3s" in output
        assert "timeout tunnel 3600s" in output
        assert "timeout server-fin 1s" in output
