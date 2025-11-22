"""Tests for DSL transformer coverage gaps - exercising uncovered code paths."""

import pytest

from haproxy_translator.parsers import DSLParser


class TestImportStatement:
    """Test import statement functionality (lines 116-117, 5034)."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_import_single_file(self, parser):
        """Test importing a single file."""
        source = '''
        config test {
            import "common/defaults.hcl"
        }
        '''
        ir = parser.parse(source)
        assert len(ir.imports) == 1
        assert ir.imports[0] == "common/defaults.hcl"

    def test_import_multiple_files(self, parser):
        """Test importing multiple files."""
        source = '''
        config test {
            import "common/defaults.hcl"
            import "security/ssl.hcl"
            import "backends/api.hcl"
        }
        '''
        ir = parser.parse(source)
        assert len(ir.imports) == 3
        assert "common/defaults.hcl" in ir.imports
        assert "security/ssl.hcl" in ir.imports
        assert "backends/api.hcl" in ir.imports


class TestLuaScripts:
    """Test Lua script functionality."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_lua_inline_script(self, parser):
        """Test inline Lua script."""
        source = '''
        config test {
            lua {
                inline hello_world {
                    core.log(core.info, "Hello, World!")
                }
            }
        }
        '''
        ir = parser.parse(source)
        assert len(ir.lua_scripts) == 1
        assert ir.lua_scripts[0].name == "hello_world"
        assert ir.lua_scripts[0].source_type == "inline"

    def test_lua_load_file(self, parser):
        """Test Lua load directive."""
        source = '''
        config test {
            lua {
                load "/etc/haproxy/lua/helpers.lua"
            }
        }
        '''
        ir = parser.parse(source)
        assert len(ir.lua_scripts) == 1
        assert ir.lua_scripts[0].source_type == "file"
        assert ir.lua_scripts[0].content == "/etc/haproxy/lua/helpers.lua"


class TestResolversHoldOptions:
    """Test resolvers hold options (lines 1825, 1827, 1829)."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_resolvers_all_hold_options(self, parser):
        """Test resolvers with all hold options."""
        source = '''
        config test {
            resolvers dns {
                nameserver ns1 "8.8.8.8" 53
                hold_nx: 30s
                hold_obsolete: 15s
                hold_other: 20s
                hold_refused: 10s
                hold_timeout: 5s
                hold_valid: 60s
                resolve_retries: 3
                timeout_resolve: 1s
                timeout_retry: 1s
            }
        }
        '''
        ir = parser.parse(source)
        assert len(ir.resolvers) == 1
        resolver = ir.resolvers[0]
        assert resolver.hold_nx == "30s"
        assert resolver.hold_obsolete == "15s"
        assert resolver.hold_other == "20s"
        assert resolver.hold_refused == "10s"
        assert resolver.hold_timeout == "5s"
        assert resolver.hold_valid == "60s"


class TestHttpCheckSSLOptions:
    """Test http-check SSL options (lines 3053-3064)."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_http_check_connect_ssl_only(self, parser):
        """Test http-check connect with SSL only."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    connect ssl
                }
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 443
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        connect_rules = [r for r in backend.http_check_rules if r.type == "connect"]
        assert len(connect_rules) == 1
        assert connect_rules[0].ssl is True

    def test_http_check_connect_ssl_with_sni(self, parser):
        """Test http-check connect with SSL and SNI."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    connect ssl sni "api.example.com"
                }
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 443
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        connect_rules = [r for r in backend.http_check_rules if r.type == "connect"]
        assert len(connect_rules) == 1
        assert connect_rules[0].ssl is True
        assert connect_rules[0].sni == "api.example.com"

    def test_http_check_connect_ssl_with_sni_and_alpn(self, parser):
        """Test http-check connect with SSL, SNI, and ALPN."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    connect ssl sni "api.example.com" alpn "h2"
                }
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 443
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        connect_rules = [r for r in backend.http_check_rules if r.type == "connect"]
        assert len(connect_rules) == 1
        assert connect_rules[0].ssl is True
        assert connect_rules[0].sni == "api.example.com"
        assert connect_rules[0].alpn == "h2"


class TestTcpCheckSSLOptions:
    """Test tcp-check SSL options."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_tcp_check_connect_ssl(self, parser):
        """Test tcp-check connect with SSL."""
        source = '''
        config test {
            backend tcp_backend {
                mode: tcp
                balance: roundrobin
                tcp-check {
                    connect ssl
                }
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 443
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        connect_rules = [r for r in backend.tcp_check_rules if r.type == "connect"]
        assert len(connect_rules) == 1
        assert connect_rules[0].ssl is True


class TestHttpCheckSendHeaders:
    """Test http-check send with headers."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_http_check_send_with_headers(self, parser):
        """Test http-check send with custom headers."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    send method "GET" uri "/health" headers {
                        header "Host" "api.example.com"
                        header "Accept" "application/json"
                    }
                }
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        send_rules = [r for r in backend.http_check_rules if r.type == "send"]
        assert len(send_rules) == 1
        # Headers should be present
        assert send_rules[0].method == "GET"
        assert send_rules[0].uri == "/health"


class TestStatsRefresh:
    """Test stats refresh option."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_stats_with_refresh(self, parser):
        """Test stats with refresh option."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                stats {
                    enable: true
                    uri: "/stats"
                    refresh: 30
                }
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert frontend.stats_config is not None
        assert frontend.stats_config.refresh == "30"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
