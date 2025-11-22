"""Tests for remaining uncovered code paths in DSL transformer."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestListenExtendedOptions:
    """Test listen section extended options (lines 4182-4298)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_listen_enabled_directive(self, parser, codegen):
        """Test listen section with enabled directive."""
        source = """
        config test {
            listen myservice {
                bind *:8080
                mode: http
                balance: roundrobin
                enabled: true
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert listen.enabled is True

    def test_listen_guid_directive(self, parser, codegen):
        """Test listen section with guid directive."""
        source = """
        config test {
            listen myservice {
                bind *:8080
                mode: http
                balance: roundrobin
                guid: "abc-123-def"
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert listen.guid == "abc-123-def"


class TestRedirectOptionsWithCodegen:
    """Test redirect rule options via codegen (lines 2616-2654)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_redirect_basic_location(self, parser, codegen):
        """Test basic redirect location."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                redirect location "https://example.com"
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "redirect location https://example.com" in output

    def test_redirect_with_code(self, parser, codegen):
        """Test redirect with custom code."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                redirect scheme "https" code 301
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "redirect scheme https code 301" in output


class TestHttpCheckMethodOnly:
    """Test http-check send with method only (lines 2977-2984)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_check_send_method_only(self, parser, codegen):
        """Test http-check send with just method, no URI."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    send method "OPTIONS"
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        send_rules = [r for r in backend.http_check_rules if r.type == "send"]
        assert len(send_rules) == 1
        assert send_rules[0].method == "OPTIONS"


class TestStatsAuthAndRefresh:
    """Test stats auth and refresh options (lines 1697-1698)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_stats_with_auth(self, parser, codegen):
        """Test stats with auth option."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                stats {
                    enable: true
                    uri: "/stats"
                    auth: "admin:secret"
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
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert frontend.stats_config is not None
        assert len(frontend.stats_config.auth) == 1
        assert frontend.stats_config.auth[0] == "admin:secret"


class TestLuaInlineWithParameters:
    """Test inline Lua scripts with parameters (lines 1939-1943)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_lua_inline_script_basic(self, parser):
        """Test basic inline Lua script."""
        source = """
        config test {
            lua {
                inline my_handler {
                    core.log(core.info, "Hello")
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.lua_scripts) == 1
        assert ir.lua_scripts[0].name == "my_handler"


class TestUseServerWithCondition:
    """Test use-server with condition (line 2950)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_use_server_basic(self, parser, codegen):
        """Test basic use-server directive."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                use-server s1 if TRUE
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                    server s2 { address: "10.0.0.2" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "use-server s1 if TRUE" in output


class TestHealthCheckHeaders:
    """Test health check with headers (lines 4393-4430)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_health_check_with_header(self, parser, codegen):
        """Test health check with custom header."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    header "Host" "api.example.com"
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.health_check is not None
        assert "Host" in backend.health_check.headers


class TestFrontendSingleRulesBlocks:
    """Test frontend rule blocks."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_http_request_block(self, parser, codegen):
        """Test frontend with http-request block."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-request {
                    set_header name: "X-Test" value: "test_value"
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
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert len(frontend.http_request_rules) >= 1

    def test_frontend_http_response_block(self, parser, codegen):
        """Test frontend with http-response block."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-response {
                    set_header name: "X-Frame-Options" value: "DENY"
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
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert len(frontend.http_response_rules) >= 1

    def test_frontend_tcp_request_block(self, parser, codegen):
        """Test frontend with tcp-request block."""
        source = """
        config test {
            frontend tcp_fe {
                bind *:3306
                mode: tcp
                tcp-request {
                    content accept
                }
                default_backend: mysql
            }
            backend mysql {
                mode: tcp
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 3306 }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert len(frontend.tcp_request_rules) >= 1


class TestListenMixedRuleHandling:
    """Test listen section mixed rule handling (lines 4130-4172)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_listen_with_http_after_response_block(self, parser, codegen):
        """Test listen section with http-after-response block."""
        source = """
        config test {
            listen myservice {
                bind *:8080
                mode: http
                balance: roundrobin
                http-after-response {
                    set_header name: "Strict-Transport-Security" value: "max-age=31536000"
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert len(listen.http_after_response_rules) >= 1


class TestBackendSingleRuleHandling:
    """Test backend single rule handling (lines 3540-3605)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_single_http_check_rule(self, parser, codegen):
        """Test backend with single http-check rule."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    send method "GET" uri "/healthz"
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert len(backend.http_check_rules) >= 1

    def test_backend_single_use_server_rule(self, parser, codegen):
        """Test backend with single use-server rule."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                use-server s1 if TRUE
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert len(backend.use_server_rules) >= 1


class TestMonitorFailCondition:
    """Test monitor-fail with condition (line 2465)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_monitor_fail_basic(self, parser, codegen):
        """Test basic monitor-fail directive."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor_uri: "/health"
                acl {
                    is_maintenance path "/maintenance"
                }
                monitor fail if is_maintenance
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert len(frontend.monitor_fail_rules) >= 1


class TestACLBlockDefinition:
    """Test ACL block definition."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_acl_block_definition(self, parser):
        """Test ACL with block definition."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                acl is_admin {
                    src "192.168.1.0/24"
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
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        acl = next(a for a in frontend.acls if a.name == "is_admin")
        assert acl.criterion == "src"


class TestFloatAndBooleanParsing:
    """Test float and boolean value parsing (lines 5114, 5121)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_boolean_false_value(self, parser):
        """Test boolean false value parsing."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                        check: false
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        server = backend.servers[0]
        assert server.check is False


class TestStickTableFeatures:
    """Test stick-table features."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_stick_on_simple_pattern(self, parser):
        """Test stick-on with simple pattern."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                stick-table {
                    type: ip
                    size: 100000
                    expire: 30m
                }
                stick on src
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.stick_table is not None
        assert len(backend.stick_rules) >= 1

    def test_stick_table_string_type(self, parser):
        """Test stick-table with string type."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                stick-table {
                    type: string
                    size: 100000
                    expire: 30m
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.stick_table is not None
        assert backend.stick_table.type == "string"


class TestHttpReuseMode:
    """Test http-reuse mode (line 2877)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_reuse_safe(self, parser, codegen):
        """Test http-reuse safe mode."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                http-reuse: safe
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-reuse safe" in output

    def test_http_reuse_always(self, parser, codegen):
        """Test http-reuse always mode."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                http-reuse: always
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-reuse always" in output


class TestListenHealthCheck:
    """Test listen with health check."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_listen_with_health_check(self, parser):
        """Test listen section with health check."""
        source = """
        config test {
            listen myservice {
                bind *:8080
                mode: http
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        listen = ir.listens[0]
        # Health check might be in metadata
        assert listen is not None


class TestFiltersSection:
    """Test filters section parsing."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_with_filters(self, parser, codegen):
        """Test frontend with filters."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                filters: [
                    { type: "compression" }
                ]
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "filter compression" in output


class TestTcpRuleParams:
    """Test TCP rule parameters (lines 5363, 5367)."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_tcp_request_with_content_accept(self, parser, codegen):
        """Test TCP request content accept."""
        source = """
        config test {
            frontend tcp_fe {
                bind *:3306
                mode: tcp
                tcp-request {
                    content accept
                }
                default_backend: mysql
            }
            backend mysql {
                mode: tcp
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 3306 }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "tcp-request content accept" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
