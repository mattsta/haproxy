"""Tests to cover variable_resolver coverage gaps."""

import os
import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestVariableResolverCoverage:
    """Test cases to achieve 100% variable_resolver coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_resolve_dict_value(self, parser, codegen):
        """Test resolving dictionary values with variables."""
        source = """
        config test {
            let port = 8080

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: ${port}
                        minconn: 10
                        maxconn: 100
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "10.0.1.10:8080" in output

    def test_resolve_list_value(self, parser, codegen):
        """Test resolving list values with variables."""
        source = """
        config test {
            let proto = "h2"

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                        alpn: ["${proto}", "http/1.1"]
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "alpn h2,http/1.1" in output

    def test_resolve_global_lua_scripts(self, parser, codegen):
        """Test resolving lua scripts in global config."""
        source = """
        config test {
            let lua_file = "/etc/haproxy/auth.lua"

            global {
                daemon: true
                lua {
                    source_type: "file"
                    content: "${lua_file}"
                }
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
        assert "lua-load /etc/haproxy/auth.lua" in output

    def test_server_port_as_string(self, parser, codegen):
        """Test server port resolution when it's a non-numeric string."""
        source = """
        config test {
            let port_var = "http"

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: "${port_var}"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        # Port should be kept as string if not a valid integer
        assert "10.0.1.10:http" in output or "10.0.1.10 http" in output

    def test_lua_script_file_resolution(self, parser, codegen):
        """Test lua script content resolution for file type."""
        source = """
        config test {
            let script_path = "/etc/haproxy/custom.lua"

            global {
                daemon: true
                lua {
                    source_type: "file"
                    content: "${script_path}"
                }
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
        assert "lua-load /etc/haproxy/custom.lua" in output

    def test_env_function_with_fallback(self, parser, codegen):
        """Test env() function with fallback when var not set."""
        # Set a test env var
        os.environ["TEST_BACKEND_PORT"] = "9000"

        source = """
        config test {
            let port = env("TEST_BACKEND_PORT")

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: ${port}
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "10.0.1.10:9000" in output

        # Cleanup
        del os.environ["TEST_BACKEND_PORT"]

    def test_env_function_undefined_with_default(self, parser, codegen):
        """Test env() function with default value when var not set."""
        # Ensure var is not set
        if "NONEXISTENT_VAR" in os.environ:
            del os.environ["NONEXISTENT_VAR"]

        source = """
        config test {
            let port = env("NONEXISTENT_VAR", "8080")

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: ${port}
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "10.0.1.10:8080" in output

    def test_env_function_undefined_no_default(self, parser, codegen):
        """Test env() function raises error when var not set and no default."""
        # Ensure var is not set
        if "UNDEFINED_VAR_NO_DEFAULT" in os.environ:
            del os.environ["UNDEFINED_VAR_NO_DEFAULT"]

        source = """
        config test {
            let port = env("UNDEFINED_VAR_NO_DEFAULT")

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: ${port}
                    }
                }
            }
        }
        """
        from haproxy_translator.utils.errors import ParseError

        with pytest.raises(ParseError, match="Environment variable not set"):
            ir = parser.parse(source)
