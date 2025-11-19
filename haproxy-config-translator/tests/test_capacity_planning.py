"""Tests for capacity planning directives: backlog, fullconn, maxconn (Phases 4E, 4F, 4G)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestFrontendBacklog:
    """Test backlog directive in frontend."""

    def test_frontend_backlog(self):
        """Test frontend with backlog."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                backlog: 2048

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

        assert ir.frontends[0].backlog == 2048
        assert "backlog 2048" in output


class TestFrontendFullconn:
    """Test fullconn directive in frontend."""

    def test_frontend_fullconn(self):
        """Test frontend with fullconn."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                maxconn: 10000
                fullconn: 8000

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

        assert ir.frontends[0].maxconn == 10000
        assert ir.frontends[0].fullconn == 8000
        assert "maxconn 10000" in output
        assert "fullconn 8000" in output

    def test_frontend_fullconn_only(self):
        """Test frontend with only fullconn (without maxconn)."""
        config = """
        config test {
            frontend api {
                bind *:443
                mode: http
                fullconn: 5000

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

        assert ir.frontends[0].fullconn == 5000
        assert "fullconn 5000" in output


class TestBackendMaxconn:
    """Test maxconn directive in backend."""

    def test_backend_maxconn(self):
        """Test backend with maxconn."""
        config = """
        config test {
            backend app {
                maxconn: 5000

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

        assert ir.backends[0].maxconn == 5000
        assert "maxconn 5000" in output


class TestBackendBacklog:
    """Test backlog directive in backend."""

    def test_backend_backlog(self):
        """Test backend with backlog."""
        config = """
        config test {
            backend app {
                backlog: 1024

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

        assert ir.backends[0].backlog == 1024
        assert "backlog 1024" in output


class TestCapacityPlanningIntegration:
    """Test capacity planning directives together."""

    def test_frontend_all_capacity_directives(self):
        """Test frontend with all capacity directives."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                maxconn: 20000
                backlog: 4096
                fullconn: 15000

                default_backend: web_backend
            }

            backend web_backend {
                servers {
                    server web1 {
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
        assert frontend.maxconn == 20000
        assert frontend.backlog == 4096
        assert frontend.fullconn == 15000

        # Verify output
        assert "maxconn 20000" in output
        assert "backlog 4096" in output
        assert "fullconn 15000" in output

    def test_backend_all_capacity_directives(self):
        """Test backend with all capacity directives."""
        config = """
        config production {
            backend api {
                mode: http
                balance: leastconn

                maxconn: 10000
                backlog: 2048

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
        assert backend.maxconn == 10000
        assert backend.backlog == 2048

        # Verify output
        assert "maxconn 10000" in output
        assert "backlog 2048" in output

    def test_complete_capacity_planning_config(self):
        """Test complete production config with capacity planning."""
        config = """
        config production {
            frontend web_frontend {
                bind *:80
                bind *:443
                mode: http

                // Capacity planning
                maxconn: 50000
                backlog: 8192
                fullconn: 40000

                // Timeouts
                timeout_client: 30s
                timeout_http_request: 10s

                default_backend: app_backend
            }

            backend app_backend {
                mode: http
                balance: roundrobin

                // Capacity planning
                maxconn: 30000
                backlog: 4096

                // Connection pooling
                http-reuse: safe

                // Timeouts
                timeout_connect: 5s
                timeout_server: 30s

                servers {
                    server app1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                        maxconn: 500
                    }
                    server app2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                        maxconn: 500
                    }
                    server app3 {
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

        # Verify frontend IR
        frontend = ir.frontends[0]
        assert frontend.maxconn == 50000
        assert frontend.backlog == 8192
        assert frontend.fullconn == 40000

        # Verify backend IR
        backend = ir.backends[0]
        assert backend.maxconn == 30000
        assert backend.backlog == 4096

        # Verify output
        assert "frontend web_frontend" in output
        assert "maxconn 50000" in output
        assert "backlog 8192" in output
        assert "fullconn 40000" in output

        assert "backend app_backend" in output
        assert "maxconn 30000" in output
        assert "backlog 4096" in output

    def test_high_traffic_scenario(self):
        """Test high-traffic configuration with aggressive capacity settings."""
        config = """
        config high_traffic {
            frontend lb {
                bind *:80
                mode: http

                // High-traffic capacity settings
                maxconn: 100000
                backlog: 16384
                fullconn: 80000

                // Monitoring
                monitor_uri: "/health"
                stats {
                    enable: true
                    uri: "/stats"
                }

                default_backend: web_pool
            }

            backend web_pool {
                mode: http
                balance: leastconn

                // High backend capacity
                maxconn: 75000
                backlog: 8192

                // Aggressive connection reuse
                http-reuse: aggressive

                // Load balancing tuning
                hash-type: consistent djb2
                hash-balance-factor: 150

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                        maxconn: 2000
                    }
                    server web2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                        maxconn: 2000
                    }
                    server web3 {
                        address: "10.0.1.3"
                        port: 8080
                        check: true
                        maxconn: 2000
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
        assert frontend.maxconn == 100000
        assert frontend.backlog == 16384
        assert frontend.fullconn == 80000
        assert frontend.monitor_uri == "/health"
        assert frontend.stats_config is not None

        # Verify backend
        backend = ir.backends[0]
        assert backend.maxconn == 75000
        assert backend.backlog == 8192
        assert backend.http_reuse == "aggressive"
        assert backend.hash_type == "consistent djb2"
        assert backend.hash_balance_factor == 150

        # Verify complete output
        assert "maxconn 100000" in output
        assert "backlog 16384" in output
        assert "fullconn 80000" in output
        assert "monitor-uri /health" in output
        assert "stats enable" in output
        assert "maxconn 75000" in output
        assert "backlog 8192" in output
        assert "http-reuse aggressive" in output
        assert "hash-type consistent djb2" in output
        assert "hash-balance-factor 150" in output
