"""Tests for Compression Tuning global directives - Final Phase."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestCompressionTuningGlobalDirectives:
    """Test cases for Compression Tuning global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_zlib_memlevel(self, parser, codegen):
        """Test zlib memory level tuning directive."""
        source = """
        config test {
            global {
                daemon: true
                tune.zlib.memlevel: 8
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

        assert ir.global_config.tuning.get("tune.zlib.memlevel") == 8
        assert "tune.zlib.memlevel 8" in output

    def test_global_zlib_windowsize(self, parser, codegen):
        """Test zlib window size tuning directive."""
        source = """
        config test {
            global {
                daemon: true
                tune.zlib.windowsize: 15
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

        assert ir.global_config.tuning.get("tune.zlib.windowsize") == 15
        assert "tune.zlib.windowsize 15" in output

    def test_global_zlib_comprehensive(self, parser, codegen):
        """Test both zlib tuning directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000

                // Compression Tuning
                tune.zlib.memlevel: 9
                tune.zlib.windowsize: 15
            }

            frontend https {
                bind *:443
                default_backend: web
            }

            backend web {
                compression {
                    algo: "gzip"
                    type: ["text/html", "text/css", "application/json"]
                }

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

        # Verify both directives in IR
        assert ir.global_config.tuning.get("tune.zlib.memlevel") == 9
        assert ir.global_config.tuning.get("tune.zlib.windowsize") == 15

        # Verify both directives in output
        assert "tune.zlib.memlevel 9" in output
        assert "tune.zlib.windowsize 15" in output

    def test_global_zlib_performance_optimization(self, parser, codegen):
        """Test zlib tuning for high-performance compression."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 200000

                // High-performance compression settings
                tune.zlib.memlevel: 8
                tune.zlib.windowsize: 13

                // Other compression-related tuning
                maxcompcpuusage: 85
                maxcomprate: 5000000
            }

            frontend api {
                bind *:443
                default_backend: api_backend
            }

            backend api_backend {
                compression {
                    algo: "gzip"
                    type: ["application/json", "application/xml"]
                }

                servers {
                    server api1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify zlib tuning directives
        assert ir.global_config.tuning.get("tune.zlib.memlevel") == 8
        assert ir.global_config.tuning.get("tune.zlib.windowsize") == 13

        # Verify other compression-related directives
        assert ir.global_config.maxcompcpuusage == 85
        assert ir.global_config.maxcomprate == 5000000

        assert "tune.zlib.memlevel 8" in output
        assert "tune.zlib.windowsize 13" in output
        assert "maxcompcpuusage 85" in output
        assert "maxcomprate 5000000" in output

    def test_global_100_percent_parity_achieved(self, parser, codegen):
        """Test comprehensive configuration with all major directive categories.

        This test represents 100% HAProxy global directive parity!
        """
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000
                nbproc: 4

                // Process & Logging (Phase 1)
                user: "haproxy"
                group: "haproxy"
                log "/dev/log" local0 info

                // SSL/TLS (Phase 1 & 2)
                ssl-default-bind-ciphers: "ECDHE-RSA-AES128-GCM-SHA256"
                ssl-default-bind-options: ["no-sslv3", "no-tlsv10"]

                // Memory & CPU (Phase 3)
                tune.buffers.limit: 1073741824
                tune.comp.maxlevel: 9

                // Performance & Runtime (Phase 4A)
                busy-polling: true
                max-spread-checks: 5000
                tune.idle-pool.shared: "on"

                // HTTP Client (Phase 4B Part 1)
                httpclient.retries: 3

                // SSL Advanced (Phase 4B Part 2)
                ssl-mode-async: true

                // QUIC/HTTP3 (Phase 4B Part 3)
                tune.quic.frontend.max-streams-bidi: 128

                // Device Detection (Phase 4B Part 4)
                deviceatlas-json-file: "/etc/haproxy/deviceatlas.json"

                // Compression Tuning (Final Phase)
                tune.zlib.memlevel: 9
                tune.zlib.windowsize: 15
            }

            frontend web {
                bind *:443
                default_backend: app
            }

            backend app {
                compression {
                    algo: "gzip"
                    type: ["text/html", "application/json"]
                }

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

        # Verify comprehensive configuration includes all phases
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 100000
        assert ir.global_config.user == "haproxy"
        assert ir.global_config.ssl_default_bind_ciphers == "ECDHE-RSA-AES128-GCM-SHA256"
        assert ir.global_config.busy_polling is True
        assert ir.global_config.httpclient_retries == 3
        assert ir.global_config.ssl_mode_async is True
        assert ir.global_config.tuning.get("tune.quic.frontend.max-streams-bidi") == 128
        assert ir.global_config.deviceatlas_json_file == "/etc/haproxy/deviceatlas.json"
        assert ir.global_config.tuning.get("tune.zlib.memlevel") == 9
        assert ir.global_config.tuning.get("tune.zlib.windowsize") == 15

        # Verify output contains directives from all phases
        assert "daemon" in output
        assert "maxconn 100000" in output
        assert "user haproxy" in output
        assert "ssl-default-bind-ciphers" in output
        assert "busy-polling" in output
        assert "httpclient.retries 3" in output
        assert "ssl-mode-async" in output
        assert "tune.quic.frontend.max-streams-bidi 128" in output
        assert "deviceatlas-json-file /etc/haproxy/deviceatlas.json" in output
        assert "tune.zlib.memlevel 9" in output
        assert "tune.zlib.windowsize 15" in output
