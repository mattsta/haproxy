"""
Test Phase 13 Batch 1: HTTP/2 Buffer Directives

This test module covers HTTP/2 receive buffer directives for controlling
upload performance and head-of-line blocking prevention.

Coverage:
- tune.h2.be.rxbuf: Backend HTTP/2 receive buffer size
- tune.h2.fe.rxbuf: Frontend HTTP/2 receive buffer size
"""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase13H2Buffers:
    """Test cases for Phase 13 Batch 1: HTTP/2 buffer directives."""

    def test_tune_h2_be_rxbuf_basic(self):
        """Test tune.h2.be.rxbuf with standard buffer size."""
        config = """
        config test {
            global {
                tune.h2.be.rxbuf: 32768
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h2.be.rxbuf") == 32768

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h2.be.rxbuf 32768" in output

    def test_tune_h2_be_rxbuf_large(self):
        """Test tune.h2.be.rxbuf with large buffer for high throughput."""
        config = """
        config test {
            global {
                tune.h2.be.rxbuf: 1638400
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h2.be.rxbuf") == 1638400

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h2.be.rxbuf 1638400" in output

    def test_tune_h2_fe_rxbuf_basic(self):
        """Test tune.h2.fe.rxbuf with standard buffer size."""
        config = """
        config test {
            global {
                tune.h2.fe.rxbuf: 32768
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h2.fe.rxbuf") == 32768

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h2.fe.rxbuf 32768" in output

    def test_tune_h2_fe_rxbuf_large(self):
        """Test tune.h2.fe.rxbuf with large buffer for many concurrent streams."""
        config = """
        config test {
            global {
                tune.h2.fe.rxbuf: 1638400
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.h2.fe.rxbuf") == 1638400

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.h2.fe.rxbuf 1638400" in output

    def test_h2_rxbuf_combined(self):
        """Test both frontend and backend rxbuf together."""
        config = """
        config test {
            global {
                tune.h2.fe.rxbuf: 1638400
                tune.h2.be.rxbuf: 819200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.tuning.get("tune.h2.fe.rxbuf") == 1638400
        assert ir.global_config.tuning.get("tune.h2.be.rxbuf") == 819200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.h2.fe.rxbuf 1638400" in output
        assert "tune.h2.be.rxbuf 819200" in output

    def test_h2_rxbuf_with_existing_h2_settings(self):
        """Test rxbuf directives with existing HTTP/2 settings."""
        config = """
        config test {
            global {
                tune.h2.header-table-size: 4096
                tune.h2.initial-window-size: 65535
                tune.h2.max-concurrent-streams: 100
                tune.h2.fe.rxbuf: 1638400
                tune.h2.be.rxbuf: 819200
                tune.h2.max-frame-size: 16384
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify existing settings
        assert ir.global_config.tuning.get("tune.h2.header-table-size") == 4096
        assert ir.global_config.tuning.get("tune.h2.initial-window-size") == 65535
        assert ir.global_config.tuning.get("tune.h2.max-concurrent-streams") == 100
        assert ir.global_config.tuning.get("tune.h2.max-frame-size") == 16384

        # Verify new rxbuf settings
        assert ir.global_config.tuning.get("tune.h2.fe.rxbuf") == 1638400
        assert ir.global_config.tuning.get("tune.h2.be.rxbuf") == 819200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.h2.header-table-size 4096" in output
        assert "tune.h2.initial-window-size 65535" in output
        assert "tune.h2.max-concurrent-streams 100" in output
        assert "tune.h2.max-frame-size 16384" in output
        assert "tune.h2.fe.rxbuf 1638400" in output
        assert "tune.h2.be.rxbuf 819200" in output

    def test_h2_upload_optimized_config(self):
        """Test HTTP/2 configuration optimized for upload performance."""
        config = """
        config upload_optimized {
            global {
                tune.h2.fe.rxbuf: 1638400
                tune.h2.fe.initial-window-size: 65535
                tune.h2.fe.max-concurrent-streams: 100
                tune.h2.be.rxbuf: 1638400
                tune.h2.be.initial-window-size: 65535
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify upload-optimized settings
        assert ir.global_config.tuning.get("tune.h2.fe.rxbuf") == 1638400
        assert ir.global_config.tuning.get("tune.h2.fe.initial-window-size") == 65535
        assert ir.global_config.tuning.get("tune.h2.fe.max-concurrent-streams") == 100
        assert ir.global_config.tuning.get("tune.h2.be.rxbuf") == 1638400
        assert ir.global_config.tuning.get("tune.h2.be.initial-window-size") == 65535

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.h2.fe.rxbuf 1638400" in output
        assert "tune.h2.fe.initial-window-size 65535" in output
        assert "tune.h2.fe.max-concurrent-streams 100" in output
        assert "tune.h2.be.rxbuf 1638400" in output
        assert "tune.h2.be.initial-window-size 65535" in output

    def test_h2_production_config(self):
        """Test production HTTP/2 configuration with realistic buffer sizes."""
        config = """
        config production {
            global {
                daemon: true
                maxconn: 50000
                tune.bufsize: 16384
                tune.h2.fe.rxbuf: 1638400
                tune.h2.fe.max-concurrent-streams: 100
                tune.h2.be.rxbuf: 819200
                tune.h2.be.max-concurrent-streams: 50
                tune.h2.max-frame-size: 16384
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify production settings
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.tuning.get("tune.bufsize") == 16384
        assert ir.global_config.tuning.get("tune.h2.fe.rxbuf") == 1638400
        assert ir.global_config.tuning.get("tune.h2.fe.max-concurrent-streams") == 100
        assert ir.global_config.tuning.get("tune.h2.be.rxbuf") == 819200
        assert ir.global_config.tuning.get("tune.h2.be.max-concurrent-streams") == 50
        assert ir.global_config.tuning.get("tune.h2.max-frame-size") == 16384

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 50000" in output
        assert "tune.bufsize 16384" in output
        assert "tune.h2.fe.rxbuf 1638400" in output
        assert "tune.h2.fe.max-concurrent-streams 100" in output
        assert "tune.h2.be.rxbuf 819200" in output
        assert "tune.h2.be.max-concurrent-streams 50" in output
        assert "tune.h2.max-frame-size 16384" in output
