"""Tests for errorfiles directive (custom error files directory reference)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestBackendErrorfiles:
    """Test backend errorfiles directive."""

    def test_backend_errorfiles(self):
        """Test backend errorfiles directive parsing."""
        config = """
        config test {
            backend app {
                mode: http
                errorfiles: "custom_errors"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].errorfiles == "custom_errors"

    def test_backend_errorfiles_codegen(self):
        """Test backend errorfiles code generation."""
        config = """
        config test {
            backend app {
                mode: http
                errorfiles: "error_pages"
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

        assert "errorfiles error_pages" in output
        assert "backend app" in output

    def test_backend_without_errorfiles(self):
        """Test backend without errorfiles (should be None)."""
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
        assert ir.backends[0].errorfiles is None

    def test_backend_errorfiles_simple_name(self):
        """Test errorfiles with simple name."""
        config = """
        config test {
            backend web {
                mode: http
                errorfiles: "myerrors"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].errorfiles == "myerrors"

    def test_backend_errorfiles_with_underscores(self):
        """Test errorfiles name with underscores."""
        config = """
        config test {
            backend api {
                mode: http
                errorfiles: "api_error_pages"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].errorfiles == "api_error_pages"

    def test_backend_errorfiles_with_dashes(self):
        """Test errorfiles name with dashes."""
        config = """
        config test {
            backend service {
                mode: http
                errorfiles: "service-errors"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].errorfiles == "service-errors"


class TestErrorfilesIntegration:
    """Integration tests for errorfiles directive."""

    def test_multiple_backends_different_errorfiles(self):
        """Test multiple backends with different errorfiles."""
        config = """
        config test {
            backend web {
                mode: http
                errorfiles: "web_errors"
                servers {
                    server web1 { address: "10.0.1.1" port: 80 }
                }
            }

            backend api {
                mode: http
                errorfiles: "api_errors"
                servers {
                    server api1 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].errorfiles == "web_errors"
        assert ir.backends[1].errorfiles == "api_errors"

    def test_errorfiles_codegen_complete(self):
        """Test complete errorfiles configuration code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                errorfiles: "custom_http_errors"
                servers {
                    server app1 { address: "192.168.1.10" port: 8080 }
                    server app2 { address: "192.168.1.11" port: 8080 }
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
        assert "errorfiles custom_http_errors" in output
        assert "server app1 192.168.1.10:8080" in output
        assert "server app2 192.168.1.11:8080" in output

    def test_errorfiles_with_balance_algorithm(self):
        """Test errorfiles with different balance algorithms."""
        config = """
        config test {
            backend lb {
                mode: http
                balance: leastconn
                errorfiles: "lb_errors"
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "balance leastconn" in output
        assert "errorfiles lb_errors" in output

    def test_errorfiles_with_timeouts(self):
        """Test errorfiles with timeout configuration."""
        config = """
        config test {
            backend app {
                mode: http
                errorfiles: "timeout_errors"
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

        assert ir.backends[0].errorfiles == "timeout_errors"
        assert ir.backends[0].timeout_connect == "5s"
        assert ir.backends[0].timeout_server == "30s"

    def test_errorfiles_different_naming_styles(self):
        """Test errorfiles with different naming conventions."""
        naming_styles = [
            "simple",
            "with_underscores",
            "with-dashes",
            "CamelCase",
            "mixed_Style-123",
        ]

        for style in naming_styles:
            config = f"""
            config test {{
                backend app {{
                    mode: http
                    errorfiles: "{style}"
                    servers {{
                        server s1 {{ address: "10.0.1.1" port: 8080 }}
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.backends[0].errorfiles == style

    def test_errorfiles_with_http_options(self):
        """Test errorfiles with HTTP-specific options."""
        config = """
        config test {
            backend web {
                mode: http
                errorfiles: "web_error_templates"
                balance: roundrobin
                option: "httpchk"
                servers {
                    server web1 { address: "10.0.1.1" port: 80 check: true }
                    server web2 { address: "10.0.1.2" port: 80 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "errorfiles web_error_templates" in output
        assert "option httpchk" in output
        assert "server web1 10.0.1.1:80 check" in output

    def test_backend_some_with_errorfiles_some_without(self):
        """Test configuration where some backends have errorfiles and others don't."""
        config = """
        config test {
            backend with_errors {
                mode: http
                errorfiles: "custom_errors"
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }

            backend without_errors {
                mode: http
                servers {
                    server s2 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].errorfiles == "custom_errors"
        assert ir.backends[1].errorfiles is None

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # First backend should have errorfiles
        assert "errorfiles custom_errors" in output

        # Verify both backends are present
        assert "backend with_errors" in output
        assert "backend without_errors" in output
