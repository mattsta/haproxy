"""Additional tests for uncovered code paths in DSL transformer."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestStatsRefreshOption:
    """Test stats refresh option (lines 1697-1698)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_stats_with_refresh_option(self, parser, codegen):
        """Test stats configuration with refresh option."""
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
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert frontend.stats_config is not None
        assert frontend.stats_config.refresh == "30"


class TestSingleRuleFormats:
    """Test single rule handling formats."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_with_single_use_backend(self, parser, codegen):
        """Test frontend with single use_backend rule."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                acl {
                    is_api path_beg "/api"
                }
                use_backend api if is_api
                default_backend: default_app
            }
            backend api {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
            backend default_app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.2" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "use_backend api if is_api" in output


class TestRedirectDropQuery:
    """Test redirect with drop-query option."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_redirect_with_drop_query(self, parser, codegen):
        """Test redirect with drop-query option."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                redirect location "https://example.com" drop-query
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "redirect location https://example.com drop-query" in output


class TestHttpCheckConnectOptions:
    """Test http-check connect with various options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_check_connect_with_port(self, parser, codegen):
        """Test http-check connect with port."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    connect port 443
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        connect_rules = [r for r in backend.http_check_rules if r.type == "connect"]
        assert len(connect_rules) == 1
        assert connect_rules[0].port == 443


class TestServerResolvers:
    """Test server with resolvers option."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_server_with_resolvers(self, parser, codegen):
        """Test server with resolvers option."""
        source = '''
        config test {
            resolvers dns {
                nameserver ns1 "8.8.8.8" 53
                timeout_resolve: 1s
                timeout_retry: 1s
                resolve_retries: 3
            }
            backend api {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "api.example.com"
                        port: 8080
                        resolvers: "dns"
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "resolvers dns" in output


class TestFrontendAclVariants:
    """Test various ACL formats."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_multiple_acls_in_block(self, parser, codegen):
        """Test multiple ACLs in a block."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                acl {
                    is_static path_end ".jpg" ".png" ".css" ".js"
                    is_api path_beg "/api"
                }
                use_backend static if is_static
                use_backend api if is_api
                default_backend: default_app
            }
            backend static {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
            backend api {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.2" port: 8080 }
                }
            }
            backend default_app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.3" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert len(frontend.acls) >= 2


class TestCompressionConfig:
    """Test compression configuration."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_with_compression(self, parser, codegen):
        """Test backend with compression configuration."""
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


class TestHttpRequestSetVar:
    """Test http-request set-var action."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_request_set_var(self, parser, codegen):
        """Test http-request set-var action."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                http-request {
                    set_var var: "txn.myvar" value: "%[hdr(Host)]"
                }
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request set-var" in output


class TestDefaultServer:
    """Test default-server configuration."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_with_default_server(self, parser, codegen):
        """Test backend with default-server options."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                default-server {
                    check: true
                    inter: 3s
                    rise: 2
                    fall: 3
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                    server s2 { address: "10.0.0.2" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "default-server" in output


class TestErrorFile:
    """Test error file configuration."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_with_errorfile(self, parser, codegen):
        """Test frontend with errorfile directive."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                errorfile 503 "/etc/haproxy/errors/503.http"
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "errorfile 503 /etc/haproxy/errors/503.http" in output


class TestLogFormat:
    """Test log-format directive."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_with_log_format(self, parser, codegen):
        """Test frontend with custom log-format."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                log-format: "%ci:%cp [%t] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Tt"
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "log-format" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
