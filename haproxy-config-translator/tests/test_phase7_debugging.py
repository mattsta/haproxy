"""Tests for Phase 7 debugging and development directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase7Debugging:
    """Test Phase 7 debugging and development directives."""

    def test_quiet(self):
        """Test quiet directive - suppress warnings."""
        config = """
        config test {
            global {
                quiet: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.quiet is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quiet" in output

    def test_quiet_false(self):
        """Test quiet directive set to false."""
        config = """
        config test {
            global {
                quiet: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.quiet is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quiet" not in output

    def test_debug_counters(self):
        """Test debug.counters directive - debug counter output file."""
        config = """
        config test {
            global {
                debug.counters: "/var/log/haproxy-counters.log"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.debug_counters == "/var/log/haproxy-counters.log"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "debug.counters /var/log/haproxy-counters.log" in output

    def test_anonkey(self):
        """Test anonkey directive - anonymization key."""
        config = """
        config test {
            global {
                anonkey: 12345
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.anonkey == 12345

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "anonkey 12345" in output

    def test_anonkey_large_value(self):
        """Test anonkey with large integer value."""
        config = """
        config test {
            global {
                anonkey: 2147483647
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.anonkey == 2147483647

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "anonkey 2147483647" in output

    def test_zero_warning(self):
        """Test zero-warning directive - treat warnings as errors."""
        config = """
        config test {
            global {
                zero-warning: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.zero_warning is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "zero-warning" in output

    def test_zero_warning_false(self):
        """Test zero-warning directive set to false."""
        config = """
        config test {
            global {
                zero-warning: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.zero_warning is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "zero-warning" not in output

    def test_warn_blocked_traffic_after(self):
        """Test warn-blocked-traffic-after directive."""
        config = """
        config test {
            global {
                warn-blocked-traffic-after: "5s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.warn_blocked_traffic_after == "5s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "warn-blocked-traffic-after 5s" in output

    def test_warn_blocked_traffic_after_minutes(self):
        """Test warn-blocked-traffic-after with minute value."""
        config = """
        config test {
            global {
                warn-blocked-traffic-after: "2m"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.warn_blocked_traffic_after == "2m"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "warn-blocked-traffic-after 2m" in output

    def test_force_cfg_parser_pause(self):
        """Test force-cfg-parser-pause directive."""
        config = """
        config test {
            global {
                force-cfg-parser-pause: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.force_cfg_parser_pause is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "force-cfg-parser-pause" in output

    def test_force_cfg_parser_pause_false(self):
        """Test force-cfg-parser-pause directive set to false."""
        config = """
        config test {
            global {
                force-cfg-parser-pause: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.force_cfg_parser_pause is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "force-cfg-parser-pause" not in output

    def test_multiple_debugging_directives(self):
        """Test multiple debugging directives together."""
        config = """
        config test {
            global {
                quiet: true
                debug.counters: "/var/log/debug-counters.log"
                anonkey: 98765
                zero-warning: true
                warn-blocked-traffic-after: "10s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.quiet is True
        assert ir.global_config.debug_counters == "/var/log/debug-counters.log"
        assert ir.global_config.anonkey == 98765
        assert ir.global_config.zero_warning is True
        assert ir.global_config.warn_blocked_traffic_after == "10s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quiet" in output
        assert "debug.counters /var/log/debug-counters.log" in output
        assert "anonkey 98765" in output
        assert "zero-warning" in output
        assert "warn-blocked-traffic-after 10s" in output

    def test_all_phase7_directives(self):
        """Test all Phase 7 directives in a complete config."""
        config = """
        config test {
            global {
                quiet: true
                debug.counters: "/var/log/haproxy/counters.log"
                anonkey: 123456789
                zero-warning: true
                warn-blocked-traffic-after: "30s"
                force-cfg-parser-pause: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.quiet is True
        assert ir.global_config.debug_counters == "/var/log/haproxy/counters.log"
        assert ir.global_config.anonkey == 123456789
        assert ir.global_config.zero_warning is True
        assert ir.global_config.warn_blocked_traffic_after == "30s"
        assert ir.global_config.force_cfg_parser_pause is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quiet" in output
        assert "debug.counters /var/log/haproxy/counters.log" in output
        assert "anonkey 123456789" in output
        assert "zero-warning" in output
        assert "warn-blocked-traffic-after 30s" in output
        assert "force-cfg-parser-pause" in output

    def test_debugging_with_frontend_backend(self):
        """Test debugging directives in a complete configuration with frontend and backend."""
        config = """
        config test {
            global {
                quiet: true
                anonkey: 42
                zero-warning: true
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
        assert ir.global_config.quiet is True
        assert ir.global_config.anonkey == 42
        assert ir.global_config.zero_warning is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quiet" in output
        assert "anonkey 42" in output
        assert "zero-warning" in output
        assert "frontend web" in output
        assert "backend servers" in output
