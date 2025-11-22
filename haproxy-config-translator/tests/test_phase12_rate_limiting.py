"""
Test Phase 12 Batch 1: Rate Limiting Global Directives

This test module covers rate limiting directives for controlling connection rates,
session rates, SSL handshake rates, pipe limits, and compression CPU usage.

Coverage:
- maxconnrate: Maximum connection rate per second
- maxsessrate: Maximum session rate per second
- maxsslrate: Maximum SSL handshake rate per second
- maxpipes: Maximum number of pipes
- maxcompcpuusage: Maximum CPU percentage for compression
"""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase12RateLimiting:
    """Test cases for Phase 12 Batch 1: Rate Limiting directives."""

    def test_maxconnrate_basic(self):
        """Test maxconnrate directive with basic value."""
        config = """
        config test {
            global {
                maxconn: 2000
                maxconnrate: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxconnrate == 100

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxconnrate 100" in output

    def test_maxconnrate_high_load(self):
        """Test maxconnrate with high connection rate for production systems."""
        config = """
        config test {
            global {
                maxconn: 50000
                maxconnrate: 5000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxconnrate == 5000
        assert ir.global_config.maxconn == 50000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxconnrate 5000" in output
        assert "maxconn 50000" in output

    def test_maxconnrate_conservative(self):
        """Test maxconnrate with conservative rate limiting."""
        config = """
        config test {
            global {
                maxconnrate: 10
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxconnrate == 10

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxconnrate 10" in output

    def test_maxsessrate_basic(self):
        """Test maxsessrate directive with basic value."""
        config = """
        config test {
            global {
                maxsessrate: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxsessrate == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxsessrate 50" in output

    def test_maxsessrate_high_traffic(self):
        """Test maxsessrate for high-traffic scenarios."""
        config = """
        config test {
            global {
                maxconn: 100000
                maxsessrate: 10000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxsessrate == 10000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxsessrate 10000" in output

    def test_maxsslrate_basic(self):
        """Test maxsslrate directive for SSL handshake rate limiting."""
        config = """
        config test {
            global {
                maxsslrate: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxsslrate == 100

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxsslrate 100" in output

    def test_maxsslrate_ssl_heavy(self):
        """Test maxsslrate for SSL-heavy workloads."""
        config = """
        config test {
            global {
                maxconn: 50000
                maxsslrate: 2000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxsslrate == 2000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxsslrate 2000" in output

    def test_maxsslrate_conservative(self):
        """Test maxsslrate with conservative SSL handshake limiting."""
        config = """
        config test {
            global {
                maxsslrate: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxsslrate == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxsslrate 50" in output

    def test_maxpipes_basic(self):
        """Test maxpipes directive for pipe buffer control."""
        config = """
        config test {
            global {
                maxpipes: 16
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxpipes == 16

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxpipes 16" in output

    def test_maxpipes_high_performance(self):
        """Test maxpipes with higher values for performance."""
        config = """
        config test {
            global {
                maxconn: 20000
                maxpipes: 128
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxpipes == 128

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxpipes 128" in output

    def test_maxpipes_zero(self):
        """Test maxpipes with zero to disable pipe usage."""
        config = """
        config test {
            global {
                maxpipes: 0
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxpipes == 0

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxpipes 0" in output

    def test_maxcompcpuusage_basic(self):
        """Test maxcompcpuusage directive for CPU usage limiting."""
        config = """
        config test {
            global {
                maxcompcpuusage: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxcompcpuusage == 50

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxcompcpuusage 50" in output

    def test_maxcompcpuusage_conservative(self):
        """Test maxcompcpuusage with conservative CPU limits."""
        config = """
        config test {
            global {
                maxcompcpuusage: 25
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxcompcpuusage == 25

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxcompcpuusage 25" in output

    def test_maxcompcpuusage_aggressive(self):
        """Test maxcompcpuusage with aggressive compression."""
        config = """
        config test {
            global {
                maxcompcpuusage: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxcompcpuusage == 100

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxcompcpuusage 100" in output

    def test_maxcompcpuusage_zero(self):
        """Test maxcompcpuusage with zero to disable compression."""
        config = """
        config test {
            global {
                maxcompcpuusage: 0
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxcompcpuusage == 0

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxcompcpuusage 0" in output

    def test_combined_rate_limiting(self):
        """Test all rate limiting directives together."""
        config = """
        config test {
            global {
                maxconn: 50000
                maxconnrate: 1000
                maxsessrate: 500
                maxsslrate: 200
                maxpipes: 64
                maxcompcpuusage: 75
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.maxconnrate == 1000
        assert ir.global_config.maxsessrate == 500
        assert ir.global_config.maxsslrate == 200
        assert ir.global_config.maxpipes == 64
        assert ir.global_config.maxcompcpuusage == 75

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxconn 50000" in output
        assert "maxconnrate 1000" in output
        assert "maxsessrate 500" in output
        assert "maxsslrate 200" in output
        assert "maxpipes 64" in output
        assert "maxcompcpuusage 75" in output

    def test_production_rate_limiting_config(self):
        """Test realistic production rate limiting configuration."""
        config = """
        config production {
            global {
                maxconn: 100000
                maxconnrate: 5000
                maxsessrate: 10000
                maxsslrate: 1000
                maxpipes: 128
                maxcompcpuusage: 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all limits are set correctly
        assert ir.global_config.maxconn == 100000
        assert ir.global_config.maxconnrate == 5000
        assert ir.global_config.maxsessrate == 10000
        assert ir.global_config.maxsslrate == 1000
        assert ir.global_config.maxpipes == 128
        assert ir.global_config.maxcompcpuusage == 50

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "maxconn 100000" in output
        assert "maxconnrate 5000" in output
        assert "maxsessrate 10000" in output
        assert "maxsslrate 1000" in output
        assert "maxpipes 128" in output
        assert "maxcompcpuusage 50" in output
