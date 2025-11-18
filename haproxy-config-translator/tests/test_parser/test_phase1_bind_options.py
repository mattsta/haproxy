"""Tests for Phase 1 critical bind options."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase1BindOptions:
    """Test cases for Phase 1 critical bind options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_bind_backlog(self, parser, codegen):
        """Test backlog bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 backlog 2048
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

        # Verify IR
        bind = ir.frontends[0].binds[0]
        assert bind.options.get("backlog") == 2048

        # Verify code generation
        assert "backlog 2048" in output

    def test_bind_interface(self, parser, codegen):
        """Test interface bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 interface "eth0"
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

        # Verify IR
        bind = ir.frontends[0].binds[0]
        assert bind.options.get("interface") == "eth0"

        # Verify code generation
        assert "interface eth0" in output

    def test_bind_thread(self, parser, codegen):
        """Test thread bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 thread 2
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

        # Verify IR
        bind = ir.frontends[0].binds[0]
        assert bind.options.get("thread") == 2

        # Verify code generation
        assert "thread 2" in output

    def test_bind_accept_netscaler_cip(self, parser, codegen):
        """Test accept-netscaler-cip bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 accept-netscaler-cip 31
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

        # Verify IR
        bind = ir.frontends[0].binds[0]
        assert bind.options.get("accept-netscaler-cip") == 31

        # Verify code generation
        assert "accept-netscaler-cip 31" in output

    def test_bind_ssl_strict_sni(self, parser, codegen):
        """Test strict-sni SSL bind option."""
        source = """
        config test {
            frontend https {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    strict-sni: true
                }
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

        # Verify SSL is enabled
        bind = ir.frontends[0].binds[0]
        assert bind.ssl is True
        assert bind.ssl_cert == "/etc/ssl/cert.pem"

        # Verify code generation
        assert "bind *:443 ssl" in output
        assert "crt /etc/ssl/cert.pem" in output
        assert "strict-sni" in output

    def test_bind_ssl_prefer_client_ciphers(self, parser, codegen):
        """Test prefer-client-ciphers SSL bind option."""
        source = """
        config test {
            frontend https {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    prefer-client-ciphers: true
                }
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

        # Verify code generation
        assert "prefer-client-ciphers" in output

    def test_bind_ssl_allow_0rtt(self, parser, codegen):
        """Test allow-0rtt SSL bind option (TLS 1.3 early data)."""
        source = """
        config test {
            frontend https {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    allow-0rtt: true
                }
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

        # Verify code generation
        assert "allow-0rtt" in output

    def test_bind_combined_socket_options(self, parser, codegen):
        """Test multiple socket options on single bind."""
        source = """
        config test {
            frontend web {
                bind *:80 backlog 4096 interface "eth1" thread 4 accept-netscaler-cip 31
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

        # Verify all options
        assert "backlog 4096" in output
        assert "interface eth1" in output
        assert "thread 4" in output
        assert "accept-netscaler-cip 31" in output

    def test_bind_production_ssl_hardening(self, parser, codegen):
        """Test production-ready SSL bind configuration with Phase 1 options."""
        source = """
        config test {
            global {
                daemon: true
                ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
                ssl-default-bind-options: ["no-sslv3", "no-tlsv10", "no-tlsv11", "no-tls-tickets"]
            }

            frontend https_hardened {
                bind *:443 ssl {
                    cert: "/etc/ssl/wildcard.pem"
                    alpn: ["h2", "http/1.1"]
                    strict-sni: true
                    prefer-client-ciphers: false
                    allow-0rtt: false
                    ssl-min-ver: "TLSv1.2"
                    ssl-max-ver: "TLSv1.3"
                } backlog 8192 thread 8

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

        # Verify comprehensive SSL hardening
        assert "bind *:443 ssl" in output
        assert "strict-sni" in output
        assert "ssl-min-ver TLSv1.2" in output
        assert "ssl-max-ver TLSv1.3" in output
        assert "backlog 8192" in output
        assert "thread 8" in output
