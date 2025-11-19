"""Tests for Phase 6 performance tuning directives (tune.*)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase6PerformanceTuning:
    """Test Phase 6 performance tuning directives."""

    def test_tune_maxaccept(self):
        """Test tune.maxaccept directive."""
        config = """
        config test {
            global {
                tune.maxaccept: 64
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.maxaccept") == 64

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.maxaccept 64" in output

    def test_tune_maxpollevents(self):
        """Test tune.maxpollevents directive."""
        config = """
        config test {
            global {
                tune.maxpollevents: 200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.maxpollevents") == 200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.maxpollevents 200" in output

    def test_tune_bufsize_small(self):
        """Test tune.bufsize.small directive."""
        config = """
        config test {
            global {
                tune.bufsize.small: 8192
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.bufsize.small") == 8192

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.bufsize.small 8192" in output

    def test_tune_rcvbuf_frontend(self):
        """Test tune.rcvbuf.frontend directive."""
        config = """
        config test {
            global {
                tune.rcvbuf.frontend: 32768
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.rcvbuf.frontend") == 32768

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.rcvbuf.frontend 32768" in output

    def test_tune_rcvbuf_backend(self):
        """Test tune.rcvbuf.backend directive."""
        config = """
        config test {
            global {
                tune.rcvbuf.backend: 65536
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.rcvbuf.backend") == 65536

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.rcvbuf.backend 65536" in output

    def test_tune_sndbuf_frontend(self):
        """Test tune.sndbuf.frontend directive."""
        config = """
        config test {
            global {
                tune.sndbuf.frontend: 32768
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.sndbuf.frontend") == 32768

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.sndbuf.frontend 32768" in output

    def test_tune_sndbuf_backend(self):
        """Test tune.sndbuf.backend directive."""
        config = """
        config test {
            global {
                tune.sndbuf.backend: 65536
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.sndbuf.backend") == 65536

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.sndbuf.backend 65536" in output

    def test_multiple_tune_directives(self):
        """Test multiple tune.* directives together."""
        config = """
        config test {
            global {
                tune.maxaccept: 64
                tune.maxpollevents: 200
                tune.bufsize.small: 8192
                tune.rcvbuf.frontend: 32768
                tune.rcvbuf.backend: 65536
                tune.sndbuf.frontend: 32768
                tune.sndbuf.backend: 65536
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all are stored in tuning dict
        assert ir.global_config.tuning.get("tune.maxaccept") == 64
        assert ir.global_config.tuning.get("tune.maxpollevents") == 200
        assert ir.global_config.tuning.get("tune.bufsize.small") == 8192
        assert ir.global_config.tuning.get("tune.rcvbuf.frontend") == 32768
        assert ir.global_config.tuning.get("tune.rcvbuf.backend") == 65536
        assert ir.global_config.tuning.get("tune.sndbuf.frontend") == 32768
        assert ir.global_config.tuning.get("tune.sndbuf.backend") == 65536

        # Verify codegen
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.maxaccept 64" in output
        assert "tune.maxpollevents 200" in output
        assert "tune.bufsize.small 8192" in output
        assert "tune.rcvbuf.frontend 32768" in output
        assert "tune.rcvbuf.backend 65536" in output
        assert "tune.sndbuf.frontend 32768" in output
        assert "tune.sndbuf.backend 65536" in output

    def test_tune_pipesize(self):
        """Test tune.pipesize directive."""
        config = """
        config test {
            global {
                tune.pipesize: 32768
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.pipesize") == 32768

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.pipesize 32768" in output

    def test_tune_recv_enough(self):
        """Test tune.recv_enough directive."""
        config = """
        config test {
            global {
                tune.recv_enough: 10000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.recv-enough") == 10000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.recv-enough 10000" in output

    def test_tune_idletimer(self):
        """Test tune.idletimer directive."""
        config = """
        config test {
            global {
                tune.idletimer: "1s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.idletimer") == "1s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.idletimer 1s" in output

    def test_tune_runqueue_depth(self):
        """Test tune.runqueue-depth directive."""
        config = """
        config test {
            global {
                tune.runqueue-depth: 200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        # Note: tune_runqueue_depth → tune.runqueue-depth
        assert ir.global_config.tuning.get("tune.runqueue-depth") == 200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.runqueue-depth 200" in output

    def test_tune_sched_low_latency(self):
        """Test tune.sched.low-latency directive."""
        config = """
        config test {
            global {
                tune.sched.low-latency: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.sched.low-latency") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.sched.low-latency on" in output

    def test_tune_max_checks_per_thread(self):
        """Test tune.max-checks-per-thread directive."""
        config = """
        config test {
            global {
                tune.max-checks-per-thread: 256
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        # Note: tune_max_checks_per_thread → tune.max-checks-per-thread
        assert ir.global_config.tuning.get("tune.max-checks-per-thread") == 256

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.max-checks-per-thread 256" in output

    def test_tune_max_rules_at_once(self):
        """Test tune.max-rules-at-once directive."""
        config = """
        config test {
            global {
                tune.max-rules-at-once: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        # Note: tune_max_rules_at_once → tune.max-rules-at-once
        assert ir.global_config.tuning.get("tune.max-rules-at-once") == 100

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.max-rules-at-once 100" in output
