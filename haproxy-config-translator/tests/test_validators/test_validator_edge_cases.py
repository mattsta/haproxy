"""Test validator edge cases for improved coverage."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.validators.semantic import SemanticValidator


class TestValidatorEdgeCases:
    """Test edge cases in semantic validation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_tcp_option_in_http_mode(self, parser):
        """Test warning when TCP option is used in HTTP mode."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                mode: http
                option: ["tcplog"]
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SemanticValidator(ir)
        validator.validate()

        # Should have a warning about TCP option in HTTP mode
        assert len(validator.warnings) > 0
        assert any("TCP option" in w and "HTTP mode" in w for w in validator.warnings)

    def test_health_check_with_method_but_no_uri(self):
        """Test warning for health check with method but missing URI."""
        from haproxy_translator.ir.nodes import (
            ConfigIR, Backend, Server, HealthCheck, BalanceAlgorithm
        )

        # Create IR with health check that has method but no URI
        health_check = HealthCheck(method="GET", uri="")
        backend = Backend(
            name="api",
            balance=BalanceAlgorithm.ROUNDROBIN,
            health_check=health_check,
            servers=[Server(name="api1", address="10.0.1.1", port=8080)]
        )
        ir = ConfigIR(backends=[backend])

        validator = SemanticValidator(ir)
        validator.validate()

        # Should have a warning about missing URI
        assert len(validator.warnings) > 0
        assert any("has method but no URI" in w for w in validator.warnings)
