"""Tests for Phase 5A-2: Error location redirect directives.

Tests for errorloc, errorloc302, and errorloc303 directives.
"""

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestErrorloc:
    """Test errorloc directive (302 redirect by default)."""

    def test_frontend_errorloc(self):
        """Test frontend errorloc directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                errorloc 503 "/errors/503.html"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert 503 in ir.frontends[0].errorloc
        assert ir.frontends[0].errorloc[503] == "/errors/503.html"

    def test_backend_errorloc(self):
        """Test backend errorloc directive."""
        config = """
        config test {
            backend api {
                mode: http
                errorloc 503 "/errors/api-503.html"
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert 503 in ir.backends[0].errorloc
        assert ir.backends[0].errorloc[503] == "/errors/api-503.html"


class TestErrorloc302:
    """Test errorloc302 directive (explicit 302 Found)."""

    def test_frontend_errorloc302(self):
        """Test frontend errorloc302 directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                errorloc302 503 http://status.example.com/503
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert 503 in ir.frontends[0].errorloc302
        assert ir.frontends[0].errorloc302[503] == "http://status.example.com/503"

    def test_backend_errorloc302(self):
        """Test backend errorloc302 directive."""
        config = """
        config test {
            backend api {
                mode: http
                errorloc302 500 http://status.example.com/api/500
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert 500 in ir.backends[0].errorloc302
        assert ir.backends[0].errorloc302[500] == "http://status.example.com/api/500"


class TestErrorloc303:
    """Test errorloc303 directive (303 See Other)."""

    def test_frontend_errorloc303(self):
        """Test frontend errorloc303 directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                errorloc303 503 http://maintenance.example.com
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert 503 in ir.frontends[0].errorloc303
        assert ir.frontends[0].errorloc303[503] == "http://maintenance.example.com"

    def test_backend_errorloc303(self):
        """Test backend errorloc303 directive."""
        config = """
        config test {
            backend web {
                mode: http
                errorloc303 503 http://maintenance.example.com/backend
                servers {
                    server web1 { address: "192.168.1.10" port: 80 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert 503 in ir.backends[0].errorloc303
        assert ir.backends[0].errorloc303[503] == "http://maintenance.example.com/backend"


class TestErrorlocIntegration:
    """Integration tests for errorloc directives."""

    def test_all_errorloc_variants_frontend(self):
        """Test frontend with all errorloc variants."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                errorloc 503 "/errors/503.html"
                errorloc302 502 http://status.example.com/502
                errorloc303 500 http://maintenance.example.com/500
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        frontend = ir.frontends[0]

        # Check errorloc (302)
        assert 503 in frontend.errorloc
        assert frontend.errorloc[503] == "/errors/503.html"

        # Check errorloc302
        assert 502 in frontend.errorloc302
        assert frontend.errorloc302[502] == "http://status.example.com/502"

        # Check errorloc303
        assert 500 in frontend.errorloc303
        assert frontend.errorloc303[500] == "http://maintenance.example.com/500"

    def test_all_errorloc_variants_backend(self):
        """Test backend with all errorloc variants."""
        config = """
        config test {
            backend api {
                mode: http
                errorloc 503 "/errors/api-503.html"
                errorloc302 502 http://status.example.com/api-502
                errorloc303 500 http://maintenance.example.com/api-500
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        backend = ir.backends[0]

        assert 503 in backend.errorloc
        assert backend.errorloc[503] == "/errors/api-503.html"
        assert 502 in backend.errorloc302
        assert backend.errorloc302[502] == "http://status.example.com/api-502"
        assert 500 in backend.errorloc303
        assert backend.errorloc303[500] == "http://maintenance.example.com/api-500"

    def test_errorloc_codegen_frontend(self):
        """Test frontend errorloc code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                errorloc 503 "/errors/503.html"
                errorloc302 502 http://status.example.com/502
                errorloc303 500 http://maintenance.example.com/500
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "errorloc 503 "/errors/503.html" in output
        assert "errorloc302 502 http://status.example.com/502" in output
        assert "errorloc303 500 http://maintenance.example.com/500" in output

    def test_errorloc_codegen_backend(self):
        """Test backend errorloc code generation."""
        config = """
        config test {
            backend api {
                mode: http
                errorloc 503 "/errors/api-503.html"
                errorloc302 502 http://status.example.com/api-502
                errorloc303 500 http://maintenance.example.com/api-500
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

        assert "errorloc 503 "/errors/api-503.html" in output
        assert "errorloc302 502 http://status.example.com/api-502" in output
        assert "errorloc303 500 http://maintenance.example.com/api-500" in output

    def test_multiple_error_codes_same_directive(self):
        """Test multiple error codes with same directive type."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                errorloc 500 "/errors/500.html"
                errorloc 502 "/errors/502.html"
                errorloc 503 "/errors/503.html"
                errorloc 504 "/errors/504.html"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        frontend = ir.frontends[0]

        assert len(frontend.errorloc) == 4
        assert frontend.errorloc[500] == "/errors/500.html"
        assert frontend.errorloc[502] == "/errors/502.html"
        assert frontend.errorloc[503] == "/errors/503.html"
        assert frontend.errorloc[504] == "/errors/504.html"
