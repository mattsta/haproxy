"""Tests for Phase 2 global directives - SSL/HTTP/2 tuning and advanced features."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase2GlobalDirectives:
    """Test cases for Phase 2 global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_buffer_tuning(self, parser, codegen):
        """Test buffer tuning directives: maxpipes, tune.bufsize, tune.maxrewrite."""
        source = """
        config test {
            global {
                daemon: true
                maxpipes: 8192
                tune.bufsize: 32768
                tune.maxrewrite: 8192
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.maxpipes == 8192
        assert ir.global_config.tuning.get("tune.bufsize") == 32768
        assert ir.global_config.tuning.get("tune.maxrewrite") == 8192

        # Verify code generation
        assert "maxpipes 8192" in output
        assert "tune.bufsize 32768" in output
        assert "tune.maxrewrite 8192" in output

    def test_global_ssl_tls13_ciphersuites(self, parser, codegen):
        """Test TLS 1.3 ciphersuite directives."""
        source = """
        config test {
            global {
                daemon: true
                ssl-default-bind-ciphersuites: "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"
                ssl-default-server-ciphersuites: "TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256"
            }

            frontend https {
                bind *:443
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
        assert ir.global_config is not None
        assert ir.global_config.ssl_default_bind_ciphersuites == "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"
        assert ir.global_config.ssl_default_server_ciphersuites == "TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256"

        # Verify code generation
        assert "ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384" in output
        assert "ssl-default-server-ciphersuites TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256" in output

    def test_global_ssl_server_options(self, parser, codegen):
        """Test ssl-default-server-options directive."""
        source = """
        config test {
            global {
                daemon: true
                ssl-default-server-options: ["no-sslv3", "no-tlsv10", "no-tlsv11"]
            }

            frontend https {
                bind *:443
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        ssl: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify IR
        assert ir.global_config is not None
        assert "no-sslv3" in ir.global_config.ssl_default_server_options
        assert "no-tlsv10" in ir.global_config.ssl_default_server_options
        assert "no-tlsv11" in ir.global_config.ssl_default_server_options

        # Verify code generation
        assert "ssl-default-server-options no-sslv3" in output
        assert "ssl-default-server-options no-tlsv10" in output
        assert "ssl-default-server-options no-tlsv11" in output

    def test_global_ssl_engine_and_key_base(self, parser, codegen):
        """Test ssl-engine and key-base directives."""
        source = """
        config test {
            global {
                daemon: true
                key-base: "/etc/ssl/keys"
                ssl-engine: "aesni"
            }

            frontend https {
                bind *:443
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
        assert ir.global_config is not None
        assert ir.global_config.key_base == "/etc/ssl/keys"
        assert ir.global_config.ssl_engine == "aesni"

        # Verify code generation
        assert "key-base /etc/ssl/keys" in output
        assert "ssl-engine aesni" in output

    def test_global_master_worker_mode(self, parser, codegen):
        """Test master-worker and mworker-max-reloads directives."""
        source = """
        config test {
            global {
                daemon: true
                master-worker: true
                mworker-max-reloads: 3
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.master_worker is True
        assert ir.global_config.mworker_max_reloads == 3

        # Verify code generation
        assert "master-worker" in output
        assert "mworker-max-reloads 3" in output

    def test_global_ssl_tuning_comprehensive(self, parser, codegen):
        """Test all SSL tuning directives (tune.ssl.*)."""
        source = """
        config test {
            global {
                daemon: true
                tune.ssl.bufsize: 32768
                tune.ssl.cachesize: 100000
                tune.ssl.lifetime: "5m"
                tune.ssl.maxrecord: 16384
                tune.ssl.keylog: "/var/log/ssl-keys.log"
                tune.ssl.capture-cipherlist-size: 256
                tune.ssl.capture-buffer-size: 128
                tune.ssl.default-dh-param: 2048
                tune.ssl.ocsp-update.minthour: 1
                tune.ssl.ocsp-update.maxhour: 24
            }

            frontend https {
                bind *:443
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

        # Verify IR (tuning dict)
        assert ir.global_config is not None
        assert ir.global_config.tuning.get("tune.ssl.bufsize") == 32768
        assert ir.global_config.tuning.get("tune.ssl.cachesize") == 100000
        assert ir.global_config.tuning.get("tune.ssl.lifetime") == "5m"
        assert ir.global_config.tuning.get("tune.ssl.maxrecord") == 16384
        assert ir.global_config.tuning.get("tune.ssl.keylog") == "/var/log/ssl-keys.log"
        assert ir.global_config.tuning.get("tune.ssl.capture-cipherlist-size") == 256
        assert ir.global_config.tuning.get("tune.ssl.capture-buffer-size") == 128
        assert ir.global_config.tuning.get("tune.ssl.default-dh-param") == 2048
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.minthour") == 1
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.maxhour") == 24

        # Verify code generation
        assert "tune.ssl.bufsize 32768" in output
        assert "tune.ssl.cachesize 100000" in output
        assert "tune.ssl.lifetime 5m" in output
        assert "tune.ssl.maxrecord 16384" in output
        assert "tune.ssl.keylog /var/log/ssl-keys.log" in output
        assert "tune.ssl.capture-cipherlist-size 256" in output
        assert "tune.ssl.capture-buffer-size 128" in output
        assert "tune.ssl.default-dh-param 2048" in output
        assert "tune.ssl.ocsp-update.minthour 1" in output
        assert "tune.ssl.ocsp-update.maxhour 24" in output

    def test_global_h2_tuning_backend(self, parser, codegen):
        """Test HTTP/2 backend tuning directives (tune.h2.be.*)."""
        source = """
        config test {
            global {
                daemon: true
                tune.h2.be.glitches-threshold: 10
                tune.h2.be.initial-window-size: 65536
                tune.h2.be.max-concurrent-streams: 100
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.tuning.get("tune.h2.be.glitches-threshold") == 10
        assert ir.global_config.tuning.get("tune.h2.be.initial-window-size") == 65536
        assert ir.global_config.tuning.get("tune.h2.be.max-concurrent-streams") == 100

        # Verify code generation
        assert "tune.h2.be.glitches-threshold 10" in output
        assert "tune.h2.be.initial-window-size 65536" in output
        assert "tune.h2.be.max-concurrent-streams 100" in output

    def test_global_h2_tuning_frontend(self, parser, codegen):
        """Test HTTP/2 frontend tuning directives (tune.h2.fe.*)."""
        source = """
        config test {
            global {
                daemon: true
                tune.h2.fe.glitches-threshold: 20
                tune.h2.fe.initial-window-size: 131072
                tune.h2.fe.max-concurrent-streams: 200
                tune.h2.fe.max-total-streams: 500
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.tuning.get("tune.h2.fe.glitches-threshold") == 20
        assert ir.global_config.tuning.get("tune.h2.fe.initial-window-size") == 131072
        assert ir.global_config.tuning.get("tune.h2.fe.max-concurrent-streams") == 200
        assert ir.global_config.tuning.get("tune.h2.fe.max-total-streams") == 500

        # Verify code generation
        assert "tune.h2.fe.glitches-threshold 20" in output
        assert "tune.h2.fe.initial-window-size 131072" in output
        assert "tune.h2.fe.max-concurrent-streams 200" in output
        assert "tune.h2.fe.max-total-streams 500" in output

    def test_global_h2_tuning_general(self, parser, codegen):
        """Test HTTP/2 general tuning directives (tune.h2.*)."""
        source = """
        config test {
            global {
                daemon: true
                tune.h2.header-table-size: 8192
                tune.h2.initial-window-size: 65536
                tune.h2.max-concurrent-streams: 150
                tune.h2.max-frame-size: 32768
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.tuning.get("tune.h2.header-table-size") == 8192
        assert ir.global_config.tuning.get("tune.h2.initial-window-size") == 65536
        assert ir.global_config.tuning.get("tune.h2.max-concurrent-streams") == 150
        assert ir.global_config.tuning.get("tune.h2.max-frame-size") == 32768

        # Verify code generation
        assert "tune.h2.header-table-size 8192" in output
        assert "tune.h2.initial-window-size 65536" in output
        assert "tune.h2.max-concurrent-streams 150" in output
        assert "tune.h2.max-frame-size 32768" in output

    def test_global_http_tuning(self, parser, codegen):
        """Test HTTP tuning directives (tune.http.*)."""
        source = """
        config test {
            global {
                daemon: true
                tune.http.maxhdr: 200
                tune.http.cookielen: 8192
                tune.http.logurilen: 2048
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.tuning.get("tune.http.maxhdr") == 200
        assert ir.global_config.tuning.get("tune.http.cookielen") == 8192
        assert ir.global_config.tuning.get("tune.http.logurilen") == 2048

        # Verify code generation
        assert "tune.http.maxhdr 200" in output
        assert "tune.http.cookielen 8192" in output
        assert "tune.http.logurilen 2048" in output

    def test_global_phase2_comprehensive(self, parser, codegen):
        """Test all Phase 2 directives together in production configuration."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 50000

                // Master-worker mode
                master-worker: true
                mworker-max-reloads: 5

                // Buffer tuning
                maxpipes: 16384
                tune.bufsize: 65536
                tune.maxrewrite: 16384

                // SSL/TLS paths
                ca-base: "/etc/ssl/certs"
                crt-base: "/etc/ssl/private"
                key-base: "/etc/ssl/keys"

                // SSL/TLS configuration
                ssl-default-bind-ciphersuites: "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"
                ssl-default-server-ciphersuites: "TLS_CHACHA20_POLY1305_SHA256"
                ssl-default-server-options: ["no-sslv3", "no-tlsv10"]
                ssl-engine: "aesni"

                // SSL tuning
                tune.ssl.bufsize: 32768
                tune.ssl.cachesize: 200000
                tune.ssl.lifetime: "10m"
                tune.ssl.default-dh-param: 2048

                // HTTP/2 tuning
                tune.h2.initial-window-size: 65536
                tune.h2.max-concurrent-streams: 100
                tune.h2.max-frame-size: 16384

                // HTTP tuning
                tune.http.maxhdr: 100
                tune.http.cookielen: 4096
            }

            frontend https {
                bind *:443
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

        # Verify all directives in output
        assert "master-worker" in output
        assert "mworker-max-reloads 5" in output
        assert "maxpipes 16384" in output
        assert "tune.bufsize 65536" in output
        assert "key-base /etc/ssl/keys" in output
        assert "ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384" in output
        assert "ssl-default-server-ciphersuites TLS_CHACHA20_POLY1305_SHA256" in output
        assert "ssl-default-server-options no-sslv3" in output
        assert "ssl-engine aesni" in output
        assert "tune.ssl.bufsize 32768" in output
        assert "tune.h2.initial-window-size 65536" in output
        assert "tune.http.maxhdr 100" in output
