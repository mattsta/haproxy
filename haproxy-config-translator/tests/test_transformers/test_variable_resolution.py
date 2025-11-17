"""Tests for variable resolution transformer."""


import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.transformers.variable_resolver import VariableResolver
from haproxy_translator.utils.errors import ParseError


class TestVariableResolution:
    """Test variable resolution functionality."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_string_interpolation_in_address(self, parser):
        """Test ${var} interpolation in server address."""
        source = """
        config test {
            let host = "10.0.1.1"

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "${host}"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        # Check that ${host} was substituted
        server = ir.backends[0].servers[0]
        assert server.address == "10.0.1.1"

    def test_string_interpolation_in_bind(self, parser):
        """Test ${var} interpolation in bind address."""
        source = """
        config test {
            let listen_ip = "0.0.0.0"
            let listen_port = "8080"

            frontend web {
                bind ${listen_ip}:${listen_port}
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        # Check that ${listen_ip} and ${listen_port} were substituted
        bind = ir.frontends[0].binds[0]
        assert bind.address == "0.0.0.0:8080"

    def test_multiple_variables_in_string(self, parser):
        """Test multiple ${var} in a single string."""
        source = """
        config test {
            let prefix = "api"
            let domain = "example.com"

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "${prefix}.${domain}"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        server = ir.backends[0].servers[0]
        assert server.address == "api.example.com"

    def test_nested_variable_resolution(self, parser):
        """Test variable referencing another variable."""
        source = """
        config test {
            let port = 8080
            let addr = "10.0.1.1:${port}"

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "${addr}"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        server = ir.backends[0].servers[0]
        # First pass resolves ${port} in addr, second pass resolves ${addr}
        assert server.address == "10.0.1.1:8080"

    def test_undefined_variable_raises_error(self, parser):
        """Test that referencing undefined variable raises error."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "${undefined_var}"
                        port: 8080
                    }
                }
            }
        }
        """
        # Variable resolution is now integrated into parser
        # Should raise ParseError for undefined variable during parse
        with pytest.raises(ParseError, match="Undefined variable"):
            parser.parse(source)

    def test_env_variable_resolution(self, parser, monkeypatch):
        """Test env() function resolves environment variables."""
        monkeypatch.setenv("TEST_HOST", "test.example.com")

        source = """
        config test {
            let host = env("TEST_HOST")

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "${host}"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Check that env() was resolved during parsing
        assert ir.variables["host"].value == "test.example.com"

        # Now resolve ${host} interpolation
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        server = ir.backends[0].servers[0]
        assert server.address == "test.example.com"

    def test_env_variable_with_default(self, parser):
        """Test env() function with default value."""
        # Don't set the environment variable
        source = """
        config test {
            let host = env("NONEXISTENT_VAR", "default.example.com")

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "${host}"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Check that default was used
        assert ir.variables["host"].value == "default.example.com"

        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        server = ir.backends[0].servers[0]
        assert server.address == "default.example.com"

    def test_boolean_variable_conversion(self, parser):
        """Test that boolean variables are converted to strings properly."""
        source = """
        config test {
            let ssl_enabled = true

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        verify: "${ssl_enabled}"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        server = ir.backends[0].servers[0]
        # Boolean true should be converted to "true"
        assert server.ssl_verify == "true"

    def test_number_variable_conversion(self, parser):
        """Test that number variables are converted to strings."""
        source = """
        config test {
            let port_num = 8080

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1:${port_num}"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        server = ir.backends[0].servers[0]
        assert server.address == "10.0.1.1:8080"

    def test_variables_in_acl(self, parser):
        """Test variable interpolation in ACL definitions."""
        source = """
        config test {
            let path_prefix = "/api"

            frontend web {
                bind *:80

                acl {
                    is_api path_beg "${path_prefix}"
                }

                default_backend: servers
            }

            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        acl = ir.frontends[0].acls[0]
        # Check that ${path_prefix} was substituted in ACL values
        assert "/api" in acl.values

    def test_no_variables_remains_unchanged(self, parser):
        """Test that config without variables is unchanged."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        original_address = ir.backends[0].servers[0].address

        resolver = VariableResolver(ir)
        ir = resolver.resolve()

        # Address should be unchanged
        assert ir.backends[0].servers[0].address == original_address


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
