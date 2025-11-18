"""Test HTTP request and response actions."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHttpRequestActions:
    """Test HTTP request actions."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_request_return(self, parser, codegen):
        """Test http-request return action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    return status: 403 content_type: "text/plain" string: "Forbidden"
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
        assert rule.action == "return"
        assert "status" in rule.parameters
        assert rule.parameters["status"] == 403

        output = codegen.generate(ir)
        assert "http-request return" in output
        assert "status 403" in output
        assert "content-type" in output
        assert "string" in output

    def test_http_request_set_header(self, parser, codegen):
        """Test http-request set_header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    set_header header: "X-Custom-Header" value: "custom-value"
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
        assert rule.action == "set_header"

        output = codegen.generate(ir)
        assert "http-request set-header" in output
        assert "X-Custom-Header" in output

    def test_http_request_add_header(self, parser, codegen):
        """Test http-request add_header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    add_header name: "X-Request-ID" value: "%[uuid()]"
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
        assert "http-request add-header" in output
        assert "X-Request-ID" in output

    def test_http_request_del_header(self, parser, codegen):
        """Test http-request del_header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    del_header name: "X-Forwarded-For"
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
        assert "http-request del-header" in output
        assert "X-Forwarded-For" in output

    def test_http_request_redirect(self, parser, codegen):
        """Test http-request redirect action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    redirect location: "https://example.com" code: 301
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
        assert "http-request redirect" in output
        assert "https://example.com" in output

    def test_http_request_set_uri(self, parser, codegen):
        """Test http-request set_uri action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    set_uri uri: "/api/v2%[path]"
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
        assert "http-request set-uri" in output

    def test_http_request_set_path(self, parser, codegen):
        """Test http-request set_path action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    set_path path: "/newpath"
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
        assert "http-request set-path" in output
        assert "/newpath" in output

    def test_http_request_set_method(self, parser, codegen):
        """Test http-request set_method action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    set_method method: "POST"
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
        assert "http-request set-method" in output
        assert "POST" in output

    def test_http_request_with_condition(self, parser, codegen):
        """Test http-request action with condition."""
        source = """
        config test {
            frontend web {
                bind *:80
                acl {
                    is_api path_beg "/api"
                }
                http-request {
                    deny if is_api
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
        rule = frontend.http_request_rules[0]
        assert rule.condition == "is_api"

        output = codegen.generate(ir)
        assert "http-request deny if is_api" in output


class TestHttpResponseActions:
    """Test HTTP response actions."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_http_response_set_status(self, parser, codegen):
        """Test http-response set_status action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    set_status status: 200
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
        assert rule.action == "set_status"

        output = codegen.generate(ir)
        assert "http-response set-status" in output
        assert "status 200" in output

    def test_http_response_set_header(self, parser, codegen):
        """Test http-response set_header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    set_header name: "X-Server" value: "HAProxy"
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
        assert "http-response set-header" in output
        assert "X-Server" in output

    def test_http_response_add_header(self, parser, codegen):
        """Test http-response add_header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    add_header name: "Cache-Control" value: "max-age=3600"
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
        assert "http-response add-header" in output
        assert "Cache-Control" in output

    def test_http_response_del_header(self, parser, codegen):
        """Test http-response del_header action."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-response {
                    del_header name: "Server"
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
        assert "http-response del-header" in output
        assert "Server" in output

    def test_multiple_http_actions(self, parser, codegen):
        """Test multiple HTTP actions in sequence."""
        source = """
        config test {
            frontend web {
                bind *:80
                http-request {
                    set_header name: "X-Forwarded-Proto" value: "https"
                }
                http-request {
                    add_header name: "X-Request-Start" value: "%[date()]"
                }
                http-response {
                    set_header name: "X-Server" value: "HAProxy"
                }
                http-response {
                    add_header name: "X-Response-Time" value: "%[date()]"
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

        assert len(frontend.http_request_rules) == 2
        assert len(frontend.http_response_rules) == 2

        output = codegen.generate(ir)
        assert output.count("http-request") == 2
        assert output.count("http-response") == 2
