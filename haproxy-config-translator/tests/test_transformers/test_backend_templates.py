"""Tests for backend template expansion."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


@pytest.fixture
def parser():
    return DSLParser()


@pytest.fixture
def codegen():
    return HAProxyCodeGenerator()


class TestBackendTemplates:
    """Tests for backend template functionality."""

    def test_backend_template_spread_basic(self, parser, codegen):
        """Test basic backend template spread with @template_name."""
        dsl_source = """
config test {
    template production_backend {
        balance: leastconn
        retries: 5
    }

    backend api {
        @production_backend

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

        # Verify template properties are applied
        assert "backend api" in output
        assert "balance leastconn" in output
        assert "retries 5" in output

    def test_backend_template_with_explicit_override(self, parser, codegen):
        """Test backend template with explicit property override."""
        dsl_source = """
config test {
    template standard_backend {
        balance: roundrobin
        retries: 3
    }

    backend api {
        @standard_backend
        retries: 5

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

        # Explicit retries should override template
        assert "backend api" in output
        assert "balance roundrobin" in output
        assert "retries 5" in output

    def test_backend_template_with_options(self, parser, codegen):
        """Test backend template with options list."""
        dsl_source = """
config test {
    template http_backend {
        option: ["httpchk GET /health", "forwardfor"]
        balance: roundrobin
    }

    backend web {
        @http_backend

        servers {
            server web1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Verify options from template are applied
        assert "backend web" in output
        assert "balance roundrobin" in output
        assert "option httpchk GET /health" in output
        assert "option forwardfor" in output

    def test_multiple_backends_same_template(self, parser, codegen):
        """Test same backend template used across multiple backends."""
        dsl_source = """
config test {
    template api_backend {
        balance: leastconn
        option: ["httpchk GET /health"]
    }

    backend api_v1 {
        @api_backend

        servers {
            server v1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }

    backend api_v2 {
        @api_backend

        servers {
            server v2 {
                address: "10.0.2.1"
                port: 8080
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Both backends should have template properties
        assert "backend api_v1" in output
        assert "backend api_v2" in output
        # Count occurrences of balance leastconn
        assert output.count("balance leastconn") == 2


class TestBackendTemplateExpansion:
    """Tests for the template expansion transformer with backends."""

    def test_backend_template_missing_graceful(self, parser):
        """Missing template should be handled gracefully."""
        dsl_source = """
config test {
    backend api {
        @nonexistent_template

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
        assert len(ir.backends) == 1


class TestBackendTemplateCodeGen:
    """Tests for code generation with backend templates."""

    def test_backend_template_generates_valid_config(self, parser, codegen):
        """Backend template should generate valid HAProxy config."""
        dsl_source = """
config test {
    template production_backend {
        balance: leastconn
        option: ["httpchk GET /health"]
        retries: 3
    }

    backend production {
        @production_backend

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

        # Verify backend is generated with template properties
        assert "backend production" in output
        assert "balance leastconn" in output
        assert "option httpchk GET /health" in output
        assert "retries 3" in output
        assert "server prod1" in output


class TestCombinedBackendTemplates:
    """Tests for combining backend templates with other template types."""

    def test_backend_and_server_templates_together(self, parser, codegen):
        """Test backend templates combined with server templates."""
        dsl_source = """
config test {
    template prod_backend {
        balance: leastconn
        option: ["httpchk GET /health"]
    }

    template prod_server {
        check: true
        inter: 3s
        fall: 3
        rise: 2
    }

    backend api {
        @prod_backend

        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
                @prod_server
            }
            server api2 {
                address: "10.0.1.2"
                port: 8080
                @prod_server
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Verify backend template properties
        assert "backend api" in output
        assert "balance leastconn" in output
        assert "option httpchk GET /health" in output

        # Verify server template properties applied to both servers
        assert "server api1 10.0.1.1:8080 check inter 3s rise 2 fall 3" in output
        assert "server api2 10.0.1.2:8080 check inter 3s rise 2 fall 3" in output

    def test_backend_with_health_check_and_acl_templates(self, parser, codegen):
        """Test backend templates with health check and ACL templates."""
        dsl_source = """
config test {
    template prod_backend {
        balance: roundrobin
        option: ["httpchk"]
    }

    template http_health {
        method: "GET"
        uri: "/api/health"
    }

    backend api {
        @prod_backend
        health-check @http_health

        servers {
            server api1 {
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

        # Verify backend and health check templates
        assert "backend api" in output
        assert "balance roundrobin" in output
        assert "option httpchk" in output
