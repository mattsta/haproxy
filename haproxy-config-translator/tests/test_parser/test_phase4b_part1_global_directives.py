"""Tests for Phase 4B Part 1 global directives - HTTP Client & Platform Options."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase4BPart1GlobalDirectives:
    """Test cases for Phase 4B Part 1 global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_httpclient_configuration(self, parser, codegen):
        """Test HTTP client configuration directives."""
        source = """
        config test {
            global {
                daemon: true
                httpclient.resolvers.disabled: false
                httpclient.resolvers.id: "nameserver1"
                httpclient.resolvers.prefer: "ipv4"
                httpclient.retries: 3
                httpclient.ssl.verify: "none"
                httpclient.ssl.ca-file: "/etc/ssl/certs/ca-certificates.crt"
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.httpclient_resolvers_disabled is False
        assert ir.global_config.httpclient_resolvers_id == "nameserver1"
        assert ir.global_config.httpclient_resolvers_prefer == "ipv4"
        assert ir.global_config.httpclient_retries == 3
        assert ir.global_config.httpclient_ssl_verify == "none"
        assert ir.global_config.httpclient_ssl_ca_file == "/etc/ssl/certs/ca-certificates.crt"

        # Note: httpclient.resolvers.disabled=false won't appear in output (only true values)
        assert "httpclient.resolvers.id nameserver1" in output
        assert "httpclient.resolvers.prefer ipv4" in output
        assert "httpclient.retries 3" in output
        assert "httpclient.ssl.verify none" in output
        assert "httpclient.ssl.ca-file /etc/ssl/certs/ca-certificates.crt" in output

    def test_global_httpclient_resolvers_disabled(self, parser, codegen):
        """Test HTTP client with resolvers disabled."""
        source = """
        config test {
            global {
                daemon: true
                httpclient.resolvers.disabled: true
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.httpclient_resolvers_disabled is True
        assert "httpclient.resolvers.disabled" in output

    def test_global_platform_specific_options(self, parser, codegen):
        """Test platform-specific I/O options."""
        source = """
        config test {
            global {
                daemon: true
                noepoll: true
                nokqueue: true
                nopoll: true
                nosplice: true
                nogetaddrinfo: true
                noreuseport: true
                limited-quic: true
                localpeer: "lb-node-01"
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.noepoll is True
        assert ir.global_config.nokqueue is True
        assert ir.global_config.nopoll is True
        assert ir.global_config.nosplice is True
        assert ir.global_config.nogetaddrinfo is True
        assert ir.global_config.noreuseport is True
        assert ir.global_config.limited_quic is True
        assert ir.global_config.localpeer == "lb-node-01"

        assert "noepoll" in output
        assert "nokqueue" in output
        assert "nopoll" in output
        assert "nosplice" in output
        assert "nogetaddrinfo" in output
        assert "noreuseport" in output
        assert "limited-quic" in output
        assert "localpeer lb-node-01" in output

    def test_global_platform_optimization(self, parser, codegen):
        """Test selective platform options for optimization."""
        source = """
        config test {
            global {
                daemon: true
                noepoll: false
                nokqueue: false
                noreuseport: true
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.noepoll is False
        assert ir.global_config.nokqueue is False
        assert ir.global_config.noreuseport is True

        # false values don't appear in output
        assert "noepoll" not in output
        assert "nokqueue" not in output
        assert "noreuseport" in output

    def test_global_phase4b_part1_comprehensive(self, parser, codegen):
        """Test all Phase 4B Part 1 directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000

                // HTTP Client Configuration
                httpclient.resolvers.id: "dns-resolver-1"
                httpclient.resolvers.prefer: "ipv6"
                httpclient.retries: 5
                httpclient.ssl.verify: "required"
                httpclient.ssl.ca-file: "/etc/ssl/certs/ca-bundle.crt"

                // Platform-Specific Optimizations
                nogetaddrinfo: true
                noreuseport: false
                limited-quic: false
                localpeer: "production-lb-01"
            }

            frontend https {
                bind *:443
                default_backend: web
            }

            backend web {
                servers {
                    server web1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify all directives in IR
        assert ir.global_config.httpclient_resolvers_id == "dns-resolver-1"
        assert ir.global_config.httpclient_resolvers_prefer == "ipv6"
        assert ir.global_config.httpclient_retries == 5
        assert ir.global_config.httpclient_ssl_verify == "required"
        assert ir.global_config.httpclient_ssl_ca_file == "/etc/ssl/certs/ca-bundle.crt"
        assert ir.global_config.nogetaddrinfo is True
        assert ir.global_config.noreuseport is False
        assert ir.global_config.limited_quic is False
        assert ir.global_config.localpeer == "production-lb-01"

        # Verify directives in output
        assert "httpclient.resolvers.id dns-resolver-1" in output
        assert "httpclient.resolvers.prefer ipv6" in output
        assert "httpclient.retries 5" in output
        assert "httpclient.ssl.verify required" in output
        assert "httpclient.ssl.ca-file /etc/ssl/certs/ca-bundle.crt" in output
        assert "nogetaddrinfo" in output
        assert "localpeer production-lb-01" in output
        # false values don't appear
        assert "noreuseport" not in output
        assert "limited-quic" not in output
