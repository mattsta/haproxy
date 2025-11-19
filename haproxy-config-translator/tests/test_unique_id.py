"""Tests for unique-id-format and unique-id-header directives (Phases 4K, 4L)."""

import pytest
from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestUniqueIdFormat:
    """Test unique-id-format directive in frontend."""

    def test_frontend_unique_id_format_basic(self):
        """Test frontend with basic unique-id-format."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                unique-id-format: "%{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid"

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

        assert ir.frontends[0].unique_id_format == "%{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid"
        assert "unique-id-format %{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid" in output

    def test_frontend_unique_id_format_simple(self):
        """Test frontend with simple unique-id-format."""
        config = """
        config test {
            frontend api {
                bind *:443
                mode: http
                unique-id-format: "%[uuid()]"

                default_backend: api_backend
            }

            backend api_backend {
                servers {
                    server api1 {
                        address: "10.0.1.1"
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

        assert ir.frontends[0].unique_id_format == "%[uuid()]"
        assert "unique-id-format %[uuid()]" in output


class TestUniqueIdHeader:
    """Test unique-id-header directive in frontend."""

    def test_frontend_unique_id_header_basic(self):
        """Test frontend with unique-id-header."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                unique-id-header: "X-Request-ID"

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

        assert ir.frontends[0].unique_id_header == "X-Request-ID"
        assert "unique-id-header X-Request-ID" in output

    def test_frontend_unique_id_header_custom(self):
        """Test frontend with custom unique-id-header."""
        config = """
        config test {
            frontend api {
                bind *:443
                mode: http
                unique-id-header: "X-Trace-ID"

                default_backend: api_backend
            }

            backend api_backend {
                servers {
                    server api1 {
                        address: "10.0.1.1"
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

        assert ir.frontends[0].unique_id_header == "X-Trace-ID"
        assert "unique-id-header X-Trace-ID" in output


class TestUniqueIdIntegration:
    """Test unique-id directives together and with other features."""

    def test_frontend_both_unique_id_directives(self):
        """Test frontend with both unique-id-format and unique-id-header."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                unique-id-format: "%{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid"
                unique-id-header: "X-Request-ID"

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

        # Verify IR
        frontend = ir.frontends[0]
        assert frontend.unique_id_format == "%{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid"
        assert frontend.unique_id_header == "X-Request-ID"

        # Verify output
        assert "unique-id-format %{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid" in output
        assert "unique-id-header X-Request-ID" in output

    def test_frontend_unique_id_with_logging(self):
        """Test unique-id directives with logging configuration."""
        config = """
        config production {
            frontend api {
                bind *:443
                mode: http

                // Logging
                log: "127.0.0.1:514 local0 info"
                log-tag: "api-gateway"
                log-format: "%ci:%cp [%tr] %ft %b/%s %TR/%Tw/%Tc/%Tr/%Ta %ST %B %CC %CS %tsc %ac/%fc/%bc/%sc/%rc %sq/%bq %hr %hs %{+Q}r"

                // Request tracking
                unique-id-format: "%{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid"
                unique-id-header: "X-Request-ID"

                default_backend: api_backend
            }

            backend api_backend {
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
        assert len(frontend.log) == 1
        assert frontend.log_tag == "api-gateway"
        assert frontend.log_format is not None
        assert frontend.unique_id_format == "%{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid"
        assert frontend.unique_id_header == "X-Request-ID"

        # Verify output
        assert "log 127.0.0.1:514 local0 info" in output
        assert "log-tag api-gateway" in output
        assert "log-format" in output
        assert "unique-id-format %{+X}o %ci:%cp_%fi:%fp_%Ts_%rt:%pid" in output
        assert "unique-id-header X-Request-ID" in output

    def test_complete_tracing_configuration(self):
        """Test complete request tracing configuration."""
        config = """
        config production {
            frontend web_frontend {
                bind *:80
                bind *:443
                mode: http

                // Metadata
                description: "Production web traffic with request tracing"
                id: 100

                // Capacity
                maxconn: 50000
                backlog: 8192

                // Request tracing
                unique-id-format: "%[uuid()]"
                unique-id-header: "X-Unique-ID"

                // Logging with unique ID
                log: "127.0.0.1:514 local0"
                log-tag: "web-frontend"
                log-format: "%{+Q}o %{-Q}ci - - [%trg] %r %ST %B %cp %ms %ft %b %s %TR %Tw %Tc %Tr %Ta %tsc %ac %fc %bc %sc %rc %sq %bq %CC %CS %hrl %hsl"

                // Monitoring
                monitor_uri: "/health"

                // Timeouts
                timeout_client: 30s
                timeout_http_request: 10s

                default_backend: web_backend
            }

            backend web_backend {
                mode: http
                balance: roundrobin

                description: "Web server backend pool"
                id: 200

                maxconn: 30000

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
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify frontend IR
        frontend = ir.frontends[0]
        assert frontend.description == "Production web traffic with request tracing"
        assert frontend.id == 100
        assert frontend.maxconn == 50000
        assert frontend.backlog == 8192
        assert frontend.unique_id_format == "%[uuid()]"
        assert frontend.unique_id_header == "X-Unique-ID"
        assert len(frontend.log) == 1
        assert frontend.log_tag == "web-frontend"
        assert frontend.monitor_uri == "/health"

        # Verify backend IR
        backend = ir.backends[0]
        assert backend.description == "Web server backend pool"
        assert backend.id == 200
        assert backend.maxconn == 30000

        # Verify output
        assert "frontend web_frontend" in output
        assert "description Production web traffic with request tracing" in output
        assert "id 100" in output
        assert "maxconn 50000" in output
        assert "backlog 8192" in output
        assert "unique-id-format %[uuid()]" in output
        assert "unique-id-header X-Unique-ID" in output
        assert "log 127.0.0.1:514 local0" in output
        assert "log-tag web-frontend" in output
        assert "monitor-uri /health" in output

        assert "backend web_backend" in output
        assert "description Web server backend pool" in output
        assert "id 200" in output
        assert "maxconn 30000" in output

    def test_distributed_tracing_setup(self):
        """Test configuration for distributed tracing scenario."""
        config = """
        config microservices {
            frontend api_gateway {
                bind *:8080
                mode: http

                description: "Microservices API gateway with distributed tracing"

                // Generate UUID for each request
                unique-id-format: "%[uuid()]"
                unique-id-header: "X-Trace-ID"

                // Log with trace ID
                log: "127.0.0.1:514 local0"
                log-format: "trace_id=%[unique-id] client_ip=%ci request=\\\"%r\\\" status=%ST bytes=%B"

                default_backend: services
            }

            backend services {
                mode: http
                balance: leastconn

                description: "Microservices backend"

                servers {
                    server svc1 {
                        address: "10.0.1.1"
                        port: 9000
                        check: true
                    }
                    server svc2 {
                        address: "10.0.1.2"
                        port: 9000
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
        assert frontend.description == "Microservices API gateway with distributed tracing"
        assert frontend.unique_id_format == "%[uuid()]"
        assert frontend.unique_id_header == "X-Trace-ID"
        assert len(frontend.log) == 1
        assert "trace_id=%[unique-id]" in frontend.log_format

        # Verify output
        assert "unique-id-format %[uuid()]" in output
        assert "unique-id-header X-Trace-ID" in output
        assert "log-format" in output
        assert "trace_id=%[unique-id]" in output

    def test_unique_id_with_stats(self):
        """Test unique-id directives with stats configuration."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                unique-id-format: "%[uuid()]"
                unique-id-header: "X-Request-ID"

                stats {
                    enable: true
                    uri: "/stats"
                    realm: "HAProxy Stats"
                }

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

        # Verify IR
        frontend = ir.frontends[0]
        assert frontend.unique_id_format == "%[uuid()]"
        assert frontend.unique_id_header == "X-Request-ID"
        assert frontend.stats_config is not None
        assert frontend.stats_config.enable is True

        # Verify output
        assert "unique-id-format %[uuid()]" in output
        assert "unique-id-header X-Request-ID" in output
        assert "stats enable" in output
        assert "stats uri /stats" in output
