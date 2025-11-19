"""Tests for backend HTTP-related directives (http-send-name-header, retry-on)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHttpSendNameHeader:
    """Test http-send-name-header directive."""

    def test_backend_http_send_name_header(self):
        """Test backend http-send-name-header directive."""
        config = """
        config test {
            backend app {
                mode: http
                http-send-name-header: "X-Backend-Server"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].http_send_name_header == "X-Backend-Server"

    def test_backend_http_send_name_header_codegen(self):
        """Test backend http-send-name-header code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: roundrobin
                http-send-name-header: "X-Server-Name"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "http-send-name-header X-Server-Name" in output
        assert "backend app" in output

    def test_backend_without_http_send_name_header(self):
        """Test backend without http-send-name-header (should be None)."""
        config = """
        config test {
            backend app {
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].http_send_name_header is None

    def test_http_send_name_header_custom_names(self):
        """Test http-send-name-header with various custom header names."""
        header_names = [
            "X-Backend-Server",
            "X-Server-Name",
            "X-HAProxy-Server",
            "X-Upstream-Name",
        ]

        for header_name in header_names:
            config = f"""
            config test {{
                backend app {{
                    mode: http
                    http-send-name-header: "{header_name}"
                    servers {{
                        server s1 {{ address: "10.0.1.1" port: 8080 }}
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.backends[0].http_send_name_header == header_name


class TestRetryOn:
    """Test retry-on directive."""

    def test_backend_retry_on(self):
        """Test backend retry-on directive."""
        config = """
        config test {
            backend app {
                mode: http
                retry-on: "conn-failure,empty-response,response-timeout"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].retry_on == "conn-failure,empty-response,response-timeout"

    def test_backend_retry_on_codegen(self):
        """Test backend retry-on code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: leastconn
                retry-on: "conn-failure,response-timeout"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "retry-on conn-failure,response-timeout" in output
        assert "backend app" in output

    def test_backend_without_retry_on(self):
        """Test backend without retry-on (should be None)."""
        config = """
        config test {
            backend app {
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].retry_on is None

    def test_retry_on_single_condition(self):
        """Test retry-on with single condition."""
        config = """
        config test {
            backend app {
                mode: http
                retry-on: "conn-failure"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].retry_on == "conn-failure"

    def test_retry_on_multiple_conditions(self):
        """Test retry-on with multiple conditions."""
        conditions = [
            "conn-failure,empty-response",
            "response-timeout,junk-response",
            "conn-failure,empty-response,response-timeout,junk-response,http-500",
        ]

        for condition in conditions:
            config = f"""
            config test {{
                backend app {{
                    mode: http
                    retry-on: "{condition}"
                    servers {{
                        server s1 {{ address: "10.0.1.1" port: 8080 }}
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.backends[0].retry_on == condition


class TestHttpDirectivesIntegration:
    """Integration tests for HTTP backend directives."""

    def test_http_send_name_header_with_retry_on(self):
        """Test http-send-name-header combined with retry-on."""
        config = """
        config test {
            backend app {
                mode: http
                http-send-name-header: "X-Backend-Server"
                retry-on: "conn-failure,response-timeout"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].http_send_name_header == "X-Backend-Server"
        assert ir.backends[0].retry_on == "conn-failure,response-timeout"

    def test_all_http_directives_combined_codegen(self):
        """Test code generation with http-reuse, http-send-name-header, and retry-on."""
        config = """
        config test {
            backend api {
                mode: http
                balance: roundrobin
                http-reuse: safe
                http-send-name-header: "X-API-Server"
                retry-on: "conn-failure,empty-response,response-timeout"
                servers {
                    server api1 { address: "192.168.1.10" port: 8080 check: true }
                    server api2 { address: "192.168.1.11" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend api" in output
        assert "mode http" in output
        assert "balance roundrobin" in output
        assert "http-reuse safe" in output
        assert "http-send-name-header X-API-Server" in output
        assert "retry-on conn-failure,empty-response,response-timeout" in output
        assert "server api1 192.168.1.10:8080 check" in output
        assert "server api2 192.168.1.11:8080 check" in output

    def test_multiple_backends_different_http_configs(self):
        """Test multiple backends with different HTTP configurations."""
        config = """
        config test {
            backend web {
                mode: http
                http-send-name-header: "X-Web-Server"
                servers {
                    server web1 { address: "10.0.1.1" port: 80 }
                }
            }

            backend api {
                mode: http
                retry-on: "conn-failure,response-timeout"
                servers {
                    server api1 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].http_send_name_header == "X-Web-Server"
        assert ir.backends[0].retry_on is None
        assert ir.backends[1].http_send_name_header is None
        assert ir.backends[1].retry_on == "conn-failure,response-timeout"

    def test_http_directives_with_timeouts(self):
        """Test HTTP directives with timeout configuration."""
        config = """
        config test {
            backend app {
                mode: http
                http-send-name-header: "X-Server"
                retry-on: "conn-failure"
                timeout_connect: 5s
                timeout_server: 30s
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].http_send_name_header == "X-Server"
        assert ir.backends[0].retry_on == "conn-failure"
        assert ir.backends[0].timeout_connect == "5s"
        assert ir.backends[0].timeout_server == "30s"
