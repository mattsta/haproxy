"""Tests for load-server-state-from-file directive (server state reload)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestBackendLoadServerState:
    """Test backend load-server-state-from-file directive."""

    def test_backend_load_server_state_global(self):
        """Test backend with load-server-state-from-file global."""
        config = """
        config test {
            backend app {
                mode: http
                load-server-state-from-file: global
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].load_server_state_from.value == "global"

    def test_backend_load_server_state_local(self):
        """Test backend with load-server-state-from-file local."""
        config = """
        config test {
            backend app {
                mode: http
                load-server-state-from-file: local
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].load_server_state_from.value == "local"

    def test_backend_load_server_state_none(self):
        """Test backend with load-server-state-from-file none."""
        config = """
        config test {
            backend app {
                mode: http
                load-server-state-from-file: none
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].load_server_state_from.value == "none"

    def test_backend_load_server_state_codegen(self):
        """Test backend load-server-state-from-file code generation."""
        config = """
        config test {
            backend app {
                mode: http
                load-server-state-from-file: global
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

        assert "load-server-state-from-file global" in output
        assert "backend app" in output


class TestListenLoadServerState:
    """Test listen load-server-state-from-file directive."""

    def test_listen_load_server_state_global(self):
        """Test listen with load-server-state-from-file global."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                load-server-state-from-file: global
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert ir.listens[0].load_server_state_from.value == "global"

    def test_listen_load_server_state_codegen(self):
        """Test listen load-server-state-from-file code generation."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                load-server-state-from-file: local
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

        assert "load-server-state-from-file local" in output
        assert "listen app" in output


class TestLoadServerStateIntegration:
    """Integration tests for load-server-state-from-file directive."""

    def test_multiple_backends_different_modes(self):
        """Test multiple backends with different load modes."""
        config = """
        config test {
            backend app1 {
                mode: http
                load-server-state-from-file: global
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }

            backend app2 {
                mode: http
                load-server-state-from-file: local
                servers {
                    server s2 { address: "10.0.2.1" port: 8080 }
                }
            }

            backend app3 {
                mode: http
                load-server-state-from-file: none
                servers {
                    server s3 { address: "10.0.3.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 3
        assert ir.backends[0].load_server_state_from.value == "global"
        assert ir.backends[1].load_server_state_from.value == "local"
        assert ir.backends[2].load_server_state_from.value == "none"

    def test_backend_without_load_server_state(self):
        """Test backend without load-server-state-from-file (should be None)."""
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
        assert ir.backends[0].load_server_state_from is None

    def test_backend_with_all_values_codegen(self):
        """Test complete backend config with all load-server-state-from values."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                load-server-state-from-file: global
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
        assert "mode http" in output
        assert "balance roundrobin" in output
        assert "load-server-state-from-file global" in output
        assert "server app1 10.0.1.1:8080 check" in output
        assert "server app2 10.0.1.2:8080 check" in output
