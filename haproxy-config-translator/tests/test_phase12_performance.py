"""
Test Phase 12 Batch 6: Performance Tuning Directives

This test module covers 13 performance tuning directives for platform-specific
options, profiling controls, and advanced zero-copy forwarding optimizations.

Coverage:
- no-memory-trimming: Disable automatic memory trimming
- noevports: Disable evports polling mechanism
- noktls: Disable kernel TLS offload
- profiling.memory: Memory profiling (on/off)
- profiling.tasks: Task profiling (on/off)
- tune.epoll.mask-events: Epoll event masking threshold
- tune.fail-alloc: Memory allocation failure testing
- tune.h1.zero-copy-fwd-recv: HTTP/1 zero-copy receive
- tune.h1.zero-copy-fwd-send: HTTP/1 zero-copy send
- tune.pt.zero-copy-forwarding: Pass-through zero-copy
- tune.renice.runtime: Runtime process priority
- tune.renice.startup: Startup process priority
- tune.takeover-other-tg-connections: Thread group connection takeover
"""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase12Performance:
    """Test cases for Phase 12 Batch 6: Performance tuning directives."""

    def test_no_memory_trimming_enabled(self):
        """Test no-memory-trimming directive enabled."""
        config = """
        config test {
            global {
                no-memory-trimming: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.no_memory_trimming is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "no-memory-trimming" in output

    def test_no_memory_trimming_disabled(self):
        """Test no-memory-trimming directive disabled."""
        config = """
        config test {
            global {
                no-memory-trimming: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.no_memory_trimming is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "no-memory-trimming" not in output

    def test_noevports_enabled(self):
        """Test noevports directive to disable evports polling."""
        config = """
        config test {
            global {
                noevports: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.noevports is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "noevports" in output

    def test_noktls_enabled(self):
        """Test noktls directive to disable kernel TLS."""
        config = """
        config test {
            global {
                noktls: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.noktls is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "noktls" in output

    def test_profiling_memory_on(self):
        """Test profiling.memory directive enabled."""
        config = """
        config test {
            global {
                profiling.memory: "on"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.profiling_memory == "on"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "profiling.memory on" in output

    def test_profiling_memory_off(self):
        """Test profiling.memory directive disabled."""
        config = """
        config test {
            global {
                profiling.memory: "off"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.profiling_memory == "off"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "profiling.memory off" in output

    def test_profiling_tasks_on(self):
        """Test profiling.tasks directive enabled."""
        config = """
        config test {
            global {
                profiling.tasks: "on"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.profiling_tasks == "on"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "profiling.tasks on" in output

    def test_profiling_tasks_off(self):
        """Test profiling.tasks directive disabled."""
        config = """
        config test {
            global {
                profiling.tasks: "off"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.profiling_tasks == "off"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "profiling.tasks off" in output

    def test_tune_epoll_mask_events(self):
        """Test tune.epoll.mask-events directive."""
        config = """
        config test {
            global {
                tune.epoll.mask-events: 1000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.epoll.mask-events") == 1000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.epoll.mask-events 1000" in output

    def test_tune_fail_alloc(self):
        """Test tune.fail-alloc for memory allocation failure testing."""
        config = """
        config test {
            global {
                tune.fail-alloc: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.fail-alloc") == 100

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.fail-alloc 100" in output

    def test_tune_h1_zero_copy_fwd_recv(self):
        """Test tune.h1.zero-copy-fwd-recv directive."""
        config = """
        config test {
            global {
                tune.h1.zero-copy-fwd-recv: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-recv") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h1.zero-copy-fwd-recv on" in output

    def test_tune_h1_zero_copy_fwd_send(self):
        """Test tune.h1.zero-copy-fwd-send directive."""
        config = """
        config test {
            global {
                tune.h1.zero-copy-fwd-send: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-send") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h1.zero-copy-fwd-send on" in output

    def test_tune_pt_zero_copy_forwarding(self):
        """Test tune.pt.zero-copy-forwarding directive."""
        config = """
        config test {
            global {
                tune.pt.zero-copy-forwarding: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.pt.zero-copy-forwarding") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.pt.zero-copy-forwarding on" in output

    def test_tune_renice_runtime(self):
        """Test tune.renice.runtime for runtime priority adjustment."""
        config = """
        config test {
            global {
                tune.renice.runtime: 10
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.renice.runtime") == 10

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.renice.runtime 10" in output

    def test_tune_renice_startup(self):
        """Test tune.renice.startup for startup priority adjustment."""
        config = """
        config test {
            global {
                tune.renice.startup: -5
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.renice.startup") == -5

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.renice.startup -5" in output

    def test_tune_takeover_other_tg_connections(self):
        """Test tune.takeover-other-tg-connections directive."""
        config = """
        config test {
            global {
                tune.takeover-other-tg-connections: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.takeover-other-tg-connections") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.takeover-other-tg-connections on" in output

    def test_zero_copy_combined(self):
        """Test all zero-copy directives together."""
        config = """
        config test {
            global {
                tune.h1.zero-copy-fwd-recv: true
                tune.h1.zero-copy-fwd-send: true
                tune.pt.zero-copy-forwarding: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-recv") is True
        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-send") is True
        assert ir.global_config.tuning.get("tune.pt.zero-copy-forwarding") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.h1.zero-copy-fwd-recv on" in output
        assert "tune.h1.zero-copy-fwd-send on" in output
        assert "tune.pt.zero-copy-forwarding on" in output

    def test_platform_specific_combined(self):
        """Test all platform-specific options together."""
        config = """
        config test {
            global {
                noepoll: true
                nokqueue: true
                noevports: true
                noktls: true
                no-memory-trimming: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.noepoll is True
        assert ir.global_config.nokqueue is True
        assert ir.global_config.noevports is True
        assert ir.global_config.noktls is True
        assert ir.global_config.no_memory_trimming is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "noepoll" in output
        assert "nokqueue" in output
        assert "noevports" in output
        assert "noktls" in output
        assert "no-memory-trimming" in output

    def test_profiling_combined(self):
        """Test all profiling directives together."""
        config = """
        config test {
            global {
                profiling.tasks: "on"
                profiling.memory: "on"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.profiling_tasks == "on"
        assert ir.global_config.profiling_memory == "on"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "profiling.tasks on" in output
        assert "profiling.memory on" in output

    def test_tune_directives_combined(self):
        """Test all tune.* performance directives together."""
        config = """
        config test {
            global {
                tune.epoll.mask-events: 500
                tune.fail-alloc: 50
                tune.renice.runtime: 5
                tune.renice.startup: -10
                tune.takeover-other-tg-connections: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.epoll.mask-events") == 500
        assert ir.global_config.tuning.get("tune.fail-alloc") == 50
        assert ir.global_config.tuning.get("tune.renice.runtime") == 5
        assert ir.global_config.tuning.get("tune.renice.startup") == -10
        assert ir.global_config.tuning.get("tune.takeover-other-tg-connections") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.epoll.mask-events 500" in output
        assert "tune.fail-alloc 50" in output
        assert "tune.renice.runtime 5" in output
        assert "tune.renice.startup -10" in output
        assert "tune.takeover-other-tg-connections on" in output

    def test_high_performance_config(self):
        """Test high-performance configuration with all optimizations."""
        config = """
        config high_perf {
            global {
                daemon: true
                maxconn: 500000
                nbthread: 32
                no-memory-trimming: true
                noktls: false
                tune.h1.zero-copy-fwd-recv: true
                tune.h1.zero-copy-fwd-send: true
                tune.pt.zero-copy-forwarding: true
                tune.takeover-other-tg-connections: true
                tune.renice.runtime: 0
                tune.renice.startup: -20
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 500000
        assert ir.global_config.nbthread == 32
        assert ir.global_config.no_memory_trimming is True
        assert ir.global_config.noktls is False
        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-recv") is True
        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-send") is True
        assert ir.global_config.tuning.get("tune.pt.zero-copy-forwarding") is True
        assert ir.global_config.tuning.get("tune.takeover-other-tg-connections") is True
        assert ir.global_config.tuning.get("tune.renice.runtime") == 0
        assert ir.global_config.tuning.get("tune.renice.startup") == -20

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 500000" in output
        assert "nbthread 32" in output
        assert "no-memory-trimming" in output
        assert "tune.h1.zero-copy-fwd-recv on" in output
        assert "tune.h1.zero-copy-fwd-send on" in output
        assert "tune.pt.zero-copy-forwarding on" in output
        assert "tune.takeover-other-tg-connections on" in output
        assert "tune.renice.runtime 0" in output
        assert "tune.renice.startup -20" in output

    def test_debugging_config(self):
        """Test debugging configuration with profiling enabled."""
        config = """
        config debugging {
            global {
                profiling.tasks: "on"
                profiling.memory: "on"
                tune.fail-alloc: 1000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.profiling_tasks == "on"
        assert ir.global_config.profiling_memory == "on"
        assert ir.global_config.tuning.get("tune.fail-alloc") == 1000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "profiling.tasks on" in output
        assert "profiling.memory on" in output
        assert "tune.fail-alloc 1000" in output

    def test_production_optimizations(self):
        """Test production-grade performance optimizations."""
        config = """
        config production {
            global {
                daemon: true
                maxconn: 1000000
                nbthread: 64
                thread-groups: 4
                no-memory-trimming: true
                tune.h1.zero-copy-fwd-recv: true
                tune.h1.zero-copy-fwd-send: true
                tune.pt.zero-copy-forwarding: true
                tune.takeover-other-tg-connections: true
                tune.epoll.mask-events: 2000
                tune.renice.runtime: -5
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 1000000
        assert ir.global_config.nbthread == 64
        assert ir.global_config.thread_groups == 4
        assert ir.global_config.no_memory_trimming is True
        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-recv") is True
        assert ir.global_config.tuning.get("tune.h1.zero-copy-fwd-send") is True
        assert ir.global_config.tuning.get("tune.pt.zero-copy-forwarding") is True
        assert ir.global_config.tuning.get("tune.takeover-other-tg-connections") is True
        assert ir.global_config.tuning.get("tune.epoll.mask-events") == 2000
        assert ir.global_config.tuning.get("tune.renice.runtime") == -5

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 1000000" in output
        assert "nbthread 64" in output
        assert "thread-groups 4" in output
        assert "no-memory-trimming" in output
        assert "tune.h1.zero-copy-fwd-recv on" in output
        assert "tune.h1.zero-copy-fwd-send on" in output
        assert "tune.pt.zero-copy-forwarding on" in output
        assert "tune.takeover-other-tg-connections on" in output
        assert "tune.epoll.mask-events 2000" in output
        assert "tune.renice.runtime -5" in output
