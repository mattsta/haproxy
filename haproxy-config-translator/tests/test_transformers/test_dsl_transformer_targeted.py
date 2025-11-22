"""Targeted tests for specific uncovered code paths in DSL transformer."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestServerOptionsExtended:
    """Test extended server options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_server_with_maxqueue(self, parser, codegen):
        """Test server with maxqueue option."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                        maxqueue: 100
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]
        assert server.options.get("maxqueue") == 100

    def test_server_with_minconn(self, parser, codegen):
        """Test server with minconn option."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                        minconn: 10
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]
        assert server.options.get("minconn") == 10


class TestErrorFormats:
    """Test error format directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_error_log_format(self, parser, codegen):
        """Test frontend with error-log-format."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                error-log-format: "%ci:%cp [%t] %ft %b/%s %ST"
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
        assert frontend.error_log_format is not None


class TestStatsConfigOptions:
    """Test stats configuration options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_stats_with_realm(self, parser, codegen):
        """Test stats with realm option."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                stats {
                    enable: true
                    uri: "/stats"
                    realm: "HAProxy Stats"
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
        assert frontend.stats_config.realm == "HAProxy Stats"


class TestHttpAfterResponseRules:
    """Test http-after-response rules."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_http_after_response_set_header(self, parser, codegen):
        """Test frontend with http-after-response set-header."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                http-after-response {
                    set_header name: "X-Cache-Status" value: "HIT"
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
        assert "http-after-response set-header" in output


class TestListenPersistRdpCookie:
    """Test listen with persist rdp-cookie."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_listen_persist_rdp_cookie_basic(self, parser, codegen):
        """Test listen section with basic persist rdp-cookie."""
        source = '''
        config test {
            listen rdp_farm {
                bind *:3389
                mode: tcp
                balance: rdp-cookie
                persist rdp-cookie
                servers {
                    server srv1 {
                        address: "1.1.1.1"
                        port: 3389
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert listen.persist_rdp_cookie == ""  # Empty string means default cookie

    def test_listen_persist_rdp_cookie_with_name(self, parser, codegen):
        """Test listen section with persist rdp-cookie and custom name."""
        source = '''
        config test {
            listen rdp_farm {
                bind *:3389
                mode: tcp
                balance: rdp-cookie
                persist rdp-cookie("custom_cookie")
                servers {
                    server srv1 {
                        address: "1.1.1.1"
                        port: 3389
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert listen.persist_rdp_cookie == "custom_cookie"


class TestBackendPersistRdpCookie:
    """Test backend with persist rdp-cookie."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_persist_rdp_cookie_basic(self, parser, codegen):
        """Test backend with basic persist rdp-cookie."""
        source = '''
        config test {
            backend rdp_servers {
                balance: rdp-cookie
                persist rdp-cookie
                servers {
                    server srv1 {
                        address: "1.1.1.1"
                        port: 3389
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.persist_rdp_cookie == ""


class TestListenWithMultipleOptions:
    """Test listen sections with various options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_listen_with_option_array(self, parser, codegen):
        """Test listen section with option array."""
        source = '''
        config test {
            listen web {
                bind *:8080
                mode: http
                balance: roundrobin
                option: ["httplog", "forwardfor", "httpchk"]
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert "httplog" in listen.options


class TestBackendWithUseServer:
    """Test backend with use-server rules."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_use_server_basic(self, parser, codegen):
        """Test backend with use-server rule."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                acl is_special {
                    src "10.0.1.0/24"
                }
                default_backend: api
            }
            backend api {
                balance: roundrobin
                use-server s2 if is_special
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                    server s2 { address: "10.0.0.2" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert len(backend.use_server_rules) == 1
        output = codegen.generate(ir)
        assert "use-server s2 if is_special" in output


class TestFrontendLogOptions:
    """Test frontend with log options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_with_log_tag(self, parser, codegen):
        """Test frontend with log-tag."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                log-tag: "frontend-web"
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
        assert frontend.log_tag == "frontend-web"


class TestBackendLogOptions:
    """Test backend with log options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_with_log_tag(self, parser, codegen):
        """Test backend with log-tag."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                log-tag: "backend-api"
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.log_tag == "backend-api"


class TestFrontendIgnorePersist:
    """Test frontend with ignore-persist rules."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_ignore_persist(self, parser, codegen):
        """Test frontend with ignore-persist rule."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                acl {
                    is_admin src "10.0.0.0/8"
                }
                ignore-persist if is_admin
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
        assert len(frontend.ignore_persist_rules) == 1
        output = codegen.generate(ir)
        assert "ignore-persist if is_admin" in output


class TestFrontendForcePersist:
    """Test frontend with force-persist rules."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_force_persist(self, parser, codegen):
        """Test frontend with force-persist rule."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                acl is_sticky {
                    src "10.0.2.0/24"
                }
                force-persist if is_sticky
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
        assert len(frontend.force_persist_rules) == 1
        output = codegen.generate(ir)
        assert "force-persist if is_sticky" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
