"""
Test Phase 13 Batch 2: Modern QUIC Directives

This test module covers modern QUIC backend/frontend specific directives
for congestion control, security, streams, and transmission.

Coverage:
- 12 Backend directives: tune.quic.be.*
- 14 Frontend directives: tune.quic.fe.*
- 2 Global directives: tune.quic.listen, tune.quic.mem.tx-max
"""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase13QUIC:
    """Test cases for Phase 13 Batch 2: Modern QUIC directives."""

    # Backend Congestion Control Tests
    def test_quic_be_cc_cubic_min_losses(self):
        """Test tune.quic.be.cc.cubic-min-losses."""
        config = """
        config test {
            global {
                tune.quic.be.cc.cubic-min-losses: 3
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.be.cc.cubic-min-losses") == 3

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.be.cc.cubic-min-losses 3" in output

    def test_quic_be_cc_hystart(self):
        """Test tune.quic.be.cc.hystart."""
        config = """
        config test {
            global {
                tune.quic.be.cc.hystart: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.be.cc.hystart") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.be.cc.hystart on" in output

    def test_quic_be_cc_combined(self):
        """Test multiple backend congestion control settings."""
        config = """
        config test {
            global {
                tune.quic.be.cc.cubic-min-losses: 3
                tune.quic.be.cc.hystart: true
                tune.quic.be.cc.max-frame-loss: 5
                tune.quic.be.cc.max-win-size: 1048576
                tune.quic.be.cc.reorder-ratio: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.be.cc.cubic-min-losses") == 3
        assert ir.global_config.tuning.get("tune.quic.be.cc.hystart") is True
        assert ir.global_config.tuning.get("tune.quic.be.cc.max-frame-loss") == 5
        assert ir.global_config.tuning.get("tune.quic.be.cc.max-win-size") == 1048576
        assert ir.global_config.tuning.get("tune.quic.be.cc.reorder-ratio") == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.be.cc.cubic-min-losses 3" in output
        assert "tune.quic.be.cc.hystart on" in output
        assert "tune.quic.be.cc.max-frame-loss 5" in output
        assert "tune.quic.be.cc.max-win-size 1048576" in output
        assert "tune.quic.be.cc.reorder-ratio 50" in output

    # Backend Stream Tests
    def test_quic_be_stream_settings(self):
        """Test backend stream configuration."""
        config = """
        config test {
            global {
                tune.quic.be.stream.data-ratio: 75
                tune.quic.be.stream.max-concurrent: 100
                tune.quic.be.stream.rxbuf: 65536
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.be.stream.data-ratio") == 75
        assert ir.global_config.tuning.get("tune.quic.be.stream.max-concurrent") == 100
        assert ir.global_config.tuning.get("tune.quic.be.stream.rxbuf") == 65536

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.be.stream.data-ratio 75" in output
        assert "tune.quic.be.stream.max-concurrent 100" in output
        assert "tune.quic.be.stream.rxbuf 65536" in output

    # Backend TX Tests
    def test_quic_be_tx_settings(self):
        """Test backend TX configuration."""
        config = """
        config test {
            global {
                tune.quic.be.tx.pacing: true
                tune.quic.be.tx.udp-gso: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.be.tx.pacing") is True
        assert ir.global_config.tuning.get("tune.quic.be.tx.udp-gso") is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.be.tx.pacing on" in output
        assert "tune.quic.be.tx.udp-gso off" in output

    # Backend Security and Timeout Tests
    def test_quic_be_security_timeout(self):
        """Test backend security and timeout settings."""
        config = """
        config test {
            global {
                tune.quic.be.sec.glitches-threshold: 10
                tune.quic.be.max-idle-timeout: "30s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.be.sec.glitches-threshold") == 10
        assert ir.global_config.tuning.get("tune.quic.be.max-idle-timeout") == "30s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.be.sec.glitches-threshold 10" in output
        assert "tune.quic.be.max-idle-timeout 30s" in output

    # Frontend Congestion Control Tests
    def test_quic_fe_cc_settings(self):
        """Test frontend congestion control configuration."""
        config = """
        config test {
            global {
                tune.quic.fe.cc.cubic-min-losses: 3
                tune.quic.fe.cc.hystart: true
                tune.quic.fe.cc.max-frame-loss: 5
                tune.quic.fe.cc.max-win-size: 2097152
                tune.quic.fe.cc.reorder-ratio: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.fe.cc.cubic-min-losses") == 3
        assert ir.global_config.tuning.get("tune.quic.fe.cc.hystart") is True
        assert ir.global_config.tuning.get("tune.quic.fe.cc.max-frame-loss") == 5
        assert ir.global_config.tuning.get("tune.quic.fe.cc.max-win-size") == 2097152
        assert ir.global_config.tuning.get("tune.quic.fe.cc.reorder-ratio") == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.fe.cc.cubic-min-losses 3" in output
        assert "tune.quic.fe.cc.hystart on" in output
        assert "tune.quic.fe.cc.max-frame-loss 5" in output
        assert "tune.quic.fe.cc.max-win-size 2097152" in output
        assert "tune.quic.fe.cc.reorder-ratio 50" in output

    # Frontend Stream Tests
    def test_quic_fe_stream_settings(self):
        """Test frontend stream configuration."""
        config = """
        config test {
            global {
                tune.quic.fe.stream.data-ratio: 80
                tune.quic.fe.stream.max-concurrent: 200
                tune.quic.fe.stream.rxbuf: 131072
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.fe.stream.data-ratio") == 80
        assert ir.global_config.tuning.get("tune.quic.fe.stream.max-concurrent") == 200
        assert ir.global_config.tuning.get("tune.quic.fe.stream.rxbuf") == 131072

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.fe.stream.data-ratio 80" in output
        assert "tune.quic.fe.stream.max-concurrent 200" in output
        assert "tune.quic.fe.stream.rxbuf 131072" in output

    # Frontend TX Tests
    def test_quic_fe_tx_settings(self):
        """Test frontend TX configuration."""
        config = """
        config test {
            global {
                tune.quic.fe.tx.pacing: true
                tune.quic.fe.tx.udp-gso: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.fe.tx.pacing") is True
        assert ir.global_config.tuning.get("tune.quic.fe.tx.udp-gso") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.fe.tx.pacing on" in output
        assert "tune.quic.fe.tx.udp-gso on" in output

    # Frontend Security Tests
    def test_quic_fe_security_settings(self):
        """Test frontend security configuration."""
        config = """
        config test {
            global {
                tune.quic.fe.sec.glitches-threshold: 10
                tune.quic.fe.sec.retry-threshold: 3
                tune.quic.fe.sock-per-conn: "default-on"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.fe.sec.glitches-threshold") == 10
        assert ir.global_config.tuning.get("tune.quic.fe.sec.retry-threshold") == 3
        assert ir.global_config.tuning.get("tune.quic.fe.sock-per-conn") == "default-on"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.fe.sec.glitches-threshold 10" in output
        assert "tune.quic.fe.sec.retry-threshold 3" in output
        assert "tune.quic.fe.sock-per-conn default-on" in output

    # Frontend Timeout Test
    def test_quic_fe_max_idle_timeout(self):
        """Test frontend max idle timeout."""
        config = """
        config test {
            global {
                tune.quic.fe.max-idle-timeout: "60s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.fe.max-idle-timeout") == "60s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.fe.max-idle-timeout 60s" in output

    # Global QUIC Tests
    def test_quic_global_settings(self):
        """Test global QUIC configuration."""
        config = """
        config test {
            global {
                tune.quic.listen: true
                tune.quic.mem.tx-max: 1048576
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.quic.listen") is True
        assert ir.global_config.tuning.get("tune.quic.mem.tx-max") == 1048576

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.listen on" in output
        assert "tune.quic.mem.tx-max 1048576" in output

    # Comprehensive Production Tests
    def test_quic_backend_production_config(self):
        """Test comprehensive backend QUIC production configuration."""
        config = """
        config quic_backend {
            global {
                tune.quic.be.cc.cubic-min-losses: 3
                tune.quic.be.cc.hystart: true
                tune.quic.be.cc.max-frame-loss: 5
                tune.quic.be.cc.max-win-size: 1048576
                tune.quic.be.cc.reorder-ratio: 50
                tune.quic.be.max-idle-timeout: "30s"
                tune.quic.be.sec.glitches-threshold: 10
                tune.quic.be.stream.data-ratio: 75
                tune.quic.be.stream.max-concurrent: 100
                tune.quic.be.stream.rxbuf: 65536
                tune.quic.be.tx.pacing: true
                tune.quic.be.tx.udp-gso: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all backend settings
        assert ir.global_config.tuning.get("tune.quic.be.cc.cubic-min-losses") == 3
        assert ir.global_config.tuning.get("tune.quic.be.cc.hystart") is True
        assert ir.global_config.tuning.get("tune.quic.be.cc.max-frame-loss") == 5
        assert ir.global_config.tuning.get("tune.quic.be.cc.max-win-size") == 1048576
        assert ir.global_config.tuning.get("tune.quic.be.cc.reorder-ratio") == 50
        assert ir.global_config.tuning.get("tune.quic.be.max-idle-timeout") == "30s"
        assert ir.global_config.tuning.get("tune.quic.be.sec.glitches-threshold") == 10
        assert ir.global_config.tuning.get("tune.quic.be.stream.data-ratio") == 75
        assert ir.global_config.tuning.get("tune.quic.be.stream.max-concurrent") == 100
        assert ir.global_config.tuning.get("tune.quic.be.stream.rxbuf") == 65536
        assert ir.global_config.tuning.get("tune.quic.be.tx.pacing") is True
        assert ir.global_config.tuning.get("tune.quic.be.tx.udp-gso") is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.be.cc.cubic-min-losses 3" in output
        assert "tune.quic.be.cc.hystart on" in output
        assert "tune.quic.be.cc.max-frame-loss 5" in output
        assert "tune.quic.be.cc.max-win-size 1048576" in output
        assert "tune.quic.be.cc.reorder-ratio 50" in output
        assert "tune.quic.be.max-idle-timeout 30s" in output
        assert "tune.quic.be.sec.glitches-threshold 10" in output
        assert "tune.quic.be.stream.data-ratio 75" in output
        assert "tune.quic.be.stream.max-concurrent 100" in output
        assert "tune.quic.be.stream.rxbuf 65536" in output
        assert "tune.quic.be.tx.pacing on" in output
        assert "tune.quic.be.tx.udp-gso off" in output

    def test_quic_frontend_production_config(self):
        """Test comprehensive frontend QUIC production configuration."""
        config = """
        config quic_frontend {
            global {
                tune.quic.fe.cc.cubic-min-losses: 3
                tune.quic.fe.cc.hystart: true
                tune.quic.fe.cc.max-frame-loss: 5
                tune.quic.fe.cc.max-win-size: 2097152
                tune.quic.fe.cc.reorder-ratio: 50
                tune.quic.fe.max-idle-timeout: "60s"
                tune.quic.fe.sec.glitches-threshold: 10
                tune.quic.fe.sec.retry-threshold: 3
                tune.quic.fe.sock-per-conn: "default-on"
                tune.quic.fe.stream.data-ratio: 80
                tune.quic.fe.stream.max-concurrent: 200
                tune.quic.fe.stream.rxbuf: 131072
                tune.quic.fe.tx.pacing: true
                tune.quic.fe.tx.udp-gso: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all frontend settings
        assert ir.global_config.tuning.get("tune.quic.fe.cc.cubic-min-losses") == 3
        assert ir.global_config.tuning.get("tune.quic.fe.cc.hystart") is True
        assert ir.global_config.tuning.get("tune.quic.fe.cc.max-frame-loss") == 5
        assert ir.global_config.tuning.get("tune.quic.fe.cc.max-win-size") == 2097152
        assert ir.global_config.tuning.get("tune.quic.fe.cc.reorder-ratio") == 50
        assert ir.global_config.tuning.get("tune.quic.fe.max-idle-timeout") == "60s"
        assert ir.global_config.tuning.get("tune.quic.fe.sec.glitches-threshold") == 10
        assert ir.global_config.tuning.get("tune.quic.fe.sec.retry-threshold") == 3
        assert ir.global_config.tuning.get("tune.quic.fe.sock-per-conn") == "default-on"
        assert ir.global_config.tuning.get("tune.quic.fe.stream.data-ratio") == 80
        assert ir.global_config.tuning.get("tune.quic.fe.stream.max-concurrent") == 200
        assert ir.global_config.tuning.get("tune.quic.fe.stream.rxbuf") == 131072
        assert ir.global_config.tuning.get("tune.quic.fe.tx.pacing") is True
        assert ir.global_config.tuning.get("tune.quic.fe.tx.udp-gso") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.quic.fe.cc.cubic-min-losses 3" in output
        assert "tune.quic.fe.cc.hystart on" in output
        assert "tune.quic.fe.cc.max-frame-loss 5" in output
        assert "tune.quic.fe.cc.max-win-size 2097152" in output
        assert "tune.quic.fe.cc.reorder-ratio 50" in output
        assert "tune.quic.fe.max-idle-timeout 60s" in output
        assert "tune.quic.fe.sec.glitches-threshold 10" in output
        assert "tune.quic.fe.sec.retry-threshold 3" in output
        assert "tune.quic.fe.sock-per-conn default-on" in output
        assert "tune.quic.fe.stream.data-ratio 80" in output
        assert "tune.quic.fe.stream.max-concurrent 200" in output
        assert "tune.quic.fe.stream.rxbuf 131072" in output
        assert "tune.quic.fe.tx.pacing on" in output
        assert "tune.quic.fe.tx.udp-gso on" in output

    def test_quic_complete_production_config(self):
        """Test complete QUIC production configuration with all settings."""
        config = """
        config quic_production {
            global {
                daemon: true
                maxconn: 50000
                tune.quic.listen: true
                tune.quic.mem.tx-max: 1048576
                tune.quic.fe.cc.hystart: true
                tune.quic.fe.stream.max-concurrent: 200
                tune.quic.fe.tx.pacing: true
                tune.quic.fe.tx.udp-gso: true
                tune.quic.be.cc.hystart: true
                tune.quic.be.stream.max-concurrent: 100
                tune.quic.be.tx.pacing: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.tuning.get("tune.quic.listen") is True
        assert ir.global_config.tuning.get("tune.quic.mem.tx-max") == 1048576
        assert ir.global_config.tuning.get("tune.quic.fe.cc.hystart") is True
        assert ir.global_config.tuning.get("tune.quic.fe.stream.max-concurrent") == 200
        assert ir.global_config.tuning.get("tune.quic.fe.tx.pacing") is True
        assert ir.global_config.tuning.get("tune.quic.fe.tx.udp-gso") is True
        assert ir.global_config.tuning.get("tune.quic.be.cc.hystart") is True
        assert ir.global_config.tuning.get("tune.quic.be.stream.max-concurrent") == 100
        assert ir.global_config.tuning.get("tune.quic.be.tx.pacing") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 50000" in output
        assert "tune.quic.listen on" in output
        assert "tune.quic.mem.tx-max 1048576" in output
        assert "tune.quic.fe.cc.hystart on" in output
        assert "tune.quic.fe.stream.max-concurrent 200" in output
        assert "tune.quic.fe.tx.pacing on" in output
        assert "tune.quic.fe.tx.udp-gso on" in output
        assert "tune.quic.be.cc.hystart on" in output
        assert "tune.quic.be.stream.max-concurrent 100" in output
        assert "tune.quic.be.tx.pacing on" in output
