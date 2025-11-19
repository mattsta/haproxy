"""Tests for http-reuse directive (connection reuse mode)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestBackendHttpReuse:
    """Test backend http-reuse directive."""

    def test_backend_http_reuse_never(self):
        """Test backend http-reuse with 'never' mode."""
        config = """
        config test {
            backend app {
                mode: http
                http-reuse: never
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].http_reuse == "never"

    def test_backend_http_reuse_safe(self):
        """Test backend http-reuse with 'safe' mode."""
        config = """
        config test {
            backend app {
                mode: http
                http-reuse: safe
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].http_reuse == "safe"

    def test_backend_http_reuse_aggressive(self):
        """Test backend http-reuse with 'aggressive' mode."""
        config = """
        config test {
            backend app {
                mode: http
                http-reuse: aggressive
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].http_reuse == "aggressive"

    def test_backend_http_reuse_always(self):
        """Test backend http-reuse with 'always' mode."""
        config = """
        config test {
            backend app {
                mode: http
                http-reuse: always
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].http_reuse == "always"

    def test_backend_http_reuse_codegen(self):
        """Test backend http-reuse code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                http-reuse: safe
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "http-reuse safe" in output
        assert "backend app" in output
        assert "balance roundrobin" in output

    def test_backend_without_http_reuse(self):
        """Test backend without http-reuse (should be None)."""
        config = """
        config test {
            backend app {
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].http_reuse is None


class TestHttpReuseIntegration:
    """Integration tests for http-reuse directive."""

    def test_multiple_backends_different_http_reuse(self):
        """Test multiple backends with different http-reuse modes."""
        config = """
        config test {
            backend app1 {
                mode: http
                http-reuse: never
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }

            backend app2 {
                mode: http
                http-reuse: safe
                servers {
                    server s2 { address: "10.0.2.1" port: 8080 }
                }
            }

            backend app3 {
                mode: http
                http-reuse: aggressive
                servers {
                    server s3 { address: "10.0.3.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 3
        assert ir.backends[0].http_reuse == "never"
        assert ir.backends[1].http_reuse == "safe"
        assert ir.backends[2].http_reuse == "aggressive"

    def test_http_reuse_codegen_complete(self):
        """Test complete http-reuse configuration code generation."""
        config = """
        config test {
            backend api {
                mode: http
                balance: leastconn
                http-reuse: aggressive
                option: "httpchk"
                servers {
                    server api1 { address: "192.168.1.10" port: 8080 check: true }
                    server api2 { address: "192.168.1.11" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend api" in output
        assert "mode http" in output
        assert "balance leastconn" in output
        assert "http-reuse aggressive" in output
        assert "option httpchk" in output
        assert "server api1 192.168.1.10:8080 check" in output
        assert "server api2 192.168.1.11:8080 check" in output

    def test_http_reuse_with_timeouts(self):
        """Test http-reuse with timeout configuration."""
        config = """
        config test {
            backend app {
                mode: http
                http-reuse: safe
                timeout_connect: 5s
                timeout_server: 30s
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].http_reuse == "safe"
        assert ir.backends[0].timeout_connect == "5s"
        assert ir.backends[0].timeout_server == "30s"

    def test_http_reuse_all_modes_codegen(self):
        """Test code generation for all http-reuse modes."""
        modes = ["never", "safe", "aggressive", "always"]

        for mode in modes:
            config = f"""
            config test {{
                backend app {{
                    mode: http
                    http-reuse: {mode}
                    servers {{
                        server s1 {{ address: "10.0.1.1" port: 8080 }}
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            codegen = HAProxyCodeGenerator()
            output = codegen.generate(ir)

            assert f"http-reuse {mode}" in output

    def test_http_reuse_with_keepalive_settings(self):
        """Test http-reuse with keep-alive related settings."""
        config = """
        config test {
            backend app {
                mode: http
                http-reuse: aggressive
                max-keep-alive-queue: 100
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].http_reuse == "aggressive"
        assert ir.backends[0].max_keep_alive_queue == 100
