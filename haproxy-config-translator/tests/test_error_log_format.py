"""Tests for error-log-format and related log format directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestDefaultsErrorLogFormat:
    """Test defaults error-log-format directive."""

    def test_defaults_error_log_format(self):
        """Test defaults error-log-format directive parsing."""
        config = """
        config test {
            defaults {
                mode: http
                error-log-format: "%ci:%cp [%t] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Tt %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"
            }

            frontend web {
                bind *:80
                mode: http
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults is not None
        assert (
            ir.defaults.error_log_format
            == "%ci:%cp [%t] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Tt %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"
        )

    def test_defaults_error_log_format_codegen(self):
        """Test defaults error-log-format code generation."""
        config = """
        config test {
            defaults {
                mode: http
                error-log-format: "%ci:%cp [%t] %ft %b/%s"
            }

            frontend web {
                bind *:80
                mode: http
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "error-log-format %ci:%cp [%t] %ft %b/%s" in output
        assert "defaults" in output


class TestFrontendErrorLogFormat:
    """Test frontend error-log-format directive."""

    def test_frontend_error_log_format(self):
        """Test frontend error-log-format directive parsing."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                error-log-format: "%ci:%cp [%t] %ft %b/%s %ST %B"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert ir.frontends[0].error_log_format == "%ci:%cp [%t] %ft %b/%s %ST %B"

    def test_frontend_error_log_format_codegen(self):
        """Test frontend error-log-format code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                error-log-format: "%ci:%cp [%t] %ft"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "error-log-format %ci:%cp [%t] %ft" in output
        assert "frontend web" in output


class TestListenLogFormats:
    """Test listen log format directives."""

    def test_listen_log_tag(self):
        """Test listen log-tag directive."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                log-tag: "app-server"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert ir.listens[0].log_tag == "app-server"

    def test_listen_log_format(self):
        """Test listen log-format directive."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                log-format: "%ci:%cp [%t] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Tt"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].log_format == "%ci:%cp [%t] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Tt"

    def test_listen_error_log_format(self):
        """Test listen error-log-format directive."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                error-log-format: "%ci:%cp [%t] %ft %b/%s %ST %B"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].error_log_format == "%ci:%cp [%t] %ft %b/%s %ST %B"

    def test_listen_log_format_sd(self):
        """Test listen log-format-sd directive."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                log-format-sd: "[exampleSDID@1234]"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].log_format_sd == "[exampleSDID@1234]"

    def test_listen_all_log_formats(self):
        """Test listen with all log format directives."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                log-tag: "app-server"
                log-format: "%ci:%cp [%t] %ft"
                error-log-format: "%ci:%cp [%t] %ST"
                log-format-sd: "[exampleSDID@1234]"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        listen = ir.listens[0]

        assert listen.log_tag == "app-server"
        assert listen.log_format == "%ci:%cp [%t] %ft"
        assert listen.error_log_format == "%ci:%cp [%t] %ST"
        assert listen.log_format_sd == "[exampleSDID@1234]"

    def test_listen_log_formats_codegen(self):
        """Test listen log format code generation."""
        config = """
        config test {
            listen app {
                bind *:8080
                mode: http
                log-tag: "app-server"
                log-format: "%ci:%cp [%t] %ft"
                error-log-format: "%ci:%cp [%t] %ST"
                log-format-sd: "[exampleSDID@1234]"
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
        assert "log-tag app-server" in output
        assert "log-format %ci:%cp [%t] %ft" in output
        assert "error-log-format %ci:%cp [%t] %ST" in output
        assert "log-format-sd [exampleSDID@1234]" in output


class TestErrorLogFormatIntegration:
    """Integration tests for error-log-format directive."""

    def test_defaults_with_error_log_format(self):
        """Test defaults with error-log-format inherited by frontend."""
        config = """
        config test {
            defaults {
                mode: http
                error-log-format: "%ci:%cp [%t] %ft %b/%s"
            }

            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }

            backend app {
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

        assert "defaults" in output
        assert "error-log-format %ci:%cp [%t] %ft %b/%s" in output

    def test_frontend_override_defaults_error_log_format(self):
        """Test frontend overriding defaults error-log-format."""
        config = """
        config test {
            defaults {
                mode: http
                error-log-format: "%ci:%cp [%t]"
            }

            frontend web {
                bind *:80
                mode: http
                error-log-format: "%ci:%cp [%t] %ft %b/%s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Defaults has one format
        assert ir.defaults.error_log_format == "%ci:%cp [%t]"

        # Frontend has different format
        assert ir.frontends[0].error_log_format == "%ci:%cp [%t] %ft %b/%s"

    def test_complex_error_log_format(self):
        """Test complex error-log-format with special characters."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                error-log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Should contain the full format string
        assert "error-log-format %ci:%cp [%tr] %ft %b/%s" in output
        assert "%TR/%Tw/%Tc/%Tr/%Ta %ST %B" in output

    def test_listen_without_log_formats(self):
        """Test listen without any log format directives (should be None)."""
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
        listen = ir.listens[0]

        assert listen.log_tag is None
        assert listen.log_format is None
        assert listen.error_log_format is None
        assert listen.log_format_sd is None
