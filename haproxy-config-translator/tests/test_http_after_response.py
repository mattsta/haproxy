"""Tests for http-after-response directive (response manipulation after headers received)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHttpAfterResponseParsing:
    """Test http-after-response directive parsing."""

    def test_frontend_http_after_response_set_header(self):
        """Test frontend http-after-response with set_header action."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-after-response {
                    set_header name:"X-Custom-Header" value: "test-value"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert len(ir.frontends[0].http_after_response_rules) == 1
        rule = ir.frontends[0].http_after_response_rules[0]
        assert rule.action == "set_header"
        assert rule.parameters["name"] == "X-Custom-Header"
        assert rule.parameters["value"] == "test-value"

    def test_backend_http_after_response_add_header(self):
        """Test backend http-after-response with add_header action."""
        config = """
        config test {
            backend app {
                mode: http
                http-after-response {
                    add_header name:"X-Backend-Server" value: "%s" }
                }
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends[0].http_after_response_rules) == 1
        rule = ir.backends[0].http_after_response_rules[0]
        assert rule.action == "add_header"
        assert rule.parameters["name"] == "X-Backend-Server"

    def test_http_after_response_del_header(self):
        """Test http-after-response with del_header action."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-after-response {
                    del_header name:"Server"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        rule = ir.frontends[0].http_after_response_rules[0]
        assert rule.action == "del_header"
        assert rule.parameters["name"] == "Server"

    def test_http_after_response_with_condition(self):
        """Test http-after-response with condition."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-after-response {
                    set_header name:"X-Frame-Options" value: "DENY" if status_200
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        rule = ir.frontends[0].http_after_response_rules[0]
        assert rule.action == "set_header"
        assert rule.condition is not None

    def test_http_after_response_set_status(self):
        """Test http-after-response with set_status action."""
        config = """
        config test {
            backend app {
                mode: http
                http-after-response {
                    set_status status:503
                }
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        rule = ir.backends[0].http_after_response_rules[0]
        assert rule.action == "set_status"
        assert rule.parameters["status"] == 503

    def test_listen_http_after_response(self):
        """Test listen http-after-response directive."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                http-after-response {
                    set_header name:"Cache-Control" value: "no-cache" }
                }
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert len(ir.listens[0].http_after_response_rules) == 1
        rule = ir.listens[0].http_after_response_rules[0]
        assert rule.action == "set_header"
        assert rule.parameters["name"] == "Cache-Control"


class TestHttpAfterResponseCodegen:
    """Test http-after-response code generation."""

    def test_frontend_http_after_response_codegen(self):
        """Test frontend http-after-response code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-after-response {
                    set_header name:"X-Custom-Header" value: "test-value"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "http-after-response set-header" in output
        assert "name X-Custom-Header" in output

    def test_backend_http_after_response_codegen(self):
        """Test backend http-after-response code generation."""
        config = """
        config test {
            backend app {
                mode: http
                http-after-response {
                    add_header name:"X-Backend" value: "app-server" }
                }
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend app" in output
        assert "http-after-response add-header" in output

    def test_http_after_response_with_condition_codegen(self):
        """Test http-after-response with condition code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-after-response {
                    del_header name:"Server" if is_static
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "http-after-response del-header" in output
        assert "if" in output


class TestHttpAfterResponseIntegration:
    """Integration tests for http-after-response directive."""

    def test_multiple_http_after_response_rules(self):
        """Test multiple http-after-response rules in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-after-response {
                    set_header name:"X-Frame-Options" value: "DENY" }
                }
                http-after-response {
                    set_header name:"X-Content-Type-Options" value: "nosniff" }
                }
                http-after-response {
                    del_header name:"Server"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].http_after_response_rules) == 3
        assert ir.frontends[0].http_after_response_rules[0].action == "set_header"
        assert ir.frontends[0].http_after_response_rules[1].action == "set_header"
        assert ir.frontends[0].http_after_response_rules[2].action == "del_header"

    def test_http_after_response_with_other_http_rules(self):
        """Test http-after-response alongside http-request and http-response."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-request {
                    set_header name:"X-Forwarded-Proto" value: "https" }
                }
                http-response {
                    set_header name:"X-Response-Time" value: "%Tr" }
                }
                http-after-response {
                    set_header name:"X-Final-Header" value: "processed" }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.frontends[0].http_request_rules) == 1
        assert len(ir.frontends[0].http_response_rules) == 1
        assert len(ir.frontends[0].http_after_response_rules) == 1

    def test_http_after_response_complete_config(self):
        """Test complete configuration with http-after-response."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: "httplog"
                http-after-response {
                    set_header name:"Strict-Transport-Security" value: "max-age=31536000" }
                }
                http-after-response {
                    del_header name:"X-Powered-By" }
                }
                default_backend: app
            }

            backend app {
                mode: http
                balance: roundrobin
                http-after-response {
                    set_header name:"X-Backend-ID" value: "%s" }
                }
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 check: true }
                    server app2 { address: "10.0.1.2" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "http-after-response set_header name Strict-Transport-Security" in output
        assert "http-after-response del_header name X-Powered-By" in output
        assert "backend app" in output
        assert "http-after-response set_header name X-Backend-ID" in output

    def test_http_after_response_various_actions(self):
        """Test http-after-response with various action types."""
        actions = [
            ("set_header", {"name": "X-Test-1", "value": "value1"}),
            ("add_header", {"name": "X-Test-2", "value": "value2"}),
            ("del_header", {"name": "X-Remove"}),
            ("replace_header", {"name": "Content-Type", "match": "text/", "replace": "application/"}),
            ("replace_value", {"name": "Location", "match": "http:", "replace": "https:"}),
        ]

        for action, params in actions:
            # Build params string
            params_str = " ".join([f"{k}: \"{v}\"" for k, v in params.items()])

            config = f"""
            config test {{
                frontend web {{
                    bind *:80
                    mode: http
                    http-after-response {{
                        {action} {params_str}
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert len(ir.frontends[0].http_after_response_rules) == 1
            assert ir.frontends[0].http_after_response_rules[0].action == action

    def test_listen_http_after_response_codegen(self):
        """Test listen http-after-response code generation."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                http-after-response {
                    set_header name: "X-Stats-Server" value: "haproxy"
                }
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "listen stats" in output
        assert "http-after-response set-header" in output
        assert "name X-Stats-Server" in output

    def test_backend_multiple_http_after_response(self):
        """Test backend with multiple http-after-response rules."""
        config = """
        config test {
            backend api {
                mode: http
                http-after-response {
                    set_header name:"Access-Control-Allow-Origin" value: "*" }
                }
                http-after-response {
                    set_header name:"Access-Control-Allow-Methods" value: "GET, POST" }
                }
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend api" in output
        assert "http-after-response set_header name Access-Control-Allow-Origin" in output
        assert "http-after-response set_header name Access-Control-Allow-Methods" in output
