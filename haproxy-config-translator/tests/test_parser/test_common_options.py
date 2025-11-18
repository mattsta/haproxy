"""Test common HAProxy options that are critical for production use."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestCriticalOptions:
    """Test critical HAProxy options for production deployments."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_option_forwardfor(self, parser, codegen):
        """Test option forwardfor - preserves client IP (99% of deployments need this)."""
        source = """
        config test {
            defaults {
                mode: http
                option: ["forwardfor"]
            }

            frontend web {
                bind *:80
                option: ["forwardfor"]
            }

            backend api {
                balance: roundrobin
                option: ["forwardfor"]
            }
        }
        """
        ir = parser.parse(source)

        # Verify defaults
        assert "forwardfor" in ir.defaults.options

        # Verify frontend
        frontend = ir.frontends[0]
        assert "forwardfor" in frontend.options

        # Verify backend
        backend = ir.backends[0]
        assert "forwardfor" in backend.options

        # Test code generation
        output = codegen.generate(ir)
        # Count occurrences - should appear in defaults, frontend, and backend
        assert output.count("option forwardfor") >= 3

    def test_option_http_keep_alive(self, parser, codegen):
        """Test option http-keep-alive - performance tuning."""
        source = """
        config test {
            defaults {
                mode: http
                option: ["http-keep-alive"]
            }
        }
        """
        ir = parser.parse(source)
        assert "http-keep-alive" in ir.defaults.options

        output = codegen.generate(ir)
        assert "option http-keep-alive" in output

    def test_option_httplog(self, parser, codegen):
        """Test option httplog - HTTP logging format."""
        source = """
        config test {
            frontend web {
                bind *:80
                option: ["httplog"]
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert "httplog" in frontend.options

        output = codegen.generate(ir)
        assert "option httplog" in output

    def test_option_http_server_close(self, parser, codegen):
        """Test option http-server-close - connection management."""
        source = """
        config test {
            defaults {
                mode: http
                option: ["http-server-close"]
            }
        }
        """
        ir = parser.parse(source)
        assert "http-server-close" in ir.defaults.options

        output = codegen.generate(ir)
        assert "option http-server-close" in output

    def test_option_redispatch(self, parser, codegen):
        """Test option redispatch - retry on server failure."""
        source = """
        config test {
            defaults {
                mode: http
                option: ["redispatch"]
                retries: 3
            }
        }
        """
        ir = parser.parse(source)
        assert "redispatch" in ir.defaults.options

        output = codegen.generate(ir)
        assert "option redispatch" in output

    def test_multiple_options(self, parser, codegen):
        """Test multiple options in array format."""
        source = """
        config test {
            frontend web {
                bind *:80
                option: ["httplog", "forwardfor", "http-server-close"]
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]

        assert "httplog" in frontend.options
        assert "forwardfor" in frontend.options
        assert "http-server-close" in frontend.options
        assert len(frontend.options) == 3

        output = codegen.generate(ir)
        assert "option httplog" in output
        assert "option forwardfor" in output
        assert "option http-server-close" in output

    def test_option_tcplog(self, parser, codegen):
        """Test option tcplog - TCP logging format."""
        source = """
        config test {
            defaults {
                mode: tcp
                option: ["tcplog"]
            }
        }
        """
        ir = parser.parse(source)
        assert "tcplog" in ir.defaults.options

        output = codegen.generate(ir)
        assert "option tcplog" in output

    def test_option_dontlognull(self, parser, codegen):
        """Test option dontlognull - don't log connections with no data."""
        source = """
        config test {
            defaults {
                mode: http
                option: ["dontlognull"]
            }
        }
        """
        ir = parser.parse(source)
        assert "dontlognull" in ir.defaults.options

        output = codegen.generate(ir)
        assert "option dontlognull" in output

    def test_option_httpchk(self, parser, codegen):
        """Test option httpchk - HTTP health checks."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                option: ["httpchk"]
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert "httpchk" in backend.options

        output = codegen.generate(ir)
        assert "option httpchk" in output

    def test_comprehensive_production_config(self, parser, codegen):
        """Test comprehensive production-ready configuration with all critical options."""
        source = """
        config production {
            global {
                daemon: true
                maxconn: 4096
            }

            defaults {
                mode: http
                retries: 3
                option: ["httplog", "dontlognull", "http-server-close", "forwardfor", "redispatch"]
                timeout: {
                    connect: 5s
                    client: 50s
                    server: 50s
                }
            }

            frontend web {
                bind *:80
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    alpn: ["h2", "http/1.1"]
                }
                option: ["httplog", "forwardfor"]
                default_backend: api
            }

            backend api {
                balance: roundrobin
                option: ["httplog", "forwardfor", "httpchk"]

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                        inter: 5s
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                        inter: 5s
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Verify all options are present
        assert "httplog" in ir.defaults.options
        assert "dontlognull" in ir.defaults.options
        assert "http-server-close" in ir.defaults.options
        assert "forwardfor" in ir.defaults.options
        assert "redispatch" in ir.defaults.options

        # Test code generation
        output = codegen.generate(ir)

        # Verify critical elements in output
        assert "option httplog" in output
        assert "option forwardfor" in output
        assert "option http-server-close" in output
        assert "option redispatch" in output
        assert "option httpchk" in output
        assert "bind *:443 ssl" in output
        assert "crt /etc/ssl/cert.pem" in output
        assert "server api1 10.0.1.1:8080 check inter 5s" in output
        assert "server api2 10.0.1.2:8080 check inter 5s" in output
