"""Tests for Phase 4B Part 3 global directives - QUIC/HTTP3 Support."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase4BPart3GlobalDirectives:
    """Test cases for Phase 4B Part 3 global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_quic_frontend_directives(self, parser, codegen):
        """Test QUIC frontend configuration directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.quic.frontend.conn-tx-buffers.limit: 100
                tune.quic.frontend.max-idle-timeout: "30s"
                tune.quic.frontend.max-streams-bidi: 128
                tune.quic.frontend.glitches-threshold: 3
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

        assert ir.global_config.tuning.get("tune.quic.frontend.conn-tx-buffers-limit") == 100
        assert ir.global_config.tuning.get("tune.quic.frontend.max-idle-timeout") == "30s"
        assert ir.global_config.tuning.get("tune.quic.frontend.max-streams-bidi") == 128
        assert ir.global_config.tuning.get("tune.quic.frontend.glitches-threshold") == 3

        assert "tune.quic.frontend.conn-tx-buffers-limit 100" in output
        assert "tune.quic.frontend.max-idle-timeout 30s" in output
        assert "tune.quic.frontend.max-streams-bidi 128" in output
        assert "tune.quic.frontend.glitches-threshold 3" in output

    def test_global_quic_general_directives(self, parser, codegen):
        """Test general QUIC configuration directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.quic.retry-threshold: 3
                tune.quic.max-frame-loss: 5
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

        assert ir.global_config.tuning.get("tune.quic.retry-threshold") == 3
        assert ir.global_config.tuning.get("tune.quic.max-frame-loss") == 5

        assert "tune.quic.retry-threshold 3" in output
        assert "tune.quic.max-frame-loss 5" in output

    def test_global_quic_socket_directive(self, parser, codegen):
        """Test QUIC socket configuration directive."""
        source = """
        config test {
            global {
                daemon: true
                tune.quic.socket.owner: "listener"
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

        assert ir.global_config.tuning.get("tune.quic.socket.owner") == "listener"
        assert "tune.quic.socket.owner listener" in output

    def test_global_quic_http3_optimization(self, parser, codegen):
        """Test QUIC optimizations for HTTP/3 deployment."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 50000

                // QUIC/HTTP3 Frontend Optimization
                tune.quic.frontend.conn-tx-buffers.limit: 200
                tune.quic.frontend.max-idle-timeout: "60s"
                tune.quic.frontend.max-streams-bidi: 256
                tune.quic.frontend.glitches-threshold: 5

                // QUIC Retry Configuration
                tune.quic.retry-threshold: 2

                // QUIC Socket Configuration
                tune.quic.socket.owner: "connection"
            }

            frontend https_http3 {
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

        # Verify all QUIC directives in IR
        assert ir.global_config.tuning.get("tune.quic.frontend.conn-tx-buffers-limit") == 200
        assert ir.global_config.tuning.get("tune.quic.frontend.max-idle-timeout") == "60s"
        assert ir.global_config.tuning.get("tune.quic.frontend.max-streams-bidi") == 256
        assert ir.global_config.tuning.get("tune.quic.frontend.glitches-threshold") == 5
        assert ir.global_config.tuning.get("tune.quic.retry-threshold") == 2
        assert ir.global_config.tuning.get("tune.quic.socket.owner") == "connection"

        # Verify all QUIC directives in output
        assert "tune.quic.frontend.conn-tx-buffers-limit 200" in output
        assert "tune.quic.frontend.max-idle-timeout 60s" in output
        assert "tune.quic.frontend.max-streams-bidi 256" in output
        assert "tune.quic.frontend.glitches-threshold 5" in output
        assert "tune.quic.retry-threshold 2" in output
        assert "tune.quic.socket.owner connection" in output

    def test_global_phase4b_part3_comprehensive(self, parser, codegen):
        """Test all Phase 4B Part 3 directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000

                // QUIC Frontend Configuration
                tune.quic.frontend.conn-tx-buffers.limit: 150
                tune.quic.frontend.max-idle-timeout: "45s"
                tune.quic.frontend.max-streams-bidi: 200
                tune.quic.frontend.glitches-threshold: 4

                // QUIC General Configuration
                tune.quic.retry-threshold: 3
                tune.quic.max-frame-loss: 10

                // QUIC Socket Configuration
                tune.quic.socket.owner: "listener"
            }

            frontend quic_frontend {
                bind *:443
                default_backend: quic_backend
            }

            backend quic_backend {
                servers {
                    server backend1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify all QUIC Frontend directives in IR
        assert ir.global_config.tuning.get("tune.quic.frontend.conn-tx-buffers-limit") == 150
        assert ir.global_config.tuning.get("tune.quic.frontend.max-idle-timeout") == "45s"
        assert ir.global_config.tuning.get("tune.quic.frontend.max-streams-bidi") == 200
        assert ir.global_config.tuning.get("tune.quic.frontend.glitches-threshold") == 4

        # Verify QUIC General directives in IR
        assert ir.global_config.tuning.get("tune.quic.retry-threshold") == 3
        assert ir.global_config.tuning.get("tune.quic.max-frame-loss") == 10

        # Verify QUIC Socket directive in IR
        assert ir.global_config.tuning.get("tune.quic.socket.owner") == "listener"

        # Verify all QUIC directives in output
        assert "tune.quic.frontend.conn-tx-buffers-limit 150" in output
        assert "tune.quic.frontend.max-idle-timeout 45s" in output
        assert "tune.quic.frontend.max-streams-bidi 200" in output
        assert "tune.quic.frontend.glitches-threshold 4" in output
        assert "tune.quic.retry-threshold 3" in output
        assert "tune.quic.max-frame-loss 10" in output
        assert "tune.quic.socket.owner listener" in output

    def test_global_quic_minimal_config(self, parser, codegen):
        """Test minimal QUIC configuration."""
        source = """
        config test {
            global {
                daemon: true
                tune.quic.frontend.max-streams-bidi: 100
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

        assert ir.global_config.tuning.get("tune.quic.frontend.max-streams-bidi") == 100
        assert "tune.quic.frontend.max-streams-bidi 100" in output
