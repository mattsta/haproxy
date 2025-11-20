"""Tests for Phase 10 batch 1 - Threading & Process directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase10Threading:
    """Test Phase 10 threading and process directives."""

    def test_nbthread(self):
        """Test nbthread directive - number of worker threads."""
        config = """
        config test {
            global {
                nbthread: 4
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 4

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 4" in output

    def test_nbthread_single(self):
        """Test nbthread with single thread."""
        config = """
        config test {
            global {
                nbthread: 1
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 1" in output

    def test_nbthread_max(self):
        """Test nbthread with maximum value."""
        config = """
        config test {
            global {
                nbthread: 64
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 64

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 64" in output

    def test_thread_groups(self):
        """Test thread-groups directive - number of thread groups."""
        config = """
        config test {
            global {
                thread-groups: 2
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.thread_groups == 2

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "thread-groups 2" in output

    def test_thread_groups_single(self):
        """Test thread-groups with single group."""
        config = """
        config test {
            global {
                thread-groups: 1
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.thread_groups == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "thread-groups 1" in output

    def test_thread_groups_max(self):
        """Test thread-groups with maximum value (16)."""
        config = """
        config test {
            global {
                thread-groups: 16
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.thread_groups == 16

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "thread-groups 16" in output

    def test_numa_cpu_mapping_on(self):
        """Test numa-cpu-mapping directive set to true."""
        config = """
        config test {
            global {
                numa-cpu-mapping: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.numa_cpu_mapping is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "numa-cpu-mapping on" in output

    def test_numa_cpu_mapping_off(self):
        """Test numa-cpu-mapping directive set to false."""
        config = """
        config test {
            global {
                numa-cpu-mapping: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.numa_cpu_mapping is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "numa-cpu-mapping off" in output

    def test_nbthread_and_thread_groups(self):
        """Test nbthread and thread-groups together."""
        config = """
        config test {
            global {
                nbthread: 8
                thread-groups: 2
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 8
        assert ir.global_config.thread_groups == 2

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 8" in output
        assert "thread-groups 2" in output

    def test_all_threading_directives(self):
        """Test all Phase 10 threading directives together."""
        config = """
        config test {
            global {
                nbthread: 16
                thread-groups: 4
                numa-cpu-mapping: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 16
        assert ir.global_config.thread_groups == 4
        assert ir.global_config.numa_cpu_mapping is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 16" in output
        assert "thread-groups 4" in output
        assert "numa-cpu-mapping on" in output

    def test_threading_with_nbproc(self):
        """Test threading directives with nbproc for compatibility."""
        config = """
        config test {
            global {
                nbproc: 2
                nbthread: 4
                thread-groups: 1
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbproc == 2
        assert ir.global_config.nbthread == 4
        assert ir.global_config.thread_groups == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbproc 2" in output
        assert "nbthread 4" in output
        assert "thread-groups 1" in output

    def test_threading_with_performance_tuning(self):
        """Test threading directives with performance tuning directives."""
        config = """
        config test {
            global {
                nbthread: 8
                numa-cpu-mapping: true
                tune.maxaccept: 64
                tune.runqueue-depth: 200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 8
        assert ir.global_config.numa_cpu_mapping is True
        assert ir.global_config.tuning.get("tune.maxaccept") == 64
        assert ir.global_config.tuning.get("tune.runqueue-depth") == 200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 8" in output
        assert "numa-cpu-mapping on" in output
        assert "tune.maxaccept 64" in output
        assert "tune.runqueue-depth 200" in output

    def test_threading_in_complete_config(self):
        """Test threading directives in a complete configuration."""
        config = """
        config test {
            global {
                daemon: true
                maxconn: 10000
                nbthread: 4
                thread-groups: 2
                numa-cpu-mapping: true
                user: "haproxy"
            }

            defaults {
                mode: http
            }

            frontend web {
                mode: http
            }

            backend servers {
                mode: http
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 10000
        assert ir.global_config.nbthread == 4
        assert ir.global_config.thread_groups == 2
        assert ir.global_config.numa_cpu_mapping is True
        assert ir.global_config.user == "haproxy"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "daemon" in output
        assert "maxconn 10000" in output
        assert "nbthread 4" in output
        assert "thread-groups 2" in output
        assert "numa-cpu-mapping on" in output
        assert "user haproxy" in output
        assert "frontend web" in output
        assert "backend servers" in output
