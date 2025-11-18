"""Tests for Phase 3 global directives - Memory, CPU, and System Integration."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase3GlobalDirectives:
    """Test cases for Phase 3 global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_system_integration(self, parser, codegen):
        """Test system integration directives: uid, gid, node, description."""
        source = """
        config test {
            global {
                daemon: true
                uid: 99
                gid: 99
                node: "lb-node-01"
                description: "Production Load Balancer"
                hard-stop-after: "30s"
                external-check: true
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.uid == 99
        assert ir.global_config.gid == 99
        assert ir.global_config.node == "lb-node-01"
        assert ir.global_config.description == "Production Load Balancer"
        assert ir.global_config.hard_stop_after == "30s"
        assert ir.global_config.external_check is True

        assert "uid 99" in output
        assert "gid 99" in output
        assert "node lb-node-01" in output
        assert "description Production Load Balancer" in output
        assert "hard-stop-after 30s" in output
        assert "external-check" in output

    def test_global_memory_tuning(self, parser, codegen):
        """Test memory tuning directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.memory.pool-allocator: "dlmalloc"
                tune.memory.fail-alloc: "on"
                tune.buffers.limit: 1073741824
                tune.buffers.reserve: 134217728
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.tuning.get("tune.memory.pool-allocator") == "dlmalloc"
        assert ir.global_config.tuning.get("tune.memory.fail-alloc") == "on"
        assert ir.global_config.tuning.get("tune.buffers.limit") == 1073741824
        assert ir.global_config.tuning.get("tune.buffers.reserve") == 134217728

        assert "tune.memory.pool-allocator dlmalloc" in output
        assert "tune.memory.fail-alloc on" in output
        assert "tune.buffers.limit 1073741824" in output
        assert "tune.buffers.reserve 134217728" in output

    def test_global_cpu_performance(self, parser, codegen):
        """Test CPU and performance tuning directives."""
        source = """
        config test {
            global {
                daemon: true
                cpu-map "1" "0-3"
                cpu-map "2" "4-7"
                tune.fd.edge-triggered: true
                tune.comp.maxlevel: 9
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.cpu_map.get("1") == "0-3"
        assert ir.global_config.cpu_map.get("2") == "4-7"
        assert ir.global_config.tuning.get("tune.fd.edge-triggered") is True
        assert ir.global_config.tuning.get("tune.comp.maxlevel") == 9

        assert "cpu-map 1 0-3" in output
        assert "cpu-map 2 4-7" in output
        assert "tune.comp.maxlevel 9" in output
        assert "tune.fd.edge-triggered" in output

    def test_global_system_security(self, parser, codegen):
        """Test system security directives."""
        source = """
        config test {
            global {
                daemon: true
                setcap: "cap_net_bind_service=+ep"
                set-dumpable: true
                unix-bind: "mode 600"
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.setcap == "cap_net_bind_service=+ep"
        assert ir.global_config.set_dumpable is True
        assert ir.global_config.unix_bind == "mode 600"

        assert "setcap cap_net_bind_service=+ep" in output
        assert "set-dumpable" in output
        assert "unix-bind mode 600" in output

    def test_global_phase3_comprehensive(self, parser, codegen):
        """Test all Phase 3 directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000

                // System integration
                uid: 1001
                gid: 1001
                node: "lb-production-01"
                description: "High-Performance Load Balancer"
                hard-stop-after: "60s"
                external-check: true

                // Memory tuning
                tune.memory.pool-allocator: "je"
                tune.buffers.limit: 2147483648
                tune.buffers.reserve: 268435456

                // CPU performance
                cpu-map "auto:1/1-4" "0-3"
                cpu-map "auto:5-8" "4-7"
                tune.fd.edge-triggered: true
                tune.comp.maxlevel: 6

                // System security
                setcap: "cap_net_bind_service,cap_net_raw=+ep"
                set-dumpable: true
                unix-bind: "mode 660 user haproxy group haproxy"
            }

            frontend https {
                bind *:443
                default_backend: web
            }

            backend web {
                servers {
                    server web1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify all directives in output
        assert "uid 1001" in output
        assert "gid 1001" in output
        assert "node lb-production-01" in output
        assert "description High-Performance Load Balancer" in output
        assert "hard-stop-after 60s" in output
        assert "external-check" in output
        assert "tune.memory.pool-allocator je" in output
        assert "tune.buffers.limit 2147483648" in output
        assert "cpu-map auto:1/1-4 0-3" in output
        assert "cpu-map auto:5-8 4-7" in output
        assert "tune.fd.edge-triggered" in output
        assert "tune.comp.maxlevel 6" in output
        assert "setcap cap_net_bind_service,cap_net_raw=+ep" in output
        assert "set-dumpable" in output
        assert "unix-bind mode 660 user haproxy group haproxy" in output
