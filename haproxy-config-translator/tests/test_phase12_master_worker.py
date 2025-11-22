"""
Test Phase 12 Batch 2: Master-Worker Mode Global Directives

This test module covers master-worker process management directives for graceful
reloads, multi-process configurations, and seamless upgrades.

Coverage:
- master-worker: Enable master-worker mode for seamless reloads
- mworker-max-reloads: Maximum number of reload attempts
- nbproc: Number of worker processes (deprecated in favor of nbthread)
"""


from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase12MasterWorker:
    """Test cases for Phase 12 Batch 2: Master-Worker mode directives."""

    def test_master_worker_basic(self):
        """Test master-worker mode enablement."""
        config = """
        config test {
            global {
                master-worker: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.master_worker is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "master-worker" in output

    def test_master_worker_disabled(self):
        """Test master-worker mode disabled (default behavior)."""
        config = """
        config test {
            global {
                master-worker: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.master_worker is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        # When false, master-worker should not appear in output
        assert "master-worker" not in output

    def test_master_worker_with_daemon(self):
        """Test master-worker mode with daemon mode."""
        config = """
        config test {
            global {
                daemon: true
                master-worker: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.daemon is True
        assert ir.global_config.master_worker is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "daemon" in output
        assert "master-worker" in output

    def test_mworker_max_reloads_basic(self):
        """Test mworker-max-reloads directive."""
        config = """
        config test {
            global {
                master-worker: true
                mworker-max-reloads: 3
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.master_worker is True
        assert ir.global_config.mworker_max_reloads == 3

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "master-worker" in output
        assert "mworker-max-reloads 3" in output

    def test_mworker_max_reloads_production(self):
        """Test mworker-max-reloads with production-safe value."""
        config = """
        config test {
            global {
                master-worker: true
                mworker-max-reloads: 10
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.mworker_max_reloads == 10

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "mworker-max-reloads 10" in output

    def test_mworker_max_reloads_unlimited(self):
        """Test mworker-max-reloads with high value for unlimited reloads."""
        config = """
        config test {
            global {
                master-worker: true
                mworker-max-reloads: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.mworker_max_reloads == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "mworker-max-reloads 50" in output

    def test_nbproc_basic(self):
        """Test nbproc directive for multi-process mode."""
        config = """
        config test {
            global {
                nbproc: 4
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbproc == 4

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbproc 4" in output

    def test_nbproc_single_process(self):
        """Test nbproc with single process (default)."""
        config = """
        config test {
            global {
                nbproc: 1
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbproc == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbproc 1" in output

    def test_nbproc_multi_core(self):
        """Test nbproc matching number of CPU cores."""
        config = """
        config test {
            global {
                nbproc: 8
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbproc == 8

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbproc 8" in output

    def test_master_worker_complete_config(self):
        """Test complete master-worker configuration."""
        config = """
        config test {
            global {
                daemon: true
                master-worker: true
                mworker-max-reloads: 5
                maxconn: 50000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.daemon is True
        assert ir.global_config.master_worker is True
        assert ir.global_config.mworker_max_reloads == 5
        assert ir.global_config.maxconn == 50000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "daemon" in output
        assert "master-worker" in output
        assert "mworker-max-reloads 5" in output
        assert "maxconn 50000" in output

    def test_production_master_worker_setup(self):
        """Test production-grade master-worker configuration."""
        config = """
        config production {
            global {
                daemon: true
                master-worker: true
                mworker-max-reloads: 10
                maxconn: 100000
                nbthread: 16
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify master-worker settings
        assert ir.global_config.daemon is True
        assert ir.global_config.master_worker is True
        assert ir.global_config.mworker_max_reloads == 10

        # Verify performance settings
        assert ir.global_config.maxconn == 100000
        assert ir.global_config.nbthread == 16

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "master-worker" in output
        assert "mworker-max-reloads 10" in output
        assert "maxconn 100000" in output
        assert "nbthread 16" in output

    def test_zero_downtime_reload_config(self):
        """Test configuration optimized for zero-downtime reloads."""
        config = """
        config zero_downtime {
            global {
                daemon: true
                master-worker: true
                mworker-max-reloads: 50
                hard-stop-after: "30s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify master-worker for seamless reloads
        assert ir.global_config.master_worker is True
        assert ir.global_config.mworker_max_reloads == 50

        # Verify hard-stop-after for graceful shutdown
        assert ir.global_config.hard_stop_after == "30s"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "master-worker" in output
        assert "mworker-max-reloads 50" in output
        assert "hard-stop-after 30s" in output
