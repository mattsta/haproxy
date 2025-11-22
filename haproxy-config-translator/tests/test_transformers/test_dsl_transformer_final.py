"""Final batch of tests for uncovered code paths in DSL transformer."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestBackendLoadBalancing:
    """Test various backend load balancing configurations."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_balance_leastconn(self, parser, codegen):
        """Test backend with leastconn balance algorithm."""
        source = '''
        config test {
            backend api {
                balance: leastconn
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "balance leastconn" in output

    def test_backend_balance_source(self, parser, codegen):
        """Test backend with source balance algorithm."""
        source = '''
        config test {
            backend api {
                balance: source
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "balance source" in output


class TestHttpCheckExpect:
    """Test http-check expect directive."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_check_expect_status(self, parser, codegen):
        """Test http-check with expect status."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                http-check {
                    send method "GET" uri "/health"
                    expect status 200
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        expect_rules = [r for r in backend.http_check_rules if r.type == "expect"]
        assert len(expect_rules) == 1


class TestFrontendHttpRulesBlock:
    """Test frontend with HTTP rules blocks."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_request_deny(self, parser, codegen):
        """Test http-request deny action."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                acl {
                    is_blocked src "10.0.0.0/8"
                }
                http-request {
                    deny if is_blocked
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
        assert "http-request deny" in output

    def test_http_request_tarpit(self, parser, codegen):
        """Test http-request tarpit action."""
        source = '''
        config test {
            frontend web {
                bind *:80
                mode: http
                acl {
                    is_suspicious src "192.168.1.0/24"
                }
                http-request {
                    tarpit if is_suspicious
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
        assert "http-request tarpit" in output


class TestBackendHttpRequestRules:
    """Test backend with HTTP request rules."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_http_request_set_path(self, parser, codegen):
        """Test backend http-request set-path."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                http-request {
                    set_path path: "/api/v2%[path]"
                }
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request set-path" in output


class TestBackendOptions:
    """Test various backend options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_backend_with_multiple_options(self, parser, codegen):
        """Test backend with multiple options."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                option: ["httpchk", "forwardfor", "httplog"]
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "option httpchk" in output
        assert "option forwardfor" in output
        assert "option httplog" in output


class TestGlobalConfiguration:
    """Test global configuration options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_with_maxconn(self, parser, codegen):
        """Test global section with maxconn."""
        source = '''
        config test {
            global {
                maxconn: 50000
                daemon: true
                user: "haproxy"
                group: "haproxy"
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "maxconn 50000" in output


class TestFrontendBindOptions:
    """Test frontend bind options."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_multiple_binds(self, parser, codegen):
        """Test frontend with multiple binds."""
        source = '''
        config test {
            frontend web {
                bind *:80
                bind *:8080
                mode: http
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
        assert len(frontend.binds) == 2


class TestResolversComplete:
    """Test complete resolvers configuration."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_resolvers_full_config(self, parser, codegen):
        """Test resolvers with complete configuration."""
        source = '''
        config test {
            resolvers mydns {
                nameserver dns1 "8.8.8.8" 53
                nameserver dns2 "8.8.4.4" 53
                timeout_resolve: 1s
                timeout_retry: 500ms
                resolve_retries: 3
                hold_valid: 60s
            }
        }
        '''
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "resolvers mydns" in output
        assert "nameserver dns1" in output
        assert "hold valid 60s" in output


class TestPeersSection:
    """Test peers section configuration."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_peers_basic(self, parser, codegen):
        """Test peers section."""
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
        assert "peer haproxy1" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
