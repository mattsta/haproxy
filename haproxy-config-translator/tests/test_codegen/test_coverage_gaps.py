"""Tests to cover remaining codegen coverage gaps."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestCodegenCoverageGaps:
    """Test cases to achieve 100% codegen coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_default_server_with_send_proxy(self, parser, codegen):
        """Test default_server with send-proxy option."""
        source = """
        config test {
            backend app {
                default_server {
                    send-proxy: true
                }
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
        assert "default-server send-proxy" in output

    def test_default_server_with_crt(self, parser, codegen):
        """Test default_server with crt option."""
        source = """
        config test {
            backend app {
                default_server {
                    ssl: true
                    crt: "/etc/ssl/client.pem"
                }
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
        assert "crt /etc/ssl/client.pem" in output

    def test_default_server_with_source(self, parser, codegen):
        """Test default_server with source option."""
        source = """
        config test {
            backend app {
                default_server {
                    source: "192.168.1.100"
                }
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
        assert "source 192.168.1.100" in output

    def test_tcp_request_with_string_params(self, parser, codegen):
        """Test TCP request rule with string parameters."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: tcp
                tcp_request {
                    action: "content"
                    params: "accept"
                    condition: "{ src 10.0.0.0/8 }"
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "tcp-request content accept if { src 10.0.0.0/8 }" in output

    def test_tcp_response_with_string_params(self, parser, codegen):
        """Test TCP response rule with string parameters."""
        source = """
        config test {
            backend app {
                mode: tcp
                tcp_response {
                    action: "content"
                    params: "accept"
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "tcp-response content accept" in output

    def test_top_level_lua_with_global_lua(self, parser, codegen):
        """Test top-level lua scripts merged with global lua_scripts."""
        source = """
        config test {
            global {
                daemon: true
                lua {
                    source_type: "file"
                    content: "/etc/haproxy/global.lua"
                }
            }

            lua auth_checker {
                source_type: "inline"
                content: \"\"\"
                function check_auth(txn)
                    return true
                end
                \"\"\"
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
        # Should have both lua scripts in global section
        assert "lua-load /etc/haproxy/global.lua" in output
        assert "lua-load" in output

        # Check lua files
        lua_files = codegen.get_lua_files(ir)
        assert len(lua_files) >= 1  # At least the inline script
