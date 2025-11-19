"""Tests for external-check directives (external health check programs)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestExternalCheckCommand:
    """Test external-check command directive."""

    def test_backend_external_check_command(self):
        """Test backend external-check command directive."""
        config = """
        config test {
            backend app {
                mode: http
                external-check command: "/usr/local/bin/health-check.sh"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].external_check_command == "/usr/local/bin/health-check.sh"

    def test_backend_external_check_command_codegen(self):
        """Test backend external-check command code generation."""
        config = """
        config test {
            backend app {
                mode: http
                external-check command: "/usr/local/bin/health-check.sh"
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

        assert "external-check command /usr/local/bin/health-check.sh" in output
        assert "backend app" in output


class TestExternalCheckPath:
    """Test external-check path directive."""

    def test_backend_external_check_path(self):
        """Test backend external-check path directive."""
        config = """
        config test {
            backend app {
                mode: http
                external-check path: "/usr/local/bin:/usr/bin:/bin"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].external_check_path == "/usr/local/bin:/usr/bin:/bin"

    def test_backend_external_check_path_codegen(self):
        """Test backend external-check path code generation."""
        config = """
        config test {
            backend app {
                mode: http
                external-check path: "/usr/local/bin:/usr/bin:/bin"
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

        assert "external-check path /usr/local/bin:/usr/bin:/bin" in output


class TestExternalCheckIntegration:
    """Integration tests for external-check directives."""

    def test_backend_both_external_check_directives(self):
        """Test backend with both external-check command and path."""
        config = """
        config test {
            backend app {
                mode: http
                external-check command: "/usr/local/bin/health-check.sh"
                external-check path: "/usr/local/bin:/usr/bin:/bin"
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

        assert backend.external_check_command == "/usr/local/bin/health-check.sh"
        assert backend.external_check_path == "/usr/local/bin:/usr/bin:/bin"

    def test_backend_external_check_codegen_complete(self):
        """Test complete external-check code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                external-check command: "/usr/local/bin/health-check.sh"
                external-check path: "/usr/local/bin:/usr/bin"
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
        assert "external-check command /usr/local/bin/health-check.sh" in output
        assert "external-check path /usr/local/bin:/usr/bin" in output
        assert "server app1 10.0.1.1:8080 check" in output
        assert "server app2 10.0.1.2:8080 check" in output

    def test_backend_without_external_check(self):
        """Test backend without external-check (should be None)."""
        config = """
        config test {
            backend web {
                mode: http
                servers {
                    server web1 { address: "192.168.1.10" port: 80 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        backend = ir.backends[0]

        assert backend.external_check_command is None
        assert backend.external_check_path is None

    def test_multiple_backends_different_external_checks(self):
        """Test multiple backends with different external checks."""
        config = """
        config test {
            backend app1 {
                mode: http
                external-check command: "/checks/app1-check.sh"
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }

            backend app2 {
                mode: http
                external-check command: "/checks/app2-check.py"
                external-check path: "/usr/bin"
                servers {
                    server s2 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].external_check_command == "/checks/app1-check.sh"
        assert ir.backends[0].external_check_path is None
        assert ir.backends[1].external_check_command == "/checks/app2-check.py"
        assert ir.backends[1].external_check_path == "/usr/bin"
