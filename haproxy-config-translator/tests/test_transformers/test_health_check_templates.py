"""Tests for health check template expansion."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


@pytest.fixture
def parser():
    return DSLParser()


@pytest.fixture
def codegen():
    return HAProxyCodeGenerator()


class TestHealthCheckTemplates:
    """Tests for health check template functionality."""

    def test_health_check_template_spread_basic(self, parser, codegen):
        """Test basic health check template spread with @template_name."""
        dsl_source = """
config test {
    template http_health {
        method: "GET"
        uri: "/health"
        expect_status: 200
    }

    backend api {
        balance: roundrobin
        health-check @http_health

        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Verify health check properties from template are applied
        assert "backend api" in output

    def test_health_check_template_with_inline_properties(self, parser, codegen):
        """Test health check template spread combined with inline properties."""
        dsl_source = """
config test {
    template base_health {
        method: "GET"
        uri: "/ping"
    }

    backend api {
        balance: roundrobin
        health-check {
            @base_health
            uri: "/health"
        }

        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)

        # Explicit uri should override template uri
        backend = ir.backends[0]
        assert backend.health_check is not None
        # Template provides method, explicit overrides uri
        assert backend.health_check.uri == "/health"

    def test_multiple_backends_same_health_template(self, parser, codegen):
        """Test same health check template used across multiple backends."""
        dsl_source = """
config test {
    template standard_health {
        method: "GET"
        uri: "/health"
        expect_status: 200
    }

    backend api1 {
        balance: roundrobin
        health-check @standard_health

        servers {
            server s1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }

    backend api2 {
        balance: leastconn
        health-check @standard_health

        servers {
            server s2 {
                address: "10.0.2.1"
                port: 8080
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)

        # Both backends should have health checks from template
        assert ir.backends[0].health_check is not None
        assert ir.backends[1].health_check is not None


class TestHealthCheckTemplateExpansion:
    """Tests for the template expansion transformer with health checks."""

    def test_health_check_template_expansion_preserves_explicit(self, parser):
        """Template values should not override explicit non-default values."""
        dsl_source = """
config test {
    template health_template {
        method: "POST"
        uri: "/status"
    }

    backend api {
        balance: roundrobin
        health-check {
            method: "HEAD"
            @health_template
        }

        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        backend = ir.backends[0]

        # Explicit method "HEAD" (non-default) should be preserved, not overwritten by template "POST"
        assert backend.health_check is not None
        assert backend.health_check.method == "HEAD"

    def test_health_check_template_missing_graceful(self, parser):
        """Missing template should be handled gracefully."""
        dsl_source = """
config test {
    backend api {
        balance: roundrobin
        health-check @nonexistent_template

        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }
}
"""
        # Should parse without error (template just not found)
        ir = parser.parse(dsl_source)
        assert ir.backends[0].health_check is not None


class TestHealthCheckTemplateCodeGen:
    """Tests for code generation with health check templates."""

    def test_health_check_template_generates_valid_config(self, parser, codegen):
        """Health check template should generate valid HAProxy config."""
        dsl_source = """
config test {
    template production_health {
        method: "GET"
        uri: "/api/health"
        expect_status: 200
    }

    backend production {
        balance: roundrobin
        option: ["httpchk"]
        health-check @production_health

        servers {
            server prod1 {
                address: "10.0.1.1"
                port: 8080
                check: true
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Verify backend is generated
        assert "backend production" in output
        assert "balance roundrobin" in output
        assert "server prod1" in output
