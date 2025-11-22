"""
Test Phase 12 Batch 4: SSL/TLS Advanced Directives

This test module covers advanced SSL/TLS tuning directives for OCSP updates,
hard limits on SSL record sizes, and SSL context caching.

Coverage:
- tune.ssl.hard-maxrecord: Hard limit on SSL/TLS record size
- tune.ssl.ocsp-update.maxdelay: Maximum delay for OCSP updates
- tune.ssl.ocsp-update.mindelay: Minimum delay for OCSP updates
- tune.ssl.ssl-ctx-cache-size: Size of SSL context cache
"""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase12SSLAdvanced:
    """Test cases for Phase 12 Batch 4: SSL/TLS advanced directives."""

    def test_tune_ssl_hard_maxrecord_basic(self):
        """Test tune.ssl.hard-maxrecord with standard size."""
        config = """
        config test {
            global {
                tune.ssl.hard-maxrecord: 16384
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.hard-maxrecord") == 16384

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.hard-maxrecord 16384" in output

    def test_tune_ssl_hard_maxrecord_small(self):
        """Test tune.ssl.hard-maxrecord with smaller size for reduced latency."""
        config = """
        config test {
            global {
                tune.ssl.hard-maxrecord: 4096
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.hard-maxrecord") == 4096

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.hard-maxrecord 4096" in output

    def test_tune_ssl_ocsp_update_maxdelay_basic(self):
        """Test tune.ssl.ocsp-update.maxdelay with standard delay."""
        config = """
        config test {
            global {
                tune.ssl.ocsp-update.maxdelay: 3600
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.maxdelay") == 3600

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.ocsp-update.maxdelay 3600" in output

    def test_tune_ssl_ocsp_update_mindelay_basic(self):
        """Test tune.ssl.ocsp-update.mindelay with standard delay."""
        config = """
        config test {
            global {
                tune.ssl.ocsp-update.mindelay: 300
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.mindelay") == 300

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.ocsp-update.mindelay 300" in output

    def test_tune_ssl_ocsp_update_delays_together(self):
        """Test tune.ssl.ocsp-update.maxdelay and mindelay together."""
        config = """
        config test {
            global {
                tune.ssl.ocsp-update.mindelay: 600
                tune.ssl.ocsp-update.maxdelay: 7200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.mindelay") == 600
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.maxdelay") == 7200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.ocsp-update.mindelay 600" in output
        assert "tune.ssl.ocsp-update.maxdelay 7200" in output

    def test_tune_ssl_ssl_ctx_cache_size_basic(self):
        """Test tune.ssl.ssl-ctx-cache-size with standard cache size."""
        config = """
        config test {
            global {
                tune.ssl.ssl-ctx-cache-size: 1000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.ssl-ctx-cache-size") == 1000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.ssl-ctx-cache-size 1000" in output

    def test_tune_ssl_ssl_ctx_cache_size_large(self):
        """Test tune.ssl.ssl-ctx-cache-size with large cache for high traffic."""
        config = """
        config test {
            global {
                tune.ssl.ssl-ctx-cache-size: 10000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.ssl-ctx-cache-size") == 10000

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.ssl-ctx-cache-size 10000" in output

    def test_ssl_advanced_combined(self):
        """Test all SSL advanced directives together."""
        config = """
        config test {
            global {
                tune.ssl.hard-maxrecord: 8192
                tune.ssl.ocsp-update.mindelay: 300
                tune.ssl.ocsp-update.maxdelay: 3600
                tune.ssl.ssl-ctx-cache-size: 2000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all settings
        assert ir.global_config.tuning.get("tune.ssl.hard-maxrecord") == 8192
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.mindelay") == 300
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.maxdelay") == 3600
        assert ir.global_config.tuning.get("tune.ssl.ssl-ctx-cache-size") == 2000

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.ssl.hard-maxrecord 8192" in output
        assert "tune.ssl.ocsp-update.mindelay 300" in output
        assert "tune.ssl.ocsp-update.maxdelay 3600" in output
        assert "tune.ssl.ssl-ctx-cache-size 2000" in output

    def test_ssl_advanced_with_existing_ssl_settings(self):
        """Test SSL advanced directives with existing SSL settings."""
        config = """
        config test {
            global {
                tune.ssl.cachesize: 20000
                tune.ssl.default-dh-param: 2048
                tune.ssl.hard-maxrecord: 16384
                tune.ssl.ssl-ctx-cache-size: 5000
                tune.ssl.ocsp-update.mindelay: 600
                tune.ssl.ocsp-update.maxdelay: 7200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify existing SSL settings still work
        assert ir.global_config.tuning.get("tune.ssl.cachesize") == 20000
        assert ir.global_config.tuning.get("tune.ssl.default-dh-param") == 2048

        # Verify new SSL settings
        assert ir.global_config.tuning.get("tune.ssl.hard-maxrecord") == 16384
        assert ir.global_config.tuning.get("tune.ssl.ssl-ctx-cache-size") == 5000
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.mindelay") == 600
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.maxdelay") == 7200

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.ssl.cachesize 20000" in output
        assert "tune.ssl.default-dh-param 2048" in output
        assert "tune.ssl.hard-maxrecord 16384" in output
        assert "tune.ssl.ssl-ctx-cache-size 5000" in output
        assert "tune.ssl.ocsp-update.mindelay 600" in output
        assert "tune.ssl.ocsp-update.maxdelay 7200" in output

    def test_ssl_ocsp_production_config(self):
        """Test production OCSP configuration with realistic values."""
        config = """
        config production {
            global {
                tune.ssl.ocsp-update.mindelay: 900
                tune.ssl.ocsp-update.maxdelay: 14400
                tune.ssl.ssl-ctx-cache-size: 50000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify production OCSP settings
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.mindelay") == 900
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.maxdelay") == 14400
        assert ir.global_config.tuning.get("tune.ssl.ssl-ctx-cache-size") == 50000

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "tune.ssl.ocsp-update.mindelay 900" in output
        assert "tune.ssl.ocsp-update.maxdelay 14400" in output
        assert "tune.ssl.ssl-ctx-cache-size 50000" in output

    def test_ssl_hard_maxrecord_latency_optimized(self):
        """Test tune.ssl.hard-maxrecord optimized for low latency."""
        config = """
        config latency {
            global {
                tune.ssl.hard-maxrecord: 1370
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("tune.ssl.hard-maxrecord") == 1370

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tune.ssl.hard-maxrecord 1370" in output

    def test_complete_ssl_tuning_config(self):
        """Test comprehensive SSL tuning configuration."""
        config = """
        config ssl_optimized {
            global {
                daemon: true
                maxconn: 100000
                tune.ssl.cachesize: 100000
                tune.ssl.lifetime: 300
                tune.ssl.maxrecord: 16384
                tune.ssl.default-dh-param: 2048
                tune.ssl.force-private-cache: true
                tune.ssl.hard-maxrecord: 8192
                tune.ssl.ocsp-update.mindelay: 1200
                tune.ssl.ocsp-update.maxdelay: 10800
                tune.ssl.ssl-ctx-cache-size: 25000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all SSL settings
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 100000
        assert ir.global_config.tuning.get("tune.ssl.cachesize") == 100000
        assert ir.global_config.tuning.get("tune.ssl.lifetime") == 300
        assert ir.global_config.tuning.get("tune.ssl.maxrecord") == 16384
        assert ir.global_config.tuning.get("tune.ssl.default-dh-param") == 2048
        assert ir.global_config.tuning.get("tune.ssl.force-private-cache") is True
        assert ir.global_config.tuning.get("tune.ssl.hard-maxrecord") == 8192
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.mindelay") == 1200
        assert ir.global_config.tuning.get("tune.ssl.ocsp-update.maxdelay") == 10800
        assert ir.global_config.tuning.get("tune.ssl.ssl-ctx-cache-size") == 25000

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 100000" in output
        assert "tune.ssl.cachesize 100000" in output
        assert "tune.ssl.lifetime 300" in output
        assert "tune.ssl.maxrecord 16384" in output
        assert "tune.ssl.default-dh-param 2048" in output
        assert "tune.ssl.force-private-cache on" in output
        assert "tune.ssl.hard-maxrecord 8192" in output
        assert "tune.ssl.ocsp-update.mindelay 1200" in output
        assert "tune.ssl.ocsp-update.maxdelay 10800" in output
        assert "tune.ssl.ssl-ctx-cache-size 25000" in output
