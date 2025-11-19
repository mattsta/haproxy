"""Tests for proxy-level logging features (Phase 4C)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestFrontendLog:
    """Test log directive in frontend."""

    def test_frontend_log_global(self):
        """Test frontend with log global."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                log: "global"

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert len(ir.frontends[0].log) == 1
        assert ir.frontends[0].log[0] == "global"
        assert "log global" in output

    def test_frontend_log_specific(self):
        """Test frontend with specific log target."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                log: "127.0.0.1:514 local0"

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert len(ir.frontends[0].log) == 1
        assert ir.frontends[0].log[0] == "127.0.0.1:514 local0"
        assert "log 127.0.0.1:514 local0" in output

    def test_frontend_log_multiple(self):
        """Test frontend with multiple log targets."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                log: "127.0.0.1:514 local0"
                log: "127.0.0.1:515 local1"

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert len(ir.frontends[0].log) == 2
        assert "127.0.0.1:514 local0" in ir.frontends[0].log
        assert "127.0.0.1:515 local1" in ir.frontends[0].log
        assert "log 127.0.0.1:514 local0" in output
        assert "log 127.0.0.1:515 local1" in output


class TestFrontendLogTag:
    """Test log-tag directive in frontend."""

    def test_frontend_log_tag(self):
        """Test frontend with log-tag."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                log: "global"
                log-tag: "web-frontend"

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.frontends[0].log_tag == "web-frontend"
        assert "log-tag web-frontend" in output

    def test_frontend_log_and_tag_together(self):
        """Test frontend with both log and log-tag."""
        config = """
        config test {
            frontend api {
                bind *:443
                mode: http
                log: "127.0.0.1:514 local0 info"
                log-tag: "api-gateway"
                log-format: "%ci:%cp [%tr] %ft %b/%s"

                default_backend: api_backend
            }

            backend api_backend {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify IR
        frontend = ir.frontends[0]
        assert len(frontend.log) == 1
        assert frontend.log[0] == "127.0.0.1:514 local0 info"
        assert frontend.log_tag == "api-gateway"
        assert frontend.log_format == "%ci:%cp [%tr] %ft %b/%s"

        # Verify output
        assert "log 127.0.0.1:514 local0 info" in output
        assert "log-tag api-gateway" in output
        assert "log-format %ci:%cp [%tr] %ft %b/%s" in output


class TestBackendLog:
    """Test log directive in backend."""

    def test_backend_log_global(self):
        """Test backend with log global."""
        config = """
        config test {
            backend app {
                log: "global"

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert len(ir.backends[0].log) == 1
        assert ir.backends[0].log[0] == "global"
        assert "log global" in output

    def test_backend_log_specific(self):
        """Test backend with specific log target."""
        config = """
        config test {
            backend app {
                log: "127.0.0.1:514 local1 notice"

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert len(ir.backends[0].log) == 1
        assert ir.backends[0].log[0] == "127.0.0.1:514 local1 notice"
        assert "log 127.0.0.1:514 local1 notice" in output


class TestBackendLogTag:
    """Test log-tag directive in backend."""

    def test_backend_log_tag(self):
        """Test backend with log-tag."""
        config = """
        config test {
            backend app {
                log: "global"
                log-tag: "app-backend"

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].log_tag == "app-backend"
        assert "log-tag app-backend" in output

    def test_backend_log_and_tag_together(self):
        """Test backend with both log and log-tag."""
        config = """
        config test {
            backend database {
                mode: tcp
                log: "127.0.0.1:514 local2 warning"
                log-tag: "db-pool"
                log-format: "%ci:%cp [%t] %ft %b/%s %Tw/%Tc/%Tt"

                servers {
                    server db1 {
                        address: "10.0.2.1"
                        port: 5432
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify IR
        backend = ir.backends[0]
        assert len(backend.log) == 1
        assert backend.log[0] == "127.0.0.1:514 local2 warning"
        assert backend.log_tag == "db-pool"
        assert backend.log_format == "%ci:%cp [%t] %ft %b/%s %Tw/%Tc/%Tt"

        # Verify output
        assert "log 127.0.0.1:514 local2 warning" in output
        assert "log-tag db-pool" in output
        assert "log-format %ci:%cp [%t] %ft %b/%s %Tw/%Tc/%Tt" in output


class TestLoggingIntegration:
    """Test logging features in complete configurations."""

    def test_complete_logging_setup(self):
        """Test complete logging configuration across frontend and backend."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                log: "127.0.0.1:514 local0 info"
                log: "127.0.0.1:515 local1 notice"
                log-tag: "web-frontend"
                log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta"

                default_backend: app_backend
            }

            backend app_backend {
                mode: http
                balance: roundrobin

                log: "127.0.0.1:514 local2 warning"
                log-tag: "app-backend"
                log-format: "%ci:%cp [%t] %ft %b/%s %Tw/%Tc/%Tt"

                servers {
                    server app1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server app2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify frontend IR
        frontend = ir.frontends[0]
        assert len(frontend.log) == 2
        assert "127.0.0.1:514 local0 info" in frontend.log
        assert "127.0.0.1:515 local1 notice" in frontend.log
        assert frontend.log_tag == "web-frontend"
        assert frontend.log_format == "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta"

        # Verify backend IR
        backend = ir.backends[0]
        assert len(backend.log) == 1
        assert backend.log[0] == "127.0.0.1:514 local2 warning"
        assert backend.log_tag == "app-backend"
        assert backend.log_format == "%ci:%cp [%t] %ft %b/%s %Tw/%Tc/%Tt"

        # Verify output
        assert "frontend web" in output
        assert "log 127.0.0.1:514 local0 info" in output
        assert "log 127.0.0.1:515 local1 notice" in output
        assert "log-tag web-frontend" in output

        assert "backend app_backend" in output
        assert "log 127.0.0.1:514 local2 warning" in output
        assert "log-tag app-backend" in output

    def test_logging_with_monitoring(self):
        """Test logging combined with monitoring features."""
        config = """
        config production {
            frontend api {
                bind *:443
                mode: http

                monitor_uri: "/healthz"
                monitor-net "10.0.0.0/8"

                log: "127.0.0.1:514 local0"
                log-tag: "api-gateway"

                default_backend: api_backend
            }

            backend api_backend {
                mode: http
                balance: uri
                hash-type: consistent djb2

                log: "127.0.0.1:514 local1"
                log-tag: "api-backend"

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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify frontend
        frontend = ir.frontends[0]
        assert frontend.monitor_uri == "/healthz"
        assert len(frontend.monitor_net) == 1
        assert len(frontend.log) == 1
        assert frontend.log_tag == "api-gateway"

        # Verify backend
        backend = ir.backends[0]
        assert backend.hash_type == "consistent djb2"
        assert len(backend.log) == 1
        assert backend.log_tag == "api-backend"

        # Verify complete output
        assert "monitor-uri /healthz" in output
        assert "monitor-net 10.0.0.0/8" in output
        assert "log 127.0.0.1:514 local0" in output
        assert "log-tag api-gateway" in output
        assert "hash-type consistent djb2" in output
        assert "log 127.0.0.1:514 local1" in output
        assert "log-tag api-backend" in output
