"""
Test Phase 12 Batch 5: Lua Tuning Directives

This test module covers Lua tuning directives for controlling boolean conversion,
burst timeout handling, and stderr logging behavior.

Coverage:
- tune.lua.bool-sample-conversion: Enable/disable boolean sample conversion
- tune.lua.burst-timeout: Timeout in milliseconds for Lua burst operations
- tune.lua.log.stderr: Configure Lua logging to stderr (on/off/auto)
"""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase12Lua:
    """Test cases for Phase 12 Batch 5: Lua tuning directives."""

    def test_tune_lua_bool_sample_conversion_enabled(self):
        """Test tune.lua.bool-sample-conversion enabled."""
        config = """
        config test {
            global {
                tune.lua.bool-sample-conversion: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.bool-sample-conversion") is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.bool-sample-conversion on" in output

    def test_tune_lua_bool_sample_conversion_disabled(self):
        """Test tune.lua.bool-sample-conversion disabled for strict Lua behavior."""
        config = """
        config test {
            global {
                tune.lua.bool-sample-conversion: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.bool-sample-conversion") is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.bool-sample-conversion off" in output

    def test_tune_lua_burst_timeout_basic(self):
        """Test tune.lua.burst-timeout with standard timeout."""
        config = """
        config test {
            global {
                tune.lua.burst-timeout: 1000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.burst-timeout") == 1000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.burst-timeout 1000" in output

    def test_tune_lua_burst_timeout_short(self):
        """Test tune.lua.burst-timeout with short timeout for quick failures."""
        config = """
        config test {
            global {
                tune.lua.burst-timeout: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.burst-timeout") == 100

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.burst-timeout 100" in output

    def test_tune_lua_burst_timeout_long(self):
        """Test tune.lua.burst-timeout with longer timeout for complex scripts."""
        config = """
        config test {
            global {
                tune.lua.burst-timeout: 5000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.burst-timeout") == 5000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.burst-timeout 5000" in output

    def test_tune_lua_log_stderr_on(self):
        """Test tune.lua.log.stderr enabled for debugging."""
        config = """
        config test {
            global {
                tune.lua.log.stderr: "on"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "on"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.log.stderr on" in output

    def test_tune_lua_log_stderr_off(self):
        """Test tune.lua.log.stderr disabled for production."""
        config = """
        config test {
            global {
                tune.lua.log.stderr: "off"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "off"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.log.stderr off" in output

    def test_tune_lua_log_stderr_auto(self):
        """Test tune.lua.log.stderr with auto mode."""
        config = """
        config test {
            global {
                tune.lua.log.stderr: "auto"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "auto"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.lua.log.stderr auto" in output

    def test_lua_tuning_combined(self):
        """Test all Lua tuning directives together."""
        config = """
        config test {
            global {
                tune.lua.bool-sample-conversion: true
                tune.lua.burst-timeout: 2000
                tune.lua.log.stderr: "on"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all settings
        assert ir.global_config.tuning.get("tune.lua.bool-sample-conversion") is True
        assert ir.global_config.tuning.get("tune.lua.burst-timeout") == 2000
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "on"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.lua.bool-sample-conversion on" in output
        assert "tune.lua.burst-timeout 2000" in output
        assert "tune.lua.log.stderr on" in output

    def test_lua_tuning_with_existing_lua_settings(self):
        """Test new Lua directives with existing Lua settings."""
        config = """
        config test {
            global {
                tune.lua.forced-yield: 1000
                tune.lua.maxmem: 268435456
                tune.lua.session-timeout: "4s"
                tune.lua.task-timeout: "4s"
                tune.lua.bool-sample-conversion: true
                tune.lua.burst-timeout: 1500
                tune.lua.log.stderr: "auto"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify existing Lua settings
        assert ir.global_config.tuning.get("tune.lua.forced-yield") == 1000
        assert ir.global_config.tuning.get("tune.lua.maxmem") == 268435456
        assert ir.global_config.tuning.get("tune.lua.session-timeout") == "4s"
        assert ir.global_config.tuning.get("tune.lua.task-timeout") == "4s"

        # Verify new Lua settings
        assert ir.global_config.tuning.get("tune.lua.bool-sample-conversion") is True
        assert ir.global_config.tuning.get("tune.lua.burst-timeout") == 1500
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "auto"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.lua.forced-yield 1000" in output
        assert "tune.lua.maxmem 268435456" in output
        assert "tune.lua.session-timeout 4s" in output
        assert "tune.lua.task-timeout 4s" in output
        assert "tune.lua.bool-sample-conversion on" in output
        assert "tune.lua.burst-timeout 1500" in output
        assert "tune.lua.log.stderr auto" in output

    def test_lua_development_config(self):
        """Test Lua configuration for development with debugging enabled."""
        config = """
        config dev {
            global {
                tune.lua.bool-sample-conversion: true
                tune.lua.burst-timeout: 5000
                tune.lua.log.stderr: "on"
                tune.lua.log.loggers: "stderr"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify development-friendly settings
        assert ir.global_config.tuning.get("tune.lua.bool-sample-conversion") is True
        assert ir.global_config.tuning.get("tune.lua.burst-timeout") == 5000
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "on"
        assert ir.global_config.tuning.get("tune.lua.log.loggers") == "stderr"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.lua.bool-sample-conversion on" in output
        assert "tune.lua.burst-timeout 5000" in output
        assert "tune.lua.log.stderr on" in output
        assert "tune.lua.log.loggers stderr" in output

    def test_lua_production_config(self):
        """Test Lua configuration for production with optimized settings."""
        config = """
        config production {
            global {
                daemon: true
                maxconn: 50000
                tune.lua.forced-yield: 10000
                tune.lua.maxmem: 536870912
                tune.lua.session-timeout: "10s"
                tune.lua.task-timeout: "10s"
                tune.lua.service-timeout: "30s"
                tune.lua.bool-sample-conversion: false
                tune.lua.burst-timeout: 1000
                tune.lua.log.stderr: "off"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify production settings
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.tuning.get("tune.lua.forced-yield") == 10000
        assert ir.global_config.tuning.get("tune.lua.maxmem") == 536870912
        assert ir.global_config.tuning.get("tune.lua.session-timeout") == "10s"
        assert ir.global_config.tuning.get("tune.lua.task-timeout") == "10s"
        assert ir.global_config.tuning.get("tune.lua.service-timeout") == "30s"
        assert ir.global_config.tuning.get("tune.lua.bool-sample-conversion") is False
        assert ir.global_config.tuning.get("tune.lua.burst-timeout") == 1000
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "off"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 50000" in output
        assert "tune.lua.forced-yield 10000" in output
        assert "tune.lua.maxmem 536870912" in output
        assert "tune.lua.session-timeout 10s" in output
        assert "tune.lua.task-timeout 10s" in output
        assert "tune.lua.service-timeout 30s" in output
        assert "tune.lua.bool-sample-conversion off" in output
        assert "tune.lua.burst-timeout 1000" in output
        assert "tune.lua.log.stderr off" in output

    def test_lua_log_stderr_special_handling(self):
        """Test tune.lua.log.stderr special conversion via tune_key logic."""
        config = """
        config test {
            global {
                tune.lua.log.stderr: "on"
                tune.lua.log.loggers: "stderr"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Both should work correctly via the special case for lua.log.* in transformer
        assert ir.global_config.tuning.get("tune.lua.log.stderr") == "on"
        assert ir.global_config.tuning.get("tune.lua.log.loggers") == "stderr"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.lua.log.stderr on" in output
        assert "tune.lua.log.loggers stderr" in output
