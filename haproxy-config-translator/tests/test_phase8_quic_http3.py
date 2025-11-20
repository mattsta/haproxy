"""Tests for Phase 8 QUIC/HTTP3 directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase8QuicHttp3:
    """Test Phase 8 QUIC/HTTP3 directives."""

    def test_tune_quic_cc_hystart(self):
        """Test tune.quic.cc-hystart directive - enable hystart congestion control."""
        config = """
        config test {
            global {
                tune.quic.cc-hystart: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.cc-hystart") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.cc-hystart on" in output

    def test_tune_quic_cc_hystart_false(self):
        """Test tune.quic.cc-hystart directive set to false."""
        config = """
        config test {
            global {
                tune.quic.cc-hystart: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.cc-hystart") is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.cc-hystart off" in output

    def test_tune_quic_reorder_ratio(self):
        """Test tune.quic.reorder-ratio directive - packet reordering threshold."""
        config = """
        config test {
            global {
                tune.quic.reorder-ratio: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.reorder-ratio") == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.reorder-ratio 50" in output

    def test_tune_quic_reorder_ratio_custom(self):
        """Test tune.quic.reorder-ratio with custom value."""
        config = """
        config test {
            global {
                tune.quic.reorder-ratio: 75
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.reorder-ratio") == 75

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.reorder-ratio 75" in output

    def test_tune_quic_zero_copy_fwd_send(self):
        """Test tune.quic.zero-copy-fwd-send directive."""
        config = """
        config test {
            global {
                tune.quic.zero-copy-fwd-send: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.zero-copy-fwd-send") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.zero-copy-fwd-send on" in output

    def test_tune_quic_zero_copy_fwd_send_false(self):
        """Test tune.quic.zero-copy-fwd-send directive set to false."""
        config = """
        config test {
            global {
                tune.quic.zero-copy-fwd-send: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.zero-copy-fwd-send") is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.zero-copy-fwd-send off" in output

    def test_tune_h2_zero_copy_fwd_send(self):
        """Test tune.h2.zero-copy-fwd-send directive."""
        config = """
        config test {
            global {
                tune.h2.zero-copy-fwd-send: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h2.zero-copy-fwd-send") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h2.zero-copy-fwd-send on" in output

    def test_tune_h2_zero_copy_fwd_send_false(self):
        """Test tune.h2.zero-copy-fwd-send directive set to false."""
        config = """
        config test {
            global {
                tune.h2.zero-copy-fwd-send: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h2.zero-copy-fwd-send") is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h2.zero-copy-fwd-send off" in output

    def test_multiple_quic_http3_directives(self):
        """Test multiple QUIC/HTTP3 directives together."""
        config = """
        config test {
            global {
                tune.quic.cc-hystart: true
                tune.quic.reorder-ratio: 60
                tune.quic.zero-copy-fwd-send: true
                tune.h2.zero-copy-fwd-send: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.cc-hystart") is True
        assert ir.global_config.tuning.get("tune.quic.reorder-ratio") == 60
        assert ir.global_config.tuning.get("tune.quic.zero-copy-fwd-send") is True
        assert ir.global_config.tuning.get("tune.h2.zero-copy-fwd-send") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.cc-hystart on" in output
        assert "tune.quic.reorder-ratio 60" in output
        assert "tune.quic.zero-copy-fwd-send on" in output
        assert "tune.h2.zero-copy-fwd-send on" in output

    def test_quic_with_existing_directives(self):
        """Test new QUIC directives with existing QUIC directives."""
        config = """
        config test {
            global {
                tune.quic.frontend.max-streams-bidi: 100
                tune.quic.cc-hystart: true
                tune.quic.retry-threshold: 3
                tune.quic.reorder-ratio: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.frontend.max-streams-bidi") == 100
        assert ir.global_config.tuning.get("tune.quic.cc-hystart") is True
        assert ir.global_config.tuning.get("tune.quic.retry-threshold") == 3
        assert ir.global_config.tuning.get("tune.quic.reorder-ratio") == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.frontend.max-streams-bidi 100" in output
        assert "tune.quic.cc-hystart on" in output
        assert "tune.quic.retry-threshold 3" in output
        assert "tune.quic.reorder-ratio 50" in output

    def test_http3_with_http2_directives(self):
        """Test new HTTP/2 directive with existing HTTP/2 directives."""
        config = """
        config test {
            global {
                tune.h2.max-concurrent-streams: 100
                tune.h2.zero-copy-fwd-send: true
                tune.h2.max-frame-size: 16384
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h2.max-concurrent-streams") == 100
        assert ir.global_config.tuning.get("tune.h2.zero-copy-fwd-send") is True
        assert ir.global_config.tuning.get("tune.h2.max-frame-size") == 16384

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h2.max-concurrent-streams 100" in output
        assert "tune.h2.zero-copy-fwd-send on" in output
        assert "tune.h2.max-frame-size 16384" in output

    def test_complete_quic_http3_configuration(self):
        """Test complete QUIC/HTTP3 configuration with all new directives."""
        config = """
        config test {
            global {
                tune.quic.cc-hystart: true
                tune.quic.reorder-ratio: 55
                tune.quic.zero-copy-fwd-send: true
                tune.h2.zero-copy-fwd-send: true
                tune.quic.frontend.max-idle-timeout: "30s"
                tune.quic.max-frame-loss: 10
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.quic.cc-hystart") is True
        assert ir.global_config.tuning.get("tune.quic.reorder-ratio") == 55
        assert ir.global_config.tuning.get("tune.quic.zero-copy-fwd-send") is True
        assert ir.global_config.tuning.get("tune.h2.zero-copy-fwd-send") is True
        assert ir.global_config.tuning.get("tune.quic.frontend.max-idle-timeout") == "30s"
        assert ir.global_config.tuning.get("tune.quic.max-frame-loss") == 10

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.quic.cc-hystart on" in output
        assert "tune.quic.reorder-ratio 55" in output
        assert "tune.quic.zero-copy-fwd-send on" in output
        assert "tune.h2.zero-copy-fwd-send on" in output
        assert "tune.quic.frontend.max-idle-timeout 30s" in output
        assert "tune.quic.max-frame-loss 10" in output
