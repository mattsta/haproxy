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

    def test_tune_disable_fast_forward(self):
        """Test tune.disable-fast-forward directive."""
        config = """
        config test {
            global {
                tune.disable-fast-forward: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.disable-fast-forward") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.disable-fast-forward on" in output

    def test_tune_disable_zero_copy_forwarding(self):
        """Test tune.disable-zero-copy-forwarding directive."""
        config = """
        config test {
            global {
                tune.disable-zero-copy-forwarding: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.disable-zero-copy-forwarding") is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.disable-zero-copy-forwarding off" in output

    def test_tune_events_max_events_at_once(self):
        """Test tune.events.max-events-at-once directive."""
        config = """
        config test {
            global {
                tune.events.max-events-at-once: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.events.max-events-at-once") == 100

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.events.max-events-at-once 100" in output

    def test_tune_memory_hot_size(self):
        """Test tune.memory.hot-size directive."""
        config = """
        config test {
            global {
                tune.memory.hot-size: 524288
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.memory.hot-size") == 524288

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.memory.hot-size 524288" in output

    def test_tune_peers_max_updates_at_once(self):
        """Test tune.peers.max-updates-at-once directive."""
        config = """
        config test {
            global {
                tune.peers.max-updates-at-once: 200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.peers.max-updates-at-once") == 200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.peers.max-updates-at-once 200" in output

    def test_tune_ring_queues(self):
        """Test tune.ring.queues directive."""
        config = """
        config test {
            global {
                tune.ring.queues: 16
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ring.queues") == 16

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ring.queues 16" in output

    def test_tune_applet_zero_copy_forwarding(self):
        """Test tune.applet.zero-copy-forwarding directive."""
        config = """
        config test {
            global {
                tune.applet.zero-copy-forwarding: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.applet.zero-copy-forwarding") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.applet.zero-copy-forwarding on" in output

    def test_tune_buffers_limit(self):
        """Test tune.buffers.limit directive."""
        config = """
        config test {
            global {
                tune.buffers.limit: 1000000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.buffers.limit") == 1000000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.buffers.limit 1000000" in output

    def test_tune_buffers_reserve(self):
        """Test tune.buffers.reserve directive."""
        config = """
        config test {
            global {
                tune.buffers.reserve: 64
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.buffers.reserve") == 64

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.buffers.reserve 64" in output

    def test_tune_comp_maxlevel(self):
        """Test tune.comp.maxlevel directive."""
        config = """
        config test {
            global {
                tune.comp.maxlevel: 9
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.comp.maxlevel") == 9

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.comp.maxlevel 9" in output

    def test_tune_http_cookielen(self):
        """Test tune.http.cookielen directive."""
        config = """
        config test {
            global {
                tune.http.cookielen: 4096
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.http.cookielen") == 4096

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.http.cookielen 4096" in output

    def test_tune_http_logurilen(self):
        """Test tune.http.logurilen directive."""
        config = """
        config test {
            global {
                tune.http.logurilen: 2048
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.http.logurilen") == 2048

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.http.logurilen 2048" in output

    def test_tune_http_maxhdr(self):
        """Test tune.http.maxhdr directive."""
        config = """
        config test {
            global {
                tune.http.maxhdr: 200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.http.maxhdr") == 200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.http.maxhdr 200" in output

    def test_tune_ssl_cachesize(self):
        """Test tune.ssl.cachesize directive."""
        config = """
        config test {
            global {
                tune.ssl.cachesize: 20000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.cachesize") == 20000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.cachesize 20000" in output
