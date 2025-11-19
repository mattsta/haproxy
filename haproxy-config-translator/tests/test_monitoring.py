"""Tests for advanced monitoring features (Phase 4B)."""

import pytest
from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestMonitorNet:
    """Test monitor-net directive for network-based monitoring."""

    def test_monitor_net_single(self):
        """Test single monitor-net directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor_uri: "/health"
                monitor-net "10.0.0.0/8"

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

        assert len(ir.frontends[0].monitor_net) == 1
        assert ir.frontends[0].monitor_net[0] == "10.0.0.0/8"
        assert "monitor-net 10.0.0.0/8" in output

    def test_monitor_net_multiple(self):
        """Test multiple monitor-net directives."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor_uri: "/health"
                monitor-net "10.0.0.0/8"
                monitor-net "192.168.1.0/24"
                monitor-net "172.16.0.0/12"

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

        assert len(ir.frontends[0].monitor_net) == 3
        assert "10.0.0.0/8" in ir.frontends[0].monitor_net
        assert "192.168.1.0/24" in ir.frontends[0].monitor_net
        assert "172.16.0.0/12" in ir.frontends[0].monitor_net

        assert "monitor-net 10.0.0.0/8" in output
        assert "monitor-net 192.168.1.0/24" in output
        assert "monitor-net 172.16.0.0/12" in output

    def test_monitor_net_ipv4_address(self):
        """Test monitor-net with single IPv4 address."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor-net "10.0.1.100"

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

        assert ir.frontends[0].monitor_net[0] == "10.0.1.100"
        assert "monitor-net 10.0.1.100" in output


class TestMonitorFail:
    """Test monitor fail directive for conditional monitoring failures."""

    def test_monitor_fail_basic(self):
        """Test basic monitor fail with ACL condition."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor_uri: "/health"

                acl {
                    is_maintenance path "/maintenance"
                }

                monitor fail if is_maintenance

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

        assert len(ir.frontends[0].monitor_fail_rules) == 1
        assert "if is_maintenance" in ir.frontends[0].monitor_fail_rules[0].condition
        assert "monitor fail if is_maintenance" in output

    def test_monitor_fail_multiple_conditions(self):
        """Test multiple monitor fail directives."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                monitor_uri: "/health"

                acl {
                    backend_down path "/down"
                    too_many_errors path "/error"
                }

                monitor fail if backend_down
                monitor fail if too_many_errors

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

        assert len(ir.frontends[0].monitor_fail_rules) == 2
        assert "monitor fail if backend_down" in output
        assert "monitor fail if too_many_errors" in output


class TestMonitoringIntegration:
    """Test monitor-net and monitor fail together."""

    def test_complete_monitoring_setup(self):
        """Test complete monitoring configuration."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                // Define monitoring endpoint
                monitor_uri: "/health"

                // Allow monitoring from specific networks
                monitor-net "10.0.0.0/8"
                monitor-net "192.168.1.0/24"

                // Define health check conditions
                acl {
                    backend_dead path "/dead"
                    too_many_connections path_beg "/overload"
                    error_rate path_beg "/error"
                }

                // Fail health checks under certain conditions
                monitor fail if backend_dead
                monitor fail if too_many_connections
                monitor fail if error_rate

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server srv2 {
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
        frontend = ir.frontends[0]
        assert frontend.monitor_uri == "/health"
        assert len(frontend.monitor_net) == 2
        assert "10.0.0.0/8" in frontend.monitor_net
        assert "192.168.1.0/24" in frontend.monitor_net
        assert len(frontend.monitor_fail_rules) == 3

        # Verify output
        assert "monitor-uri /health" in output
        assert "monitor-net 10.0.0.0/8" in output
        assert "monitor-net 192.168.1.0/24" in output
        assert "monitor fail if backend_dead" in output
        assert "monitor fail if too_many_connections" in output
        assert "monitor fail if error_rate" in output

    def test_monitoring_with_load_balancing(self):
        """Test monitoring combined with load balancing features."""
        config = """
        config production {
            frontend api {
                bind *:443
                mode: http

                monitor_uri: "/healthz"
                monitor-net "10.0.0.0/8"

                acl {
                    service_degraded path "/degraded"
                }

                monitor fail if service_degraded

                default_backend: api_backend
            }

            backend api_backend {
                mode: http
                balance: uri
                hash-type: consistent djb2
                hash-balance-factor: 150

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
                    server api3 {
                        address: "10.0.1.3"
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

        # Verify frontend monitoring
        frontend = ir.frontends[0]
        assert frontend.monitor_uri == "/healthz"
        assert len(frontend.monitor_net) == 1
        assert len(frontend.monitor_fail_rules) == 1

        # Verify backend load balancing
        backend = ir.backends[0]
        assert backend.hash_type == "consistent djb2"
        assert backend.hash_balance_factor == 150

        # Verify complete output
        assert "monitor-uri /healthz" in output
        assert "monitor-net 10.0.0.0/8" in output
        assert "monitor fail if service_degraded" in output
        assert "hash-type consistent djb2" in output
        assert "hash-balance-factor 150" in output
