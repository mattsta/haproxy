"""Test advanced HTTP request and response actions."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHttpRequestAdvancedActions:
    """Test advanced HTTP request actions."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_request_set_var(self, parser, codegen):
        """Test http-request set-var action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    set_var var: "txn.user_id" value: "%[urlp(user_id)]"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]

        assert len(frontend.http_request_rules) == 1
        rule = frontend.http_request_rules[0]
        assert rule.action == "set_var"

        output = codegen.generate(ir)
        assert "http-request set-var" in output
        assert "txn.user_id" in output

    def test_http_request_unset_var(self, parser, codegen):
        """Test http-request unset-var action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    unset_var var: "txn.user_id"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request unset-var" in output
        assert "txn.user_id" in output

    def test_http_request_replace_header(self, parser, codegen):
        """Test http-request replace-header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    replace_header name: "Host" match: "old\\.example\\.com" replace: "new.example.com"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request replace-header" in output
        assert "Host" in output

    def test_http_request_replace_value(self, parser, codegen):
        """Test http-request replace-value action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    replace_value name: "Cookie" match: "secure=false" replace: "secure=true"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request replace-value" in output
        assert "Cookie" in output

    def test_http_request_allow(self, parser, codegen):
        """Test http-request allow action."""
        source = """
        config test {
            frontend web {
                bind *:80
                acl {
                    is_internal src "10.0.0.0/8"
                }
                http-request {
                    allow if is_internal
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request allow if is_internal" in output

    def test_http_request_deny_with_status(self, parser, codegen):
        """Test http-request deny with status code."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    deny deny_status: 403
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request deny" in output
        assert "deny status 403" in output

    def test_http_request_tarpit(self, parser, codegen):
        """Test http-request tarpit action."""
        source = """
        config test {
            frontend web {
                bind *:80
                acl {
                    is_bad_bot hdr_sub "User-Agent" "BadBot"
                }
                http-request {
                    tarpit if is_bad_bot
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request tarpit if is_bad_bot" in output

    def test_http_request_auth(self, parser, codegen):
        """Test http-request auth action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    auth realm: "Protected Area"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request auth" in output
        assert "realm" in output

    def test_http_request_cache_use(self, parser, codegen):
        """Test http-request cache-use action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    cache_use name: "my_cache"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request cache-use" in output
        assert "my_cache" in output

    def test_http_request_capture(self, parser, codegen):
        """Test http-request capture action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    capture sample: "%[hdr(User-Agent)]" len: 128
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request capture" in output

    def test_http_request_do_resolve(self, parser, codegen):
        """Test http-request do-resolve action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    do_resolve var: "txn.myip" resolvers: "dns1" str: "%[hdr(host)]"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request do-resolve" in output

    def test_http_request_set_log_level(self, parser, codegen):
        """Test http-request set-log-level action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    set_log_level level: "silent"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-request set-log-level" in output
        assert "silent" in output


class TestHttpResponseAdvancedActions:
    """Test advanced HTTP response actions."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_response_set_var(self, parser, codegen):
        """Test http-response set-var action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    set_var var: "txn.response_time" value: "%[date()]"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response set-var" in output
        assert "txn.response_time" in output

    def test_http_response_unset_var(self, parser, codegen):
        """Test http-response unset-var action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    unset_var var: "txn.temp"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response unset-var" in output
        assert "txn.temp" in output

    def test_http_response_replace_header(self, parser, codegen):
        """Test http-response replace-header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    replace_header name: "Location" match: "http://" replace: "https://"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response replace-header" in output
        assert "Location" in output

    def test_http_response_replace_value(self, parser, codegen):
        """Test http-response replace-value action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    replace_value name: "Set-Cookie" match: "HttpOnly" replace: "HttpOnly; Secure"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response replace-value" in output
        assert "Set-Cookie" in output

    def test_http_response_allow(self, parser, codegen):
        """Test http-response allow action."""
        source = """
        config test {
            frontend web {
                bind *:80
                acl {
                    is_success status "200-299"
                }
                http-response {
                    allow if is_success
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response allow if is_success" in output

    def test_http_response_deny(self, parser, codegen):
        """Test http-response deny action."""
        source = """
        config test {
            frontend web {
                bind *:80
                acl {
                    has_error status "500-599"
                }
                http-response {
                    deny if has_error
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response deny if has_error" in output

    def test_http_response_cache_store(self, parser, codegen):
        """Test http-response cache-store action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    cache_store name: "my_cache"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response cache-store" in output
        assert "my_cache" in output

    def test_http_response_capture(self, parser, codegen):
        """Test http-response capture action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    capture sample: "%[hdr(Server)]" len: 64
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "http-response capture" in output

    def test_http_response_return(self, parser, codegen):
        """Test http-response return action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    return status: 200 content_type: "text/plain" string: "OK"
                }
                default_backend: app
            }
            backend app {
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]

        assert len(frontend.http_response_rules) == 1
        rule = frontend.http_response_rules[0]
        assert rule.action == "return"

        output = codegen.generate(ir)
        assert "http-response return" in output
        assert "status 200" in output
