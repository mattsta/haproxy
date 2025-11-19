"""Tests for http-error directive (custom HTTP error responses)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHttpErrorParsing:
    """Test http-error directive parsing."""

    def test_http_error_with_file(self):
        """Test http-error with file body source."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 404
                    file: "/etc/haproxy/errors/404.http"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert len(ir.frontends[0].http_errors) == 1
        http_error = ir.frontends[0].http_errors[0]
        assert http_error.status == 404
        assert http_error.file == "/etc/haproxy/errors/404.http"

    def test_http_error_with_lf_file(self):
        """Test http-error with lf-file body source."""
        config = """
        config test {
            backend app {
                mode: http
                http-error {
                    status: 500
                    lf-file: "/etc/haproxy/errors/500.lf"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends[0].http_errors) == 1
        http_error = ir.backends[0].http_errors[0]
        assert http_error.status == 500
        assert http_error.lf_file == "/etc/haproxy/errors/500.lf"

    def test_http_error_with_string(self):
        """Test http-error with string body source."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 503
                    string: "Service Unavailable"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        http_error = ir.frontends[0].http_errors[0]
        assert http_error.status == 503
        assert http_error.string == "Service Unavailable"

    def test_http_error_with_lf_string(self):
        """Test http-error with lf-string body source."""
        config = """
        config test {
            backend api {
                mode: http
                http-error {
                    status: 502
                    lf-string: "Bad Gateway - %[date]"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        http_error = ir.backends[0].http_errors[0]
        assert http_error.status == 502
        assert http_error.lf_string == "Bad Gateway - %[date]"

    def test_http_error_with_errorfile(self):
        """Test http-error with errorfile body source."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 403
                    errorfile: "/errors/403.html"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        http_error = ir.frontends[0].http_errors[0]
        assert http_error.status == 403
        assert http_error.errorfile == "/errors/403.html"

    def test_http_error_with_errorfiles_name(self):
        """Test http-error with errorfiles-name body source."""
        config = """
        config test {
            backend app {
                mode: http
                http-error {
                    status: 500
                    errorfiles-name: "my_errors"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        http_error = ir.backends[0].http_errors[0]
        assert http_error.status == 500
        assert http_error.errorfiles_name == "my_errors"

    def test_http_error_with_default_errorfiles(self):
        """Test http-error with default-errorfiles body source."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 400
                    default-errorfiles: true
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        http_error = ir.frontends[0].http_errors[0]
        assert http_error.status == 400
        assert http_error.default_errorfiles is True

    def test_http_error_with_content_type(self):
        """Test http-error with content-type."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 404
                    content-type: "application/json"
                    string: "{error: Not Found}"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        http_error = ir.frontends[0].http_errors[0]
        assert http_error.status == 404
        assert http_error.content_type == "application/json"
        assert http_error.string == "{error: Not Found}"


class TestHttpErrorCodegen:
    """Test http-error code generation."""

    def test_http_error_file_codegen(self):
        """Test http-error with file code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 404
                    file: "/errors/404.http"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "http-error status 404 file /errors/404.http" in output

    def test_http_error_string_codegen(self):
        """Test http-error with string code generation."""
        config = """
        config test {
            backend app {
                mode: http
                http-error {
                    status: 503
                    string: "Service Unavailable"
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
        assert 'http-error status 503 string "Service Unavailable"' in output

    def test_http_error_with_content_type_codegen(self):
        """Test http-error with content-type code generation."""
        config = """
        config test {
            frontend api {
                bind *:8080
                mode: http
                http-error {
                    status: 404
                    content-type: "application/json"
                    string: "{error: Not Found}"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend api" in output
        assert "http-error status 404 content-type application/json" in output
        assert 'string "{error: Not Found}"' in output

    def test_http_error_default_errorfiles_codegen(self):
        """Test http-error with default-errorfiles code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 400
                    default-errorfiles: true
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "http-error status 400 default-errorfiles" in output

    def test_http_error_errorfiles_name_codegen(self):
        """Test http-error with errorfiles-name code generation."""
        config = """
        config test {
            backend app {
                mode: http
                http-error {
                    status: 500
                    errorfiles-name: "custom_errors"
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

        assert "http-error status 500 errorfiles custom_errors" in output


class TestHttpErrorIntegration:
    """Integration tests for http-error directive."""

    def test_multiple_http_errors_frontend(self):
        """Test multiple http-error directives in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 404
                    file: "/errors/404.http"
                }
                http-error {
                    status: 500
                    file: "/errors/500.http"
                }
                http-error {
                    status: 503
                    string: "Service Unavailable"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].http_errors) == 3
        assert ir.frontends[0].http_errors[0].status == 404
        assert ir.frontends[0].http_errors[1].status == 500
        assert ir.frontends[0].http_errors[2].status == 503

    def test_multiple_http_errors_backend(self):
        """Test multiple http-error directives in backend."""
        config = """
        config test {
            backend app {
                mode: http
                http-error {
                    status: 502
                    lf-string: "Bad Gateway - %[date]"
                }
                http-error {
                    status: 503
                    errorfiles-name: "maintenance"
                }
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends[0].http_errors) == 2
        assert ir.backends[0].http_errors[0].status == 502
        assert ir.backends[0].http_errors[1].status == 503

    def test_http_error_in_listen(self):
        """Test http-error directive in listen section."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                http-error {
                    status: 404
                    string: "Stats page not found"
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
        assert len(ir.listens[0].http_errors) == 1
        assert ir.listens[0].http_errors[0].status == 404
        assert ir.listens[0].http_errors[0].string == "Stats page not found"

    def test_http_error_codegen_complete(self):
        """Test complete http-error configuration code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: "httplog"
                http-error {
                    status: 404
                    content-type: "text/html"
                    file: "/errors/404.html"
                }
                http-error {
                    status: 500
                    content-type: "text/html"
                    file: "/errors/500.html"
                }
                default_backend: app
            }

            backend app {
                mode: http
                balance: roundrobin
                http-error {
                    status: 503
                    string: "Backend Unavailable"
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
        assert "http-error status 404 content-type text/html file /errors/404.html" in output
        assert "http-error status 500 content-type text/html file /errors/500.html" in output
        assert "backend app" in output
        assert 'http-error status 503 string "Backend Unavailable"' in output

    def test_http_error_multiple_in_frontend(self):
        """Test multiple http-error directives in a frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 400
                    string: "Bad Request"
                }
                http-error {
                    status: 404
                    file: "/errors/404.http"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.frontends[0].http_errors) == 2
        assert ir.frontends[0].http_errors[0].status == 400
        assert ir.frontends[0].http_errors[1].status == 404

    def test_http_error_various_status_codes(self):
        """Test http-error with various HTTP status codes."""
        status_codes = [400, 401, 403, 404, 500, 502, 503, 504]

        for code in status_codes:
            config = f"""
            config test {{
                frontend web {{
                    bind *:80
                    mode: http
                    http-error {{
                        status: {code}
                        string: "Error {code}"
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.frontends[0].http_errors[0].status == code
            assert ir.frontends[0].http_errors[0].string == f"Error {code}"

    def test_http_error_lf_file_codegen(self):
        """Test http-error with lf-file code generation."""
        config = """
        config test {
            backend api {
                mode: http
                http-error {
                    status: 500
                    lf-file: "/errors/500.lf"
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
        assert "http-error status 500 lf-file /errors/500.lf" in output

    def test_http_error_errorfile_codegen(self):
        """Test http-error with errorfile code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-error {
                    status: 403
                    errorfile: "/errors/403.html"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "http-error status 403 errorfile /errors/403.html" in output

    def test_http_error_listen_codegen(self):
        """Test http-error in listen section code generation."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                http-error {
                    status: 404
                    content-type: "application/json"
                    string: "{error: not found}"
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
        assert "http-error status 404 content-type application/json" in output
        assert 'string "{error: not found}"' in output
