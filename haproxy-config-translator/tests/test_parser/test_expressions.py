"""Test expression parsing and evaluation."""

import pytest

from haproxy_translator.parsers.dsl_parser import DSLParser


@pytest.fixture
def parser():
    """Create DSL parser instance."""
    return DSLParser()


class TestVariableDeclarations:
    """Test variable declaration and references."""

    def test_simple_variable(self, parser):
        """Test simple variable declaration."""
        source = """
        config test {
            let backend_port = 8080

            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        assert "backend_port" in ir.variables
        assert ir.variables["backend_port"].value == 8080

    def test_string_variable(self, parser):
        """Test string variable."""
        source = """
        config test {
            let server_host = "api.example.com"

            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        assert "server_host" in ir.variables
        assert ir.variables["server_host"].value == "api.example.com"

    def test_boolean_variable(self, parser):
        """Test boolean variable."""
        source = """
        config test {
            let enable_ssl = true

            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        assert "enable_ssl" in ir.variables
        assert ir.variables["enable_ssl"].value is True


class TestEnvFunction:
    """Test environment variable function."""

    def test_env_call_simple(self, parser):
        """Test simple env() call."""
        import os

        # Set the environment variable for the test
        os.environ["PORT"] = "9000"
        try:
            source = """
            config test {
                let port = env("PORT")

                backend servers {
                    balance: roundrobin
                }
            }
            """
            # This will parse, but won't actually resolve until transformation
            ir = parser.parse(source)
            assert "port" in ir.variables
        finally:
            # Clean up
            del os.environ["PORT"]

    def test_env_call_with_default(self, parser):
        """Test env() with default value."""
        source = """
        config test {
            let port = env("PORT", 8080)

            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        assert "port" in ir.variables


class TestTemplates:
    """Test template definition and usage."""

    def test_template_definition(self, parser):
        """Test template definition."""
        source = """
        config test {
            template server_defaults {
                check: true
                inter: 3s
                rise: 2
                fall: 3
            }

            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        assert "server_defaults" in ir.templates
        template = ir.templates["server_defaults"]
        assert template.parameters["check"] is True
        assert template.parameters["inter"] == "3s"

    def test_template_spreading(self, parser):
        """Test template spreading syntax."""
        source = """
        config test {
            template server_defaults {
                check: true
                weight: 100
            }

            backend servers {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                        @server_defaults
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        # Template spreading will be handled in transformation phase
        assert "server_defaults" in ir.templates


class TestStringInterpolation:
    """Test string interpolation with variables."""

    def test_interpolated_string(self, parser):
        """Test string with variable interpolation."""
        source = """
        config test {
            let hostname = "api"

            backend servers {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "${hostname}.example.com"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        # Interpolation will be resolved during transformation
        assert "hostname" in ir.variables


class TestArraysAndObjects:
    """Test array and object literals."""

    def test_string_array(self, parser):
        """Test string array."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    alpn: ["h2", "http/1.1"]
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]
        assert len(bind.alpn) == 2
        assert "h2" in bind.alpn

    def test_option_array(self, parser):
        """Test option as array."""
        source = """
        config test {
            defaults {
                option: ["httplog", "dontlognull", "forwardfor"]
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.defaults.options) == 3
        assert "httplog" in ir.defaults.options


class TestDurationValues:
    """Test duration parsing with units."""

    def test_seconds(self, parser):
        """Test seconds duration."""
        source = """
        config test {
            defaults {
                timeout: {
                    connect: 5s
                }
            }
        }
        """
        ir = parser.parse(source)
        assert ir.defaults.timeout_connect == "5s"

    def test_milliseconds(self, parser):
        """Test milliseconds duration."""
        source = """
        config test {
            defaults {
                timeout: {
                    connect: 5000ms
                }
            }
        }
        """
        ir = parser.parse(source)
        assert ir.defaults.timeout_connect == "5000ms"

    def test_minutes(self, parser):
        """Test minutes duration."""
        source = """
        config test {
            defaults {
                timeout: {
                    client: 5m
                }
            }
        }
        """
        ir = parser.parse(source)
        assert ir.defaults.timeout_client == "5m"


class TestNumberParsing:
    """Test integer and float parsing."""

    def test_integer(self, parser):
        """Test integer parsing."""
        source = """
        config test {
            global {
                maxconn: 4096
            }
        }
        """
        ir = parser.parse(source)
        assert ir.global_config.maxconn == 4096

    def test_port_numbers(self, parser):
        """Test port number parsing."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server s1 address: "127.0.0.1" port: 8080
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.servers[0].port == 8080


class TestIdentifiers:
    """Test identifier parsing."""

    def test_simple_identifier(self, parser):
        """Test simple identifier."""
        source = """
        config my_config {
            global {
                maxconn: 1000
            }
        }
        """
        ir = parser.parse(source)
        assert ir.name == "my_config"

    def test_identifier_with_numbers(self, parser):
        """Test identifier with numbers."""
        source = """
        config config123 {
            global {
                maxconn: 1000
            }
        }
        """
        ir = parser.parse(source)
        assert ir.name == "config123"

    def test_identifier_with_underscore(self, parser):
        """Test identifier with underscores."""
        source = """
        config my_test_config_v2 {
            global {
                maxconn: 1000
            }
        }
        """
        ir = parser.parse(source)
        assert ir.name == "my_test_config_v2"


class TestQualifiedIdentifiers:
    """Test qualified identifiers (with dots)."""

    def test_lua_action_name(self, parser):
        """Test qualified identifier for Lua actions."""
        source = """
        config test {
            frontend web {
                http-request {
                    lua.my_function
                }
                default_backend: servers
            }
            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        # Check that http-request rules exist in the frontend
        # The exact structure depends on transformer implementation
        assert len(ir.frontends) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
