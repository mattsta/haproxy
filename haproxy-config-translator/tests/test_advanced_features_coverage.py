"""Advanced feature coverage tests for HAProxy DSL transformer."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestCompressionFeatures:
    """Test compression features coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_compression_with_algo_and_types(self, parser, codegen):
        """Test compression with algorithm and types."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                compression {
                    algo: "gzip"
                    type: ["text/html", "text/plain", "application/json"]
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "compression algo gzip" in output
        assert "compression type" in output


class TestServerOptions:
    """Test server options coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_server_with_check_enabled(self, parser, codegen):
        """Test server with health check options."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                        check: true
                        rise: 3
                        fall: 2
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "check" in output
        assert "rise 3" in output
        assert "fall 2" in output

    def test_server_with_backup_flag(self, parser, codegen):
        """Test server with backup flag."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                    server s2 {
                        address: "10.0.0.2"
                        port: 8080
                        backup: true
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "backup" in output


class TestMailersSection:
    """Test mailers section coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_mailers_section(self, parser, codegen):
        """Test mailers section configuration."""
        source = '''
        config test {
            mailers alert_mailers {
                timeout_mail: 20s
                mailer smtp1 "smtp.example.com" 25
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "mailers alert_mailers" in output
        assert "timeout mail 20s" in output
        assert "mailer smtp1 smtp.example.com:25" in output


class TestPeersSection:
    """Test peers section coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_peers_section(self, parser, codegen):
        """Test peers section configuration."""
        source = '''
        config test {
            peers mypeers {
                peer haproxy1 "192.168.1.1" 10000
                peer haproxy2 "192.168.1.2" 10000
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "peers mypeers" in output
        assert "peer haproxy1 192.168.1.1:10000" in output
        assert "peer haproxy2 192.168.1.2:10000" in output


class TestGlobalLuaConfiguration:
    """Test global Lua configuration coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_lua_load(self, parser, codegen):
        """Test global lua-load directive."""
        source = '''
        config test {
            global {
                lua-load "/etc/haproxy/lua/helpers.lua"
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "lua-load /etc/haproxy/lua/helpers.lua" in output

    def test_global_lua_prepend_path(self, parser, codegen):
        """Test global lua-prepend-path directive."""
        source = '''
        config test {
            global {
                lua-prepend-path "/etc/haproxy/lua"
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "lua-prepend-path /etc/haproxy/lua" in output


class TestFrontendCapture:
    """Test frontend capture directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_declare_capture(self, parser, codegen):
        """Test frontend declare capture directive."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture request len 64
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers { server s1 { address: "10.0.0.1" port: 8080 } }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "declare capture request len 64" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
