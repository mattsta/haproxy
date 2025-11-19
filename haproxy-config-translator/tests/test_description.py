"""Tests for description directive (Phase 4H)."""

import pytest
from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestFrontendDescription:
    """Test description directive in frontend."""

    def test_frontend_description(self):
        """Test frontend with description."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                description: "Main web frontend for HTTP traffic"

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.frontends[0].description == "Main web frontend for HTTP traffic"
        assert "description Main web frontend for HTTP traffic" in output


class TestBackendDescription:
    """Test description directive in backend."""

    def test_backend_description(self):
        """Test backend with description."""
        config = """
        config test {
            backend app {
                mode: http
                description: "Application server backend pool"

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].description == "Application server backend pool"
        assert "description Application server backend pool" in output


class TestListenDescription:
    """Test description directive in listen."""

    def test_listen_description(self):
        """Test listen with description."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                description: "Statistics and monitoring endpoint"

                servers {
                    server stats_srv {
                        address: "127.0.0.1"
                        port: 9090
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.listens[0].description == "Statistics and monitoring endpoint"
        assert "description Statistics and monitoring endpoint" in output


class TestDescriptionIntegration:
    """Test description with other directives."""

    def test_frontend_with_description_and_stats(self):
        """Test frontend with description and stats."""
        config = """
        config production {
            frontend api {
                bind *:443
                mode: http
                description: "API gateway - handles all external API requests"

                maxconn: 10000
                backlog: 2048

                stats {
                    enable: true
                    uri: "/stats"
                }

                default_backend: api_backend
            }

            backend api_backend {
                description: "Backend pool for API servers"
                mode: http
                balance: leastconn

                maxconn: 5000

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify IR
        frontend = ir.frontends[0]
        backend = ir.backends[0]

        assert frontend.description == "API gateway - handles all external API requests"
        assert backend.description == "Backend pool for API servers"

        # Verify output
        assert "description API gateway - handles all external API requests" in output
        assert "description Backend pool for API servers" in output
        assert "stats enable" in output

    def test_complete_config_with_descriptions(self):
        """Test complete configuration with descriptions everywhere."""
        config = """
        config production {
            frontend web_frontend {
                bind *:80
                bind *:443
                mode: http
                description: "Production web traffic frontend - HTTP and HTTPS"

                maxconn: 50000
                backlog: 8192

                timeout_client: 30s
                timeout_http_request: 10s

                monitor_uri: "/health"

                default_backend: web_backend
            }

            backend web_backend {
                mode: http
                balance: roundrobin
                description: "Web server backend pool with round-robin distribution"

                maxconn: 30000
                backlog: 4096

                http-reuse: safe

                timeout_connect: 5s
                timeout_server: 30s

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                        maxconn: 500
                    }
                    server web2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                        maxconn: 500
                    }
                }
            }

            listen admin_stats {
                bind *:9999
                mode: http
                description: "Administrative statistics and monitoring dashboard"

                servers {
                    server stats1 {
                        address: "127.0.0.1"
                        port: 9000
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify frontend
        frontend = ir.frontends[0]
        assert frontend.description == "Production web traffic frontend - HTTP and HTTPS"
        assert frontend.maxconn == 50000
        assert frontend.backlog == 8192

        # Verify backend
        backend = ir.backends[0]
        assert backend.description == "Web server backend pool with round-robin distribution"
        assert backend.maxconn == 30000
        assert backend.backlog == 4096

        # Verify listen
        listen = ir.listens[0]
        assert listen.description == "Administrative statistics and monitoring dashboard"

        # Verify output
        assert "frontend web_frontend" in output
        assert "description Production web traffic frontend - HTTP and HTTPS" in output

        assert "backend web_backend" in output
        assert "description Web server backend pool with round-robin distribution" in output

        assert "listen admin_stats" in output
        assert "description Administrative statistics and monitoring dashboard" in output

    def test_description_with_special_characters(self):
        """Test description with special characters and formatting."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                description: "Web frontend - handles traffic for example.com & api.example.com"

                default_backend: app
            }

            backend app {
                description: "App servers (production): load balanced with RR algorithm"

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.frontends[0].description == "Web frontend - handles traffic for example.com & api.example.com"
        assert ir.backends[0].description == "App servers (production): load balanced with RR algorithm"

        assert "description Web frontend - handles traffic for example.com & api.example.com" in output
        assert "description App servers (production): load balanced with RR algorithm" in output
