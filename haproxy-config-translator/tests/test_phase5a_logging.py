"""Tests for Phase 5A-1: Enhanced logging directives.

Tests for error-log-format, log-format-sd, errorfiles, and dispatch directives.
"""

from haproxy_translator.parsers import DSLParser


class TestErrorLogFormat:
    """Test error-log-format directive."""

    def test_frontend_error_log_format(self):
        """Test frontend error-log-format directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                error-log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert ir.frontends[0].error_log_format is not None
        assert "%ci:%cp" in ir.frontends[0].error_log_format
        assert "%ST" in ir.frontends[0].error_log_format

    def test_backend_error_log_format(self):
        """Test backend error-log-format directive."""
        config = """
        config test {
            backend api {
                mode: http
                error-log-format: "%ci:%cp [%tr] %ft %b/%s %ST %B %CC %tsc"
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].error_log_format is not None
        assert "%ci:%cp" in ir.backends[0].error_log_format
        assert "%tsc" in ir.backends[0].error_log_format


class TestLogFormatSD:
    """Test log-format-sd directive (RFC 5424 structured data)."""

    def test_frontend_log_format_sd(self):
        """Test frontend log-format-sd directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                log-format-sd: "[request@1234 clientip=\\"%ci\\" method=\\"%HM\\" uri=\\"%HU\\"]"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert ir.frontends[0].log_format_sd is not None
        assert "request@1234" in ir.frontends[0].log_format_sd
        assert "clientip" in ir.frontends[0].log_format_sd

    def test_backend_log_format_sd(self):
        """Test backend log-format-sd directive."""
        config = """
        config test {
            backend api {
                mode: http
                log-format-sd: "[backend@1234 server=\\"%s\\" status=\\"%ST\\"]"
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].log_format_sd is not None
        assert "backend@1234" in ir.backends[0].log_format_sd
        assert "status" in ir.backends[0].log_format_sd


class TestErrorfiles:
    """Test errorfiles directive."""

    def test_backend_errorfiles(self):
        """Test backend errorfiles directive."""
        config = """
        config test {
            backend api {
                mode: http
                errorfiles: "/etc/haproxy/errors"
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].errorfiles == "/etc/haproxy/errors"

    def test_backend_errorfiles_custom_path(self):
        """Test backend errorfiles with custom path."""
        config = """
        config test {
            backend web {
                mode: http
                errorfiles: "/var/www/errors/custom"
                servers {
                    server web1 { address: "192.168.1.10" port: 80 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].errorfiles == "/var/www/errors/custom"


class TestDispatch:
    """Test dispatch directive."""

    def test_backend_dispatch(self):
        """Test backend dispatch directive."""
        config = """
        config test {
            backend simple {
                mode: http
                dispatch: "192.168.1.10:8080"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].dispatch == "192.168.1.10:8080"

    def test_backend_dispatch_ipv6(self):
        """Test backend dispatch with IPv6 address."""
        config = """
        config test {
            backend ipv6_simple {
                mode: http
                dispatch: "[::1]:8080"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].dispatch == "[::1]:8080"


class TestIntegration:
    """Integration tests combining multiple new directives."""

    def test_frontend_all_logging_directives(self):
        """Test frontend with all logging directives."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                log: "global"
                log-tag: "frontend-web"
                log-format: "%ci:%cp [%tr] %ft %b/%s"
                error-log-format: "%ci:%cp [%tr] ERROR %ft %ST"
                log-format-sd: "[request@1234 client=\\"%ci\\"]"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        frontend = ir.frontends[0]
        assert frontend.log_tag == "frontend-web"
        assert frontend.log_format is not None
        assert frontend.error_log_format is not None
        assert frontend.log_format_sd is not None
        assert "ERROR" in frontend.error_log_format
        assert "request@1234" in frontend.log_format_sd

    def test_backend_all_new_directives(self):
        """Test backend with all new directives."""
        config = """
        config test {
            backend api {
                mode: http
                balance: roundrobin
                log: "global"
                log-format: "%ci:%cp [%tr] %b/%s %ST"
                error-log-format: "%ci:%cp ERROR %ST %B"
                log-format-sd: "[backend@1234 status=\\"%ST\\"]"
                errorfiles: "/etc/haproxy/errors/api"
                servers {
                    server api1 { address: "10.0.1.1" port: 8080 }
                    server api2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        backend = ir.backends[0]
        assert backend.log_format is not None
        assert backend.error_log_format is not None
        assert backend.log_format_sd is not None
        assert backend.errorfiles == "/etc/haproxy/errors/api"
        assert len(backend.servers) == 2

    def test_dispatch_without_servers(self):
        """Test dispatch can be used without server definitions."""
        config = """
        config test {
            backend simple_lb {
                mode: http
                dispatch: "10.0.1.100:80"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        backend = ir.backends[0]
        assert backend.dispatch == "10.0.1.100:80"
        assert len(backend.servers) == 0  # No servers needed with dispatch

    def test_complete_logging_stack(self):
        """Test complete logging stack with all features."""
        config = """
        config test {
            frontend https_frontend {
                bind *:443
                mode: http
                log: "127.0.0.1:514 local0"
                log-tag: "https-frontend"
                log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B"
                error-log-format: "%ci:%cp [%tr] ERROR %ft %b/%s %ST %B %CC %CS"
                log-format-sd: "[request@12345 client=\\"%ci\\" method=\\"%HM\\" uri=\\"%HU\\" status=\\"%ST\\"]"

                default_backend: api_backend
            }

            backend api_backend {
                mode: http
                balance: leastconn
                log: "127.0.0.1:514 local1"
                log-format: "%ci:%cp [%tr] %b/%s %ST %B %Tq/%Tw/%Tc/%Tr/%Ta"
                error-log-format: "%ci:%cp [%tr] ERROR %b/%s %ST %B"
                log-format-sd: "[backend@12345 server=\\"%s\\" status=\\"%ST\\" bytes=\\"%B\\"]"
                errorfiles: "/etc/haproxy/errors/api"

                servers {
                    server api1 { address: "10.0.1.1" port: 8080 check: true }
                    server api2 { address: "10.0.1.2" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Validate frontend
        frontend = ir.frontends[0]
        assert frontend.log_format is not None
        assert frontend.error_log_format is not None
        assert frontend.log_format_sd is not None
        assert "%TR/%Tw/%Tc/%Tr/%Ta" in frontend.log_format
        assert "ERROR" in frontend.error_log_format
        assert "request@12345" in frontend.log_format_sd

        # Validate backend
        backend = ir.backends[0]
        assert backend.log_format is not None
        assert backend.error_log_format is not None
        assert backend.log_format_sd is not None
        assert backend.errorfiles == "/etc/haproxy/errors/api"
        assert "backend@12345" in backend.log_format_sd
        assert len(backend.servers) == 2
