"""Tests for HTTP resilience directives: http-send-name-header and retry-on (Phases 4O, 4P)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHttpSendNameHeader:
    """Test http-send-name-header directive in backend."""

    def test_backend_http_send_name_header_basic(self):
        """Test backend with http-send-name-header."""
        config = """
        config test {
            backend app {
                mode: http
                http-send-name-header: "X-Backend-Name"

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

        assert ir.backends[0].http_send_name_header == "X-Backend-Name"
        assert "http-send-name-header X-Backend-Name" in output

    def test_backend_http_send_name_header_custom(self):
        """Test backend with custom http-send-name-header."""
        config = """
        config test {
            backend api {
                mode: http
                balance: leastconn

                http-send-name-header: "X-Server-ID"

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server api2 {
                        address: "10.0.1.2"
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

        assert ir.backends[0].http_send_name_header == "X-Server-ID"
        assert "http-send-name-header X-Server-ID" in output


class TestRetryOn:
    """Test retry-on directive in backend."""

    def test_backend_retry_on_basic(self):
        """Test backend with basic retry-on."""
        config = """
        config test {
            backend app {
                mode: http
                retry-on: "conn-failure,empty-response,response-timeout"

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

        assert ir.backends[0].retry_on == "conn-failure,empty-response,response-timeout"
        assert "retry-on conn-failure,empty-response,response-timeout" in output

    def test_backend_retry_on_http_status(self):
        """Test backend with retry-on for HTTP status codes."""
        config = """
        config test {
            backend api {
                mode: http
                balance: roundrobin

                retry-on: "500,502,503,504"

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

        assert ir.backends[0].retry_on == "500,502,503,504"
        assert "retry-on 500,502,503,504" in output

    def test_backend_retry_on_all_retryable(self):
        """Test backend with retry-on all-retryable-errors."""
        config = """
        config test {
            backend database {
                mode: http
                balance: leastconn

                retry-on: "all-retryable-errors"

                servers {
                    server db1 {
                        address: "10.0.2.1"
                        port: 5432
                        check: true
                    }
                    server db2 {
                        address: "10.0.2.2"
                        port: 5432
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

        assert ir.backends[0].retry_on == "all-retryable-errors"
        assert "retry-on all-retryable-errors" in output


class TestHttpResilienceIntegration:
    """Test HTTP resilience directives together."""

    def test_backend_both_resilience_directives(self):
        """Test backend with both http-send-name-header and retry-on."""
        config = """
        config production {
            backend api_backend {
                mode: http
                balance: leastconn

                http-send-name-header: "X-Backend-Server"
                retry-on: "conn-failure,empty-response,500,502,503"

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server api2 {
                        address: "10.0.1.2"
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
        backend = ir.backends[0]
        assert backend.http_send_name_header == "X-Backend-Server"
        assert backend.retry_on == "conn-failure,empty-response,500,502,503"

        # Verify output
        assert "http-send-name-header X-Backend-Server" in output
        assert "retry-on conn-failure,empty-response,500,502,503" in output

    def test_backend_resilience_with_http_reuse(self):
        """Test resilience directives with http-reuse for connection pooling."""
        config = """
        config production {
            backend microservice {
                mode: http
                balance: roundrobin

                // Connection pooling
                http-reuse: safe

                // Observability
                http-send-name-header: "X-HAProxy-Server"

                // Resilience
                retry-on: "conn-failure,empty-response,response-timeout"

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
        backend = ir.backends[0]
        assert backend.http_reuse == "safe"
        assert backend.http_send_name_header == "X-HAProxy-Server"
        assert backend.retry_on == "conn-failure,empty-response,response-timeout"

        # Verify output
        assert "http-reuse safe" in output
        assert "http-send-name-header X-HAProxy-Server" in output
        assert "retry-on conn-failure,empty-response,response-timeout" in output

    def test_complete_resilient_backend(self):
        """Test complete resilient backend configuration."""
        config = """
        config high_availability {
            backend resilient_api {
                mode: http
                balance: leastconn

                description: "Highly resilient API backend"
                id: 300

                // Capacity
                maxconn: 5000
                max-keep-alive-queue: 100
                max-session-srv-conns: 8

                // Connection management
                http-reuse: aggressive

                // Observability
                http-send-name-header: "X-API-Server"

                // Resilience and retry
                retries: 3
                retry-on: "conn-failure,empty-response,junk-response,response-timeout,500,502,503,504"

                // Timeouts
                timeout_connect: 3s
                timeout_server: 10s
                timeout_check: 2s

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                        maxconn: 500
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                        maxconn: 500
                    }
                    server api3 {
                        address: "10.0.1.3"
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

        # Verify IR
        backend = ir.backends[0]
        assert backend.description == "Highly resilient API backend"
        assert backend.id == 300
        assert backend.maxconn == 5000
        assert backend.max_keep_alive_queue == 100
        assert backend.max_session_srv_conns == 8
        assert backend.http_reuse == "aggressive"
        assert backend.http_send_name_header == "X-API-Server"
        assert backend.retries == 3
        assert backend.retry_on == "conn-failure,empty-response,junk-response,response-timeout,500,502,503,504"
        assert backend.timeout_connect == "3s"
        assert backend.timeout_server == "10s"
        assert backend.timeout_check == "2s"

        # Verify output
        assert "backend resilient_api" in output
        assert "description Highly resilient API backend" in output
        assert "id 300" in output
        assert "maxconn 5000" in output
        assert "max-keep-alive-queue 100" in output
        assert "max-session-srv-conns 8" in output
        assert "http-reuse aggressive" in output
        assert "http-send-name-header X-API-Server" in output
        assert "retries 3" in output
        assert "retry-on conn-failure,empty-response,junk-response,response-timeout,500,502,503,504" in output
        assert "timeout connect 3s" in output
        assert "timeout server 10s" in output
        assert "timeout check 2s" in output

    def test_microservices_with_tracing_and_retry(self):
        """Test microservices architecture with distributed tracing and retry."""
        config = """
        config microservices {
            frontend gateway {
                bind *:8080
                mode: http

                // Request tracing
                unique-id-format: "%[uuid()]"
                unique-id-header: "X-Trace-ID"

                default_backend: auth_service
            }

            backend auth_service {
                mode: http
                balance: roundrobin

                description: "Authentication microservice"

                // Send server info for debugging
                http-send-name-header: "X-Auth-Server"

                // Retry on failures
                retry-on: "conn-failure,empty-response,500,503"
                retries: 2

                // Connection pooling
                http-reuse: safe
                max-session-srv-conns: 5

                servers {
                    server auth1 {
                        address: "10.0.1.1"
                        port: 9001
                        check: true
                    }
                    server auth2 {
                        address: "10.0.1.2"
                        port: 9001
                        check: true
                    }
                }
            }

            backend user_service {
                mode: http
                balance: leastconn

                description: "User management microservice"

                // Send server info for debugging
                http-send-name-header: "X-User-Server"

                // More aggressive retry for critical service
                retry-on: "all-retryable-errors"
                retries: 3

                // Connection pooling
                http-reuse: safe
                max-session-srv-conns: 8

                servers {
                    server user1 {
                        address: "10.0.2.1"
                        port: 9002
                        check: true
                    }
                    server user2 {
                        address: "10.0.2.2"
                        port: 9002
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

        # Verify frontend IR
        frontend = ir.frontends[0]
        assert frontend.unique_id_format == "%[uuid()]"
        assert frontend.unique_id_header == "X-Trace-ID"

        # Verify auth_service backend IR
        auth_backend = ir.backends[0]
        assert auth_backend.description == "Authentication microservice"
        assert auth_backend.http_send_name_header == "X-Auth-Server"
        assert auth_backend.retry_on == "conn-failure,empty-response,500,503"
        assert auth_backend.retries == 2
        assert auth_backend.http_reuse == "safe"
        assert auth_backend.max_session_srv_conns == 5

        # Verify user_service backend IR
        user_backend = ir.backends[1]
        assert user_backend.description == "User management microservice"
        assert user_backend.http_send_name_header == "X-User-Server"
        assert user_backend.retry_on == "all-retryable-errors"
        assert user_backend.retries == 3
        assert user_backend.http_reuse == "safe"
        assert user_backend.max_session_srv_conns == 8

        # Verify output
        assert "frontend gateway" in output
        assert "unique-id-format %[uuid()]" in output
        assert "unique-id-header X-Trace-ID" in output

        assert "backend auth_service" in output
        assert "http-send-name-header X-Auth-Server" in output
        assert "retry-on conn-failure,empty-response,500,503" in output
        assert "retries 2" in output

        assert "backend user_service" in output
        assert "http-send-name-header X-User-Server" in output
        assert "retry-on all-retryable-errors" in output
        assert "retries 3" in output

    def test_api_gateway_with_observability(self):
        """Test API gateway configuration with full observability."""
        config = """
        config api_gateway {
            backend external_api {
                mode: http
                balance: roundrobin

                description: "External API proxy with full observability"

                // Server identification in headers
                http-send-name-header: "X-Proxy-Server"

                // Resilient retry strategy
                retry-on: "conn-failure,empty-response,junk-response,response-timeout,0rtt-rejected,500,502,503,504"
                retries: 4

                // Logging
                log: "127.0.0.1:514 local0"
                log-tag: "external-api"

                // Timeouts
                timeout_connect: 5s
                timeout_server: 30s

                servers {
                    server api1 {
                        address: "api1.example.com"
                        port: 443
                        check: true
                        ssl: true
                        sni: "str(api1.example.com)"
                    }
                    server api2 {
                        address: "api2.example.com"
                        port: 443
                        check: true
                        ssl: true
                        sni: "str(api2.example.com)"
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
        backend = ir.backends[0]
        assert backend.description == "External API proxy with full observability"
        assert backend.http_send_name_header == "X-Proxy-Server"
        assert backend.retry_on == "conn-failure,empty-response,junk-response,response-timeout,0rtt-rejected,500,502,503,504"
        assert backend.retries == 4
        assert len(backend.log) == 1
        assert backend.log_tag == "external-api"
        assert backend.timeout_connect == "5s"
        assert backend.timeout_server == "30s"

        # Verify output
        assert "backend external_api" in output
        assert "description External API proxy with full observability" in output
        assert "http-send-name-header X-Proxy-Server" in output
        assert "retry-on conn-failure,empty-response,junk-response,response-timeout,0rtt-rejected,500,502,503,504" in output
        assert "retries 4" in output
        assert "log 127.0.0.1:514 local0" in output
        assert "log-tag external-api" in output
