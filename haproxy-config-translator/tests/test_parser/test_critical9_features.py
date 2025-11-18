"""Test Critical 9 features for HAProxy parity."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestCritical9Features:
    """Test the Critical 9 features implementation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_frontend_log_format(self, parser, codegen):
        """Test custom log-format in frontend."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                log-format: "%ci:%cp [%t] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Tt %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]

        assert frontend.log_format is not None
        assert "%ci:%cp" in frontend.log_format

        output = codegen.generate(ir)
        assert "log-format" in output
        assert "%ci:%cp" in output

    def test_backend_log_format(self, parser, codegen):
        """Test custom log-format in backend."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                mode: http
                log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC"
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]

        assert backend.log_format is not None
        assert "%TR" in backend.log_format

        output = codegen.generate(ir)
        assert "log-format" in output
        assert "%TR" in output

    def test_capture_request_headers(self, parser, codegen):
        """Test capture request header."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                capture request header "X-Forwarded-For" 15
                capture request header "User-Agent" 128
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]

        assert len(frontend.capture_request_headers) == 2
        assert ("X-Forwarded-For", 15) in frontend.capture_request_headers
        assert ("User-Agent", 128) in frontend.capture_request_headers

        output = codegen.generate(ir)
        assert "capture request header X-Forwarded-For len 15" in output
        assert "capture request header User-Agent len 128" in output

    def test_capture_response_headers(self, parser, codegen):
        """Test capture response header."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                capture response header "Content-Type" 64
                capture response header "Set-Cookie" 128
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]

        assert len(frontend.capture_response_headers) == 2
        assert ("Content-Type", 64) in frontend.capture_response_headers
        assert ("Set-Cookie", 128) in frontend.capture_response_headers

        output = codegen.generate(ir)
        assert "capture response header Content-Type len 64" in output
        assert "capture response header Set-Cookie len 128" in output

    def test_server_check_ssl(self, parser, codegen):
        """Test server check-ssl option."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                        check: true
                        check-ssl: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        server = ir.backends[0].servers[0]

        assert server.check_ssl is True

        output = codegen.generate(ir)
        assert "check-ssl" in output

    def test_server_check_sni(self, parser, codegen):
        """Test server check-sni option."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                        check: true
                        check-ssl: true
                        check-sni: "api.example.com"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        server = ir.backends[0].servers[0]

        assert server.check_sni == "api.example.com"

        output = codegen.generate(ir)
        assert "check-sni api.example.com" in output

    def test_server_ssl_version_constraints(self, parser, codegen):
        """Test server SSL version constraints."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                        ssl: true
                        ssl-min-ver: "TLSv1.2"
                        ssl-max-ver: "TLSv1.3"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        server = ir.backends[0].servers[0]

        assert server.ssl_min_ver == "TLSv1.2"
        assert server.ssl_max_ver == "TLSv1.3"

        output = codegen.generate(ir)
        assert "ssl-min-ver TLSv1.2" in output
        assert "ssl-max-ver TLSv1.3" in output

    def test_server_ca_file(self, parser, codegen):
        """Test server ca-file option."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                        ssl: true
                        ca-file: "/etc/ssl/certs/ca-bundle.crt"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        server = ir.backends[0].servers[0]

        assert server.ca_file == "/etc/ssl/certs/ca-bundle.crt"

        output = codegen.generate(ir)
        assert "ca-file /etc/ssl/certs/ca-bundle.crt" in output

    def test_server_crt(self, parser, codegen):
        """Test server crt option for mutual TLS."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                        ssl: true
                        crt: "/etc/ssl/client/cert.pem"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        server = ir.backends[0].servers[0]

        assert server.crt == "/etc/ssl/client/cert.pem"

        output = codegen.generate(ir)
        assert "crt /etc/ssl/client/cert.pem" in output

    def test_server_source(self, parser, codegen):
        """Test server source IP binding."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        source: "192.168.1.100"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        server = ir.backends[0].servers[0]

        assert server.source == "192.168.1.100"

        output = codegen.generate(ir)
        assert "source 192.168.1.100" in output

    def test_default_server_ssl_options(self, parser, codegen):
        """Test default-server with SSL options."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: api
            }
            backend api {
                default-server {
                    check: true
                    check-ssl: true
                    check-sni: "api.example.com"
                    ssl-min-ver: "TLSv1.2"
                    ca-file: "/etc/ssl/certs/ca-bundle.crt"
                }
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8443
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        default_server = ir.backends[0].default_server

        assert default_server is not None
        assert default_server.check_ssl is True
        assert default_server.check_sni == "api.example.com"
        assert default_server.ssl_min_ver == "TLSv1.2"
        assert default_server.ca_file == "/etc/ssl/certs/ca-bundle.crt"

        output = codegen.generate(ir)
        assert "default-server" in output
        assert "check-ssl" in output
        assert "check-sni api.example.com" in output
        assert "ssl-min-ver TLSv1.2" in output
        assert "ca-file /etc/ssl/certs/ca-bundle.crt" in output

    def test_production_config_with_all_critical9(self, parser, codegen):
        """Test production-like config with all Critical 9 features."""
        source = """
        config production {
            global {
                daemon: true
                maxconn: 50000
            }

            defaults {
                mode: http
                timeout: {
                    connect: 5s
                    client: 30s
                    server: 30s
                }
            }

            frontend https {
                bind *:443 ssl {
                    cert: "/etc/ssl/production.pem"
                    alpn: ["h2", "http/1.1"]
                } accept-proxy true

                mode: http
                log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC %CS %tsc"
                capture request header "X-Forwarded-For" 15
                capture request header "User-Agent" 128
                capture response header "Content-Type" 64

                default_backend: backend_pool
            }

            backend backend_pool {
                mode: http
                balance: leastconn
                log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B"

                default-server {
                    check: true
                    check-ssl: true
                    check-sni: "api.example.com"
                    ssl-min-ver: "TLSv1.2"
                    ssl-max-ver: "TLSv1.3"
                    ca-file: "/etc/ssl/certs/ca-bundle.crt"
                }

                servers {
                    server backend1 {
                        address: "10.0.1.1"
                        port: 8443
                        ssl: true
                        source: "192.168.1.100"
                        crt: "/etc/ssl/client/cert.pem"
                    }
                    server backend2 {
                        address: "10.0.1.2"
                        port: 8443
                        ssl: true
                        source: "192.168.1.100"
                        crt: "/etc/ssl/client/cert.pem"
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Verify frontend features
        frontend = ir.frontends[0]
        assert frontend.log_format is not None
        assert len(frontend.capture_request_headers) == 2
        assert len(frontend.capture_response_headers) == 1
        assert frontend.binds[0].options["accept-proxy"] is True

        # Verify backend features
        backend = ir.backends[0]
        assert backend.log_format is not None
        assert backend.default_server is not None
        assert backend.default_server.check_ssl is True
        assert backend.default_server.check_sni == "api.example.com"
        assert backend.default_server.ssl_min_ver == "TLSv1.2"
        assert backend.default_server.ssl_max_ver == "TLSv1.3"

        # Verify server features
        server = backend.servers[0]
        assert server.source == "192.168.1.100"
        assert server.crt == "/etc/ssl/client/cert.pem"

        # Verify codegen
        output = codegen.generate(ir)
        assert "log-format" in output
        assert "capture request header" in output
        assert "capture response header" in output
        assert "check-ssl" in output
        assert "check-sni" in output
        assert "ssl-min-ver" in output
        assert "ssl-max-ver" in output
        assert "ca-file" in output
        assert "source 192.168.1.100" in output
        assert "crt /etc/ssl/client/cert.pem" in output
        assert "accept-proxy" in output
