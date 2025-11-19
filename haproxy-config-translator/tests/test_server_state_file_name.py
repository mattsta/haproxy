"""Tests for server-state-file-name directive (server state file specification)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestBackendServerStateFileName:
    """Test backend server-state-file-name directive."""

    def test_backend_server_state_file_name_use_backend_name(self):
        """Test backend with server-state-file-name: use-backend-name."""
        config = """
        config test {
            backend app {
                mode: http
                server-state-file-name: use-backend-name
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].server_state_file_name == "use-backend-name"

    def test_backend_server_state_file_name_custom_path(self):
        """Test backend with server-state-file-name custom file path."""
        config = """
        config test {
            backend app {
                mode: http
                server-state-file-name: "/var/lib/haproxy/state/backend-app.state"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].server_state_file_name == "/var/lib/haproxy/state/backend-app.state"

    def test_backend_server_state_file_name_codegen_use_backend_name(self):
        """Test backend server-state-file-name code generation with use-backend-name."""
        config = """
        config test {
            backend app {
                mode: http
                server-state-file-name: use-backend-name
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "server-state-file-name use-backend-name" in output
        assert "backend app" in output

    def test_backend_server_state_file_name_codegen_custom_path(self):
        """Test backend server-state-file-name code generation with custom path."""
        config = """
        config test {
            backend app {
                mode: http
                server-state-file-name: "/var/lib/haproxy/app.state"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "server-state-file-name /var/lib/haproxy/app.state" in output
        assert "backend app" in output

    def test_backend_without_server_state_file_name(self):
        """Test backend without server-state-file-name (should be None)."""
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
        assert ir.backends[0].server_state_file_name is None


class TestListenServerStateFileName:
    """Test listen server-state-file-name directive."""

    def test_listen_server_state_file_name_use_backend_name(self):
        """Test listen with server-state-file-name: use-backend-name."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                server-state-file-name: use-backend-name
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert ir.listens[0].server_state_file_name == "use-backend-name"

    def test_listen_server_state_file_name_custom_path(self):
        """Test listen with server-state-file-name custom file path."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                server-state-file-name: "/var/state/listen-app.state"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].server_state_file_name == "/var/state/listen-app.state"

    def test_listen_server_state_file_name_codegen(self):
        """Test listen server-state-file-name code generation."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                server-state-file-name: use-backend-name
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "server-state-file-name use-backend-name" in output
        assert "listen app" in output

    def test_listen_without_server_state_file_name(self):
        """Test listen without server-state-file-name (should be None)."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].server_state_file_name is None


class TestServerStateFileNameIntegration:
    """Integration tests for server-state-file-name directive."""

    def test_backend_with_load_server_state_and_file_name(self):
        """Test backend with both load-server-state-from-file and server-state-file-name."""
        config = """
        config test {
            backend app {
                mode: http
                load-server-state-from-file: local
                server-state-file-name: use-backend-name
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        backend = ir.backends[0]

        assert backend.load_server_state_from.value == "local"
        assert backend.server_state_file_name == "use-backend-name"

    def test_backend_server_state_codegen_complete(self):
        """Test complete backend with both server state directives."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                load-server-state-from-file: local
                server-state-file-name: "/var/lib/haproxy/app.state"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 check: true }
                    server app2 { address: "10.0.1.2" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend app" in output
        assert "load-server-state-from-file local" in output
        assert "server-state-file-name /var/lib/haproxy/app.state" in output
        assert "server app1 10.0.1.1:8080 check" in output
        assert "server app2 10.0.1.2:8080 check" in output

    def test_multiple_backends_different_file_names(self):
        """Test multiple backends with different server-state-file-name values."""
        config = """
        config test {
            backend app1 {
                mode: http
                server-state-file-name: use-backend-name
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }

            backend app2 {
                mode: http
                server-state-file-name: "/var/state/app2.state"
                servers {
                    server s2 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].server_state_file_name == "use-backend-name"
        assert ir.backends[1].server_state_file_name == "/var/state/app2.state"

    def test_listen_with_load_server_state_and_file_name(self):
        """Test listen with both load-server-state-from-file and server-state-file-name."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                load-server-state-from-file: local
                server-state-file-name: "/var/state/listen.state"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "listen app" in output
        assert "load-server-state-from-file local" in output
        assert "server-state-file-name /var/state/listen.state" in output
