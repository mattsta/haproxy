"""Phase 13 Batch 4: SSL advanced directives tests.

Tests for:
- ssl-default-bind-curves: Elliptic curves for bind
- ssl-default-bind-sigalgs: Signature algorithms for bind
- ssl-default-bind-client-sigalgs: Client signature algorithms for bind
- ssl-default-server-curves: Elliptic curves for server
- ssl-default-server-sigalgs: Signature algorithms for server
- ssl-default-server-client-sigalgs: Client signature algorithms for server
- ssl-security-level: OpenSSL security level
"""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase13SSLAdvanced:
    """Test Phase 13 Batch 4: SSL advanced directives."""

    def test_ssl_default_bind_curves(self):
        """Test ssl-default-bind-curves for elliptic curves."""
        config = """
        config test {
            global {
                ssl-default-bind-curves: "X25519:P-256:P-384"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_default_bind_curves == "X25519:P-256:P-384"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-default-bind-curves X25519:P-256:P-384" in output

    def test_ssl_default_bind_sigalgs(self):
        """Test ssl-default-bind-sigalgs for signature algorithms."""
        config = """
        config test {
            global {
                ssl-default-bind-sigalgs: "RSA+SHA256:ECDSA+SHA256"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_default_bind_sigalgs == "RSA+SHA256:ECDSA+SHA256"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-default-bind-sigalgs RSA+SHA256:ECDSA+SHA256" in output

    def test_ssl_default_bind_client_sigalgs(self):
        """Test ssl-default-bind-client-sigalgs for client signatures."""
        config = """
        config test {
            global {
                ssl-default-bind-client-sigalgs: "ECDSA+SHA256:RSA+SHA256"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_default_bind_client_sigalgs == "ECDSA+SHA256:RSA+SHA256"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-default-bind-client-sigalgs ECDSA+SHA256:RSA+SHA256" in output

    def test_ssl_default_server_curves(self):
        """Test ssl-default-server-curves for server elliptic curves."""
        config = """
        config test {
            global {
                ssl-default-server-curves: "X25519:P-256"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_default_server_curves == "X25519:P-256"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-default-server-curves X25519:P-256" in output

    def test_ssl_default_server_sigalgs(self):
        """Test ssl-default-server-sigalgs for server signature algorithms."""
        config = """
        config test {
            global {
                ssl-default-server-sigalgs: "RSA+SHA384:ECDSA+SHA384"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_default_server_sigalgs == "RSA+SHA384:ECDSA+SHA384"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-default-server-sigalgs RSA+SHA384:ECDSA+SHA384" in output

    def test_ssl_default_server_client_sigalgs(self):
        """Test ssl-default-server-client-sigalgs for server client signatures."""
        config = """
        config test {
            global {
                ssl-default-server-client-sigalgs: "ECDSA+SHA512:RSA+SHA512"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_default_server_client_sigalgs == "ECDSA+SHA512:RSA+SHA512"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-default-server-client-sigalgs ECDSA+SHA512:RSA+SHA512" in output

    def test_ssl_security_level(self):
        """Test ssl-security-level for OpenSSL security level."""
        config = """
        config test {
            global {
                ssl-security-level: 2
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_security_level == 2

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-security-level 2" in output

    def test_ssl_security_level_strict(self):
        """Test ssl-security-level with strict level 3."""
        config = """
        config test {
            global {
                ssl-security-level: 3
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_security_level == 3

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-security-level 3" in output

    def test_ssl_complete_modern_config(self):
        """Test complete modern SSL configuration with all directives."""
        config = """
        config test {
            global {
                daemon: true
                ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
                ssl-default-bind-ciphersuites: "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"
                ssl-default-bind-curves: "X25519:P-256:P-384"
                ssl-default-bind-sigalgs: "ECDSA+SHA256:RSA+SHA256:ECDSA+SHA384:RSA+SHA384"
                ssl-default-bind-client-sigalgs: "ECDSA+SHA256:RSA+SHA256"
                ssl-default-server-ciphers: "ECDHE-RSA-AES128-GCM-SHA256"
                ssl-default-server-ciphersuites: "TLS_AES_128_GCM_SHA256"
                ssl-default-server-curves: "X25519:P-256"
                ssl-default-server-sigalgs: "RSA+SHA256:RSA+SHA384"
                ssl-default-server-client-sigalgs: "RSA+SHA256"
                ssl-security-level: 2
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify bind configuration
        assert ir.global_config.ssl_default_bind_curves == "X25519:P-256:P-384"
        assert (
            ir.global_config.ssl_default_bind_sigalgs
            == "ECDSA+SHA256:RSA+SHA256:ECDSA+SHA384:RSA+SHA384"
        )
        assert ir.global_config.ssl_default_bind_client_sigalgs == "ECDSA+SHA256:RSA+SHA256"

        # Verify server configuration
        assert ir.global_config.ssl_default_server_curves == "X25519:P-256"
        assert ir.global_config.ssl_default_server_sigalgs == "RSA+SHA256:RSA+SHA384"
        assert ir.global_config.ssl_default_server_client_sigalgs == "RSA+SHA256"

        # Verify security level
        assert ir.global_config.ssl_security_level == 2

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Check all directives are present
        assert "ssl-default-bind-curves X25519:P-256:P-384" in output
        assert "ssl-default-bind-sigalgs ECDSA+SHA256:RSA+SHA256:ECDSA+SHA384:RSA+SHA384" in output
        assert "ssl-default-bind-client-sigalgs ECDSA+SHA256:RSA+SHA256" in output
        assert "ssl-default-server-curves X25519:P-256" in output
        assert "ssl-default-server-sigalgs RSA+SHA256:RSA+SHA384" in output
        assert "ssl-default-server-client-sigalgs RSA+SHA256" in output
        assert "ssl-security-level 2" in output

    def test_ssl_high_security_config(self):
        """Test high-security SSL configuration."""
        config = """
        config test {
            global {
                ssl-default-bind-ciphersuites: "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256"
                ssl-default-bind-curves: "X25519:X448"
                ssl-default-bind-sigalgs: "ECDSA+SHA512:RSA+SHA512"
                ssl-security-level: 3
                tune.ssl.default-dh-param: 4096
                tune.ssl.lifetime: "1h"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.ssl_default_bind_curves == "X25519:X448"
        assert ir.global_config.ssl_default_bind_sigalgs == "ECDSA+SHA512:RSA+SHA512"
        assert ir.global_config.ssl_security_level == 3

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "ssl-default-bind-curves X25519:X448" in output
        assert "ssl-default-bind-sigalgs ECDSA+SHA512:RSA+SHA512" in output
        assert "ssl-security-level 3" in output
        assert "tune.ssl.default-dh-param 4096" in output

    def test_ssl_backend_specific_config(self):
        """Test SSL configuration with backend-specific settings."""
        config = """
        config test {
            global {
                ssl-default-bind-curves: "X25519:P-256:P-384:P-521"
                ssl-default-server-curves: "P-256:P-384"
                ssl-default-bind-sigalgs: "ECDSA+SHA256:RSA+SHA256"
                ssl-default-server-sigalgs: "ECDSA+SHA384:RSA+SHA384:ECDSA+SHA512:RSA+SHA512"
                ssl-security-level: 2
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.global_config.ssl_default_bind_curves == "X25519:P-256:P-384:P-521"
        assert ir.global_config.ssl_default_server_curves == "P-256:P-384"
        assert ir.global_config.ssl_default_bind_sigalgs == "ECDSA+SHA256:RSA+SHA256"
        assert (
            ir.global_config.ssl_default_server_sigalgs
            == "ECDSA+SHA384:RSA+SHA384:ECDSA+SHA512:RSA+SHA512"
        )

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "ssl-default-bind-curves X25519:P-256:P-384:P-521" in output
        assert "ssl-default-server-curves P-256:P-384" in output
        assert "ssl-default-bind-sigalgs ECDSA+SHA256:RSA+SHA256" in output
        assert (
            "ssl-default-server-sigalgs ECDSA+SHA384:RSA+SHA384:ECDSA+SHA512:RSA+SHA512" in output
        )
