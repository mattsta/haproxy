"""Comprehensive tests for ALL server options to achieve 100% coverage."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestAllServerOptions:
    """Test ALL server configuration options for complete coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_server_all_agent_options(self, parser, codegen):
        """Test all agent-check related options."""
        source = """
        config test {
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        agent-check: true
                        agent-port: 9090
                        agent-addr: "10.0.1.10"
                        agent-inter: 5s
                        agent-send: "health"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "agent-check" in output
        assert "agent-port 9090" in output
        assert "agent-addr 10.0.1.10" in output
        assert "agent-inter 5s" in output
        assert "agent-send health" in output

    def test_server_all_connection_options(self, parser, codegen):
        """Test all connection management options."""
        source = """
        config test {
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        minconn: 5
                        maxconn: 100
                        maxqueue: 50
                        max-reuse: 200
                        pool-max-conn: 75
                        pool-purge-delay: 10s
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "minconn 5" in output
        assert "maxconn 100" in output
        assert "maxqueue 50" in output
        assert "max-reuse 200" in output
        assert "pool-max-conn 75" in output
        assert "pool-purge-delay 10s" in output

    def test_server_all_dns_options(self, parser, codegen):
        """Test all DNS and resolution options."""
        source = """
        config test {
            backend app {
                servers {
                    server app1 {
                        address: "app.example.com"
                        port: 8080
                        resolvers: "mydns"
                        resolve-prefer: "ipv6"
                        init-addr: "last,libc,none"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "resolvers mydns" in output
        assert "resolve-prefer ipv6" in output
        assert "init-addr last,libc,none" in output

    def test_server_all_error_handling_options(self, parser, codegen):
        """Test all error handling and observation options."""
        source = """
        config test {
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        error-limit: 10
                        observe: "layer7"
                        on-error: "mark-down"
                        on-marked-down: "shutdown-sessions"
                        on-marked-up: "shutdown-backup-sessions"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "error-limit 10" in output
        assert "observe layer7" in output
        assert "on-error mark-down" in output
        assert "on-marked-down shutdown-sessions" in output
        assert "on-marked-up shutdown-backup-sessions" in output

    def test_server_all_protocol_options(self, parser, codegen):
        """Test all protocol and networking options."""
        source = """
        config test {
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        proto: "h2"
                        check-proto: "smtp"
                        tfo: true
                        namespace: "netns1"
                        usesrc: "client"
                        check-send-proxy: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "proto h2" in output
        assert "check-proto smtp" in output
        assert "tfo" in output
        assert "namespace netns1" in output
        assert "usesrc client" in output
        assert "check-send-proxy" in output

    def test_server_all_identity_options(self, parser, codegen):
        """Test all identity and tracking options."""
        source = """
        config test {
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        id: 1001
                        cookie: "srv1"
                        track: "backend/app1"
                        redir: "http://backup.example.com"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "id 1001" in output
        assert "cookie srv1" in output
        assert "track backend/app1" in output
        assert "redir http://backup.example.com" in output

    def test_server_state_options(self, parser, codegen):
        """Test server state management options."""
        source = """
        config test {
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
        backend = ir.backends[0]

        # Verify IR structure
        assert len(backend.servers) == 2

        output = codegen.generate(ir)
        assert "disabled" in output

    def test_server_combined_options(self, parser, codegen):
        """Test multiple server options combined."""
        source = """
        config test {
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        check: true
                        inter: 2s
                        rise: 3
                        fall: 2
                        weight: 100
                        maxconn: 500
                        minconn: 10
                        ssl: true
                        verify: "required"
                        sni: "app.example.com"
                        backup: false
                        id: 1
                        cookie: "app1"
                        agent-check: true
                        agent-port: 9090
                        resolvers: "dns1"
                        init-addr: "last"
                        error-limit: 5
                        on-error: "fastinter"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]

        # Verify IR structure
        assert server.name == "app1"
        assert server.check is True
        assert server.rise == 3
        assert server.fall == 2
        assert server.weight == 100
        assert server.maxconn == 500
        assert server.ssl is True

        # Verify codegen output
        output = codegen.generate(ir)
        assert "check" in output
        assert "inter 2s" in output
        assert "rise 3" in output
        assert "fall 2" in output
        assert "weight 100" in output
        assert "maxconn 500" in output
        assert "minconn 10" in output
        assert "ssl" in output
        assert "verify required" in output
        assert "sni app.example.com" in output
        assert "id 1" in output
        assert "cookie app1" in output
        assert "agent-check" in output
        assert "agent-port 9090" in output
        assert "resolvers dns1" in output
        assert "init-addr last" in output
        assert "error-limit 5" in output
        assert "on-error fastinter" in output
