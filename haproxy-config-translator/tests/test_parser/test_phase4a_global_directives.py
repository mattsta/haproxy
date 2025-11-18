"""Tests for Phase 4A global directives - Performance, Lua, Variables, Pools, Buffers."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase4AGlobalDirectives:
    """Test cases for Phase 4A global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_performance_runtime(self, parser, codegen):
        """Test performance and runtime directives."""
        source = """
        config test {
            global {
                daemon: true
                busy-polling: true
                max-spread-checks: 5000
                spread-checks: 30
                maxcompcpuusage: 80
                maxcomprate: 1000000
                default-path: "/usr/local/bin:/usr/bin"
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

        assert ir.global_config.busy_polling is True
        assert ir.global_config.max_spread_checks == 5000
        assert ir.global_config.spread_checks == 30
        assert ir.global_config.maxcompcpuusage == 80
        assert ir.global_config.maxcomprate == 1000000
        assert ir.global_config.default_path == "/usr/local/bin:/usr/bin"

        assert "busy-polling" in output
        assert "max-spread-checks 5000" in output
        assert "spread-checks 30" in output
        assert "maxcompcpuusage 80" in output
        assert "maxcomprate 1000000" in output
        assert "default-path /usr/local/bin:/usr/bin" in output

    def test_global_tune_performance(self, parser, codegen):
        """Test tune.* performance directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.idle-pool.shared: "on"
                tune.pattern.cache-size: 100000
                tune.stick-counters: 12
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

        assert ir.global_config.tuning.get("tune.idle-pool.shared") == "on"
        assert ir.global_config.tuning.get("tune.pattern.cache-size") == 100000
        assert ir.global_config.tuning.get("tune.stick-counters") == 12

        assert "tune.idle-pool.shared on" in output
        assert "tune.pattern.cache-size 100000" in output
        assert "tune.stick-counters 12" in output

    def test_global_lua_configuration(self, parser, codegen):
        """Test Lua configuration directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.lua.forced-yield: 10000
                tune.lua.maxmem: 1073741824
                tune.lua.session-timeout: "4s"
                tune.lua.task-timeout: "4s"
                tune.lua.service-timeout: "4s"
                tune.lua.log.loggers: "on"
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

        assert ir.global_config.tuning.get("tune.lua.forced-yield") == 10000
        assert ir.global_config.tuning.get("tune.lua.maxmem") == 1073741824
        assert ir.global_config.tuning.get("tune.lua.session-timeout") == "4s"
        assert ir.global_config.tuning.get("tune.lua.task-timeout") == "4s"
        assert ir.global_config.tuning.get("tune.lua.service-timeout") == "4s"
        assert ir.global_config.tuning.get("tune.lua.log.loggers") == "on"

        assert "tune.lua.forced-yield 10000" in output
        assert "tune.lua.maxmem 1073741824" in output
        assert "tune.lua.session-timeout 4s" in output
        assert "tune.lua.task-timeout 4s" in output
        assert "tune.lua.service-timeout 4s" in output
        assert "tune.lua.log.loggers on" in output

    def test_global_variables_configuration(self, parser, codegen):
        """Test variables configuration directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.vars.global-max-size: 1048576
                tune.vars.proc-max-size: 262144
                tune.vars.reqres-max-size: 65536
                tune.vars.sess-max-size: 32768
                tune.vars.txn-max-size: 16384
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

        assert ir.global_config.tuning.get("tune.vars.global-max-size") == 1048576
        assert ir.global_config.tuning.get("tune.vars.proc-max-size") == 262144
        assert ir.global_config.tuning.get("tune.vars.reqres-max-size") == 65536
        assert ir.global_config.tuning.get("tune.vars.sess-max-size") == 32768
        assert ir.global_config.tuning.get("tune.vars.txn-max-size") == 16384

        assert "tune.vars.global-max-size 1048576" in output
        assert "tune.vars.proc-max-size 262144" in output
        assert "tune.vars.reqres-max-size 65536" in output
        assert "tune.vars.sess-max-size 32768" in output
        assert "tune.vars.txn-max-size 16384" in output

    def test_global_connection_pool(self, parser, codegen):
        """Test connection pool directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.pool.high-fd-ratio: 75
                tune.pool.low-fd-ratio: 25
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

        assert ir.global_config.tuning.get("tune.pool.high-fd-ratio") == 75
        assert ir.global_config.tuning.get("tune.pool.low-fd-ratio") == 25

        assert "tune.pool.high-fd-ratio 75" in output
        assert "tune.pool.low-fd-ratio 25" in output

    def test_global_socket_buffers(self, parser, codegen):
        """Test socket buffer directives."""
        source = """
        config test {
            global {
                daemon: true
                tune.rcvbuf.client: 131072
                tune.rcvbuf.server: 131072
                tune.sndbuf.client: 131072
                tune.sndbuf.server: 131072
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

        assert ir.global_config.tuning.get("tune.rcvbuf.client") == 131072
        assert ir.global_config.tuning.get("tune.rcvbuf.server") == 131072
        assert ir.global_config.tuning.get("tune.sndbuf.client") == 131072
        assert ir.global_config.tuning.get("tune.sndbuf.server") == 131072

        assert "tune.rcvbuf.client 131072" in output
        assert "tune.rcvbuf.server 131072" in output
        assert "tune.sndbuf.client 131072" in output
        assert "tune.sndbuf.server 131072" in output

    def test_global_phase4a_comprehensive(self, parser, codegen):
        """Test all Phase 4A directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000

                // Performance & Runtime
                busy-polling: true
                max-spread-checks: 5000
                spread-checks: 30
                maxcompcpuusage: 80
                maxcomprate: 1000000
                default-path: "/usr/local/bin:/usr/bin"
                tune.idle-pool.shared: "on"
                tune.pattern.cache-size: 100000
                tune.stick-counters: 12

                // Lua Configuration
                tune.lua.forced-yield: 10000
                tune.lua.maxmem: 1073741824
                tune.lua.session-timeout: "4s"
                tune.lua.task-timeout: "4s"
                tune.lua.service-timeout: "4s"
                tune.lua.log.loggers: "on"

                // Variables Configuration
                tune.vars.global-max-size: 1048576
                tune.vars.proc-max-size: 262144
                tune.vars.reqres-max-size: 65536
                tune.vars.sess-max-size: 32768
                tune.vars.txn-max-size: 16384

                // Connection Pool
                tune.pool.high-fd-ratio: 75
                tune.pool.low-fd-ratio: 25

                // Socket Buffers
                tune.rcvbuf.client: 131072
                tune.rcvbuf.server: 131072
                tune.sndbuf.client: 131072
                tune.sndbuf.server: 131072
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
        assert "busy-polling" in output
        assert "max-spread-checks 5000" in output
        assert "spread-checks 30" in output
        assert "maxcompcpuusage 80" in output
        assert "maxcomprate 1000000" in output
        assert "default-path /usr/local/bin:/usr/bin" in output
        assert "tune.idle-pool.shared on" in output
        assert "tune.pattern.cache-size 100000" in output
        assert "tune.stick-counters 12" in output
        assert "tune.lua.forced-yield 10000" in output
        assert "tune.lua.maxmem 1073741824" in output
        assert "tune.lua.session-timeout 4s" in output
        assert "tune.lua.task-timeout 4s" in output
        assert "tune.lua.service-timeout 4s" in output
        assert "tune.lua.log.loggers on" in output
        assert "tune.vars.global-max-size 1048576" in output
        assert "tune.vars.proc-max-size 262144" in output
        assert "tune.vars.reqres-max-size 65536" in output
        assert "tune.vars.sess-max-size 32768" in output
        assert "tune.vars.txn-max-size 16384" in output
        assert "tune.pool.high-fd-ratio 75" in output
        assert "tune.pool.low-fd-ratio 25" in output
        assert "tune.rcvbuf.client 131072" in output
        assert "tune.rcvbuf.server 131072" in output
        assert "tune.sndbuf.client 131072" in output
        assert "tune.sndbuf.server 131072" in output
