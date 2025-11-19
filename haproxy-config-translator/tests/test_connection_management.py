"""Tests for connection management directives: max-keep-alive-queue and max-session-srv-conns (Phases 4M, 4N)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestFrontendMaxKeepAliveQueue:
    """Test max-keep-alive-queue directive in frontend."""

    def test_frontend_max_keep_alive_queue(self):
        """Test frontend with max-keep-alive-queue."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                max-keep-alive-queue: 100

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

        assert ir.frontends[0].max_keep_alive_queue == 100
        assert "max-keep-alive-queue 100" in output

    def test_frontend_max_keep_alive_queue_large_value(self):
        """Test frontend with large max-keep-alive-queue."""
        config = """
        config test {
            frontend api {
                bind *:443
                mode: http
                max-keep-alive-queue: 1000

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

        assert ir.frontends[0].max_keep_alive_queue == 1000
        assert "max-keep-alive-queue 1000" in output


class TestBackendMaxKeepAliveQueue:
    """Test max-keep-alive-queue directive in backend."""

    def test_backend_max_keep_alive_queue(self):
        """Test backend with max-keep-alive-queue."""
        config = """
        config test {
            backend app {
                mode: http
                max-keep-alive-queue: 50

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

        assert ir.backends[0].max_keep_alive_queue == 50
        assert "max-keep-alive-queue 50" in output

    def test_backend_max_keep_alive_queue_with_http_reuse(self):
        """Test backend with max-keep-alive-queue and http-reuse."""
        config = """
        config test {
            backend api {
                mode: http
                balance: leastconn

                http-reuse: safe
                max-keep-alive-queue: 200

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
        backend = ir.backends[0]
        assert backend.max_keep_alive_queue == 200
        assert backend.http_reuse == "safe"

        # Verify output
        assert "max-keep-alive-queue 200" in output
        assert "http-reuse safe" in output


class TestBackendMaxSessionSrvConns:
    """Test max-session-srv-conns directive in backend."""

    def test_backend_max_session_srv_conns(self):
        """Test backend with max-session-srv-conns."""
        config = """
        config test {
            backend app {
                mode: http
                max-session-srv-conns: 5

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

        assert ir.backends[0].max_session_srv_conns == 5
        assert "max-session-srv-conns 5" in output

    def test_backend_max_session_srv_conns_higher_limit(self):
        """Test backend with higher max-session-srv-conns limit."""
        config = """
        config test {
            backend database {
                mode: tcp
                balance: leastconn
                max-session-srv-conns: 10

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

        assert ir.backends[0].max_session_srv_conns == 10
        assert "max-session-srv-conns 10" in output


class TestConnectionManagementIntegration:
    """Test connection management directives together."""

    def test_frontend_and_backend_max_keep_alive_queue(self):
        """Test max-keep-alive-queue in both frontend and backend."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                maxconn: 10000
                max-keep-alive-queue: 100

                default_backend: app_backend
            }

            backend app_backend {
                mode: http
                balance: roundrobin

                maxconn: 5000
                max-keep-alive-queue: 50

                servers {
                    server app1 {
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

        # Verify frontend IR
        frontend = ir.frontends[0]
        assert frontend.maxconn == 10000
        assert frontend.max_keep_alive_queue == 100

        # Verify backend IR
        backend = ir.backends[0]
        assert backend.maxconn == 5000
        assert backend.max_keep_alive_queue == 50

        # Verify output
        assert "frontend web" in output
        assert "maxconn 10000" in output
        assert "max-keep-alive-queue 100" in output

        assert "backend app_backend" in output
        assert "maxconn 5000" in output
        assert "max-keep-alive-queue 50" in output

    def test_backend_all_connection_directives(self):
        """Test backend with all connection management directives."""
        config = """
        config production {
            backend api {
                mode: http
                balance: leastconn

                // Capacity planning
                maxconn: 8000
                backlog: 2048

                // Connection management
                max-keep-alive-queue: 150
                max-session-srv-conns: 8

                // Connection reuse
                http-reuse: safe

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
        assert backend.maxconn == 8000
        assert backend.backlog == 2048
        assert backend.max_keep_alive_queue == 150
        assert backend.max_session_srv_conns == 8
        assert backend.http_reuse == "safe"

        # Verify output
        assert "maxconn 8000" in output
        assert "backlog 2048" in output
        assert "max-keep-alive-queue 150" in output
        assert "max-session-srv-conns 8" in output
        assert "http-reuse safe" in output

    def test_complete_high_performance_config(self):
        """Test complete high-performance configuration with all capacity directives."""
        config = """
        config high_performance {
            frontend lb {
                bind *:80
                bind *:443
                mode: http

                description: "High-performance load balancer frontend"
                id: 100

                // Capacity planning
                maxconn: 50000
                backlog: 8192
                fullconn: 40000

                // Connection management
                max-keep-alive-queue: 500

                // Timeouts
                timeout_client: 30s
                timeout_http_request: 10s
                timeout_http_keep_alive: 5s

                // Monitoring
                monitor_uri: "/health"

                default_backend: high_perf_backend
            }

            backend high_perf_backend {
                mode: http
                balance: leastconn

                description: "High-performance backend pool"
                id: 200

                // Capacity planning
                maxconn: 30000
                backlog: 4096

                // Connection management
                max-keep-alive-queue: 300
                max-session-srv-conns: 10

                // Connection reuse
                http-reuse: aggressive

                // Timeouts
                timeout_connect: 5s
                timeout_server: 30s

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                        maxconn: 1000
                    }
                    server web2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                        maxconn: 1000
                    }
                    server web3 {
                        address: "10.0.1.3"
                        port: 8080
                        check: true
                        maxconn: 1000
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
        assert frontend.description == "High-performance load balancer frontend"
        assert frontend.id == 100
        assert frontend.maxconn == 50000
        assert frontend.backlog == 8192
        assert frontend.fullconn == 40000
        assert frontend.max_keep_alive_queue == 500
        assert frontend.timeout_client == "30s"
        assert frontend.timeout_http_request == "10s"
        assert frontend.timeout_http_keep_alive == "5s"
        assert frontend.monitor_uri == "/health"

        # Verify backend IR
        backend = ir.backends[0]
        assert backend.description == "High-performance backend pool"
        assert backend.id == 200
        assert backend.maxconn == 30000
        assert backend.backlog == 4096
        assert backend.max_keep_alive_queue == 300
        assert backend.max_session_srv_conns == 10
        assert backend.http_reuse == "aggressive"
        assert backend.timeout_connect == "5s"
        assert backend.timeout_server == "30s"

        # Verify complete output
        assert "frontend lb" in output
        assert "description High-performance load balancer frontend" in output
        assert "id 100" in output
        assert "maxconn 50000" in output
        assert "backlog 8192" in output
        assert "fullconn 40000" in output
        assert "max-keep-alive-queue 500" in output
        assert "timeout client 30s" in output
        assert "timeout http-request 10s" in output
        assert "timeout http-keep-alive 5s" in output
        assert "monitor-uri /health" in output

        assert "backend high_perf_backend" in output
        assert "description High-performance backend pool" in output
        assert "id 200" in output
        assert "maxconn 30000" in output
        assert "backlog 4096" in output
        assert "max-keep-alive-queue 300" in output
        assert "max-session-srv-conns 10" in output
        assert "http-reuse aggressive" in output
        assert "timeout connect 5s" in output
        assert "timeout server 30s" in output

    def test_microservices_connection_limits(self):
        """Test connection management for microservices architecture."""
        config = """
        config microservices {
            backend auth_service {
                mode: http
                balance: roundrobin

                description: "Authentication service backend"

                // Limit connections per session
                max-session-srv-conns: 3
                max-keep-alive-queue: 50

                // Connection pooling
                http-reuse: safe

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

                description: "User service backend"

                // Higher limits for user service
                max-session-srv-conns: 5
                max-keep-alive-queue: 100

                // Connection pooling
                http-reuse: safe

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

        # Verify auth_service IR
        auth_backend = ir.backends[0]
        assert auth_backend.description == "Authentication service backend"
        assert auth_backend.max_session_srv_conns == 3
        assert auth_backend.max_keep_alive_queue == 50
        assert auth_backend.http_reuse == "safe"

        # Verify user_service IR
        user_backend = ir.backends[1]
        assert user_backend.description == "User service backend"
        assert user_backend.max_session_srv_conns == 5
        assert user_backend.max_keep_alive_queue == 100
        assert user_backend.http_reuse == "safe"

        # Verify output
        assert "backend auth_service" in output
        assert "max-session-srv-conns 3" in output
        assert "max-keep-alive-queue 50" in output

        assert "backend user_service" in output
        assert "max-session-srv-conns 5" in output
        assert "max-keep-alive-queue 100" in output
