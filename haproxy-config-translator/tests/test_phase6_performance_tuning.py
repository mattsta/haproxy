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
