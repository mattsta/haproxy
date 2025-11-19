"""Tests for use-fcgi-app directive (FastCGI application reference)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestUseFcgiApp:
    """Test use-fcgi-app directive."""

    def test_backend_use_fcgi_app(self):
        """Test backend use-fcgi-app directive."""
        config = """
        config test {
            backend php_app {
                mode: http
                use-fcgi-app: "php-fpm"
                servers {
                    server app1 { address: "127.0.0.1" port: 9000 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].use_fcgi_app == "php-fpm"

    def test_backend_use_fcgi_app_codegen(self):
        """Test backend use-fcgi-app code generation."""
        config = """
        config test {
            backend php_app {
                mode: http
                balance: roundrobin
                use-fcgi-app: "php-fpm"
                servers {
                    server app1 { address: "127.0.0.1" port: 9000 }
                    server app2 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "use-fcgi-app php-fpm" in output
        assert "backend php_app" in output
        assert "server app1 127.0.0.1:9000" in output
        assert "server app2 127.0.0.1:9001" in output

    def test_backend_without_use_fcgi_app(self):
        """Test backend without use-fcgi-app (should be None)."""
        config = """
        config test {
            backend web {
                mode: http
                servers {
                    server web1 { address: "192.168.1.10" port: 80 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].use_fcgi_app is None

    def test_multiple_backends_with_fcgi(self):
        """Test multiple backends with different FastCGI apps."""
        config = """
        config test {
            backend php_backend {
                mode: http
                use-fcgi-app: "php-fpm"
                servers {
                    server php1 { address: "127.0.0.1" port: 9000 }
                }
            }

            backend python_backend {
                mode: http
                use-fcgi-app: "python-fcgi"
                servers {
                    server py1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].use_fcgi_app == "php-fpm"
        assert ir.backends[1].use_fcgi_app == "python-fcgi"
