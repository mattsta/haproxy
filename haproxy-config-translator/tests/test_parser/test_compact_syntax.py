"""Tests for compact DSL syntax features."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


@pytest.fixture
def parser():
    return DSLParser()


@pytest.fixture
def codegen():
    return HAProxyCodeGenerator()


class TestCompactServerSyntax:
    """Tests for compact server definition syntax."""

    def test_comma_separated_server_properties(self, parser, codegen):
        """Test server definition with comma-separated properties."""
        dsl_source = """
config test {
    backend api {
        servers {
            server s1 { address: "10.0.1.1", port: 8080, check: true }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        assert len(ir.backends) == 1
        assert len(ir.backends[0].servers) == 1
        server = ir.backends[0].servers[0]
        assert server.address == "10.0.1.1"
        assert server.port == 8080
        assert server.check is True

    def test_mixed_syntax_comma_and_newline(self, parser, codegen):
        """Test mixing comma-separated and newline-separated properties."""
        dsl_source = """
config test {
    backend api {
        servers {
            server s1 {
                address: "10.0.1.1", port: 8080,
                check: true
                weight: 100
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        server = ir.backends[0].servers[0]
        assert server.address == "10.0.1.1"
        assert server.port == 8080
        assert server.check is True
        assert server.weight == 100

    def test_trailing_comma_allowed(self, parser):
        """Test that trailing comma is allowed."""
        dsl_source = """
config test {
    backend api {
        servers {
            server s1 { address: "10.0.1.1", port: 8080, }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        assert len(ir.backends[0].servers) == 1

    def test_multiple_servers_compact(self, parser, codegen):
        """Test multiple servers with compact syntax."""
        dsl_source = """
config test {
    backend api {
        servers {
            server s1 { address: "10.0.1.1", port: 8080, check: true }
            server s2 { address: "10.0.1.2", port: 8080, check: true }
            server s3 { address: "10.0.1.3", port: 8080, check: true }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server s1 10.0.1.1:8080 check" in output
        assert "server s2 10.0.1.2:8080 check" in output
        assert "server s3 10.0.1.3:8080 check" in output

    def test_inline_server_syntax(self, parser, codegen):
        """Test inline server syntax (space-separated, no braces)."""
        dsl_source = """
config test {
    backend api {
        servers {
            server s1 address: "10.0.1.1" port: 8080 check: true
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        server = ir.backends[0].servers[0]
        assert server.address == "10.0.1.1"
        assert server.port == 8080
        assert server.check is True


class TestCompactSyntaxWithTemplates:
    """Tests for compact syntax combined with templates."""

    def test_compact_server_with_template_spread(self, parser, codegen):
        """Test compact server syntax with template spread."""
        dsl_source = """
config test {
    template prod_server {
        check: true
        inter: 3s
        fall: 3
        rise: 2
    }

    backend api {
        servers {
            server s1 { address: "10.0.1.1", port: 8080, @prod_server }
            server s2 { address: "10.0.1.2", port: 8080, @prod_server }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Both servers should have template properties applied
        assert "server s1 10.0.1.1:8080 check inter 3s" in output
        assert "server s2 10.0.1.2:8080 check inter 3s" in output

    def test_compact_syntax_in_loop(self, parser, codegen):
        """Test compact syntax inside a for loop."""
        dsl_source = """
config test {
    backend api {
        servers {
            for i in [1..3] {
                server "api${i}" { address: "10.0.1.${i}", port: 8080, check: true }
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server api1 10.0.1.1:8080 check" in output
        assert "server api2 10.0.1.2:8080 check" in output
        assert "server api3 10.0.1.3:8080 check" in output


class TestDefaultServerDirective:
    """Tests for default-server directive."""

    def test_default_server_output(self, parser, codegen):
        """Test that default-server directive generates correct HAProxy output."""
        dsl_source = """
config test {
    backend api {
        default-server {
            check: true
            inter: 3s
            fall: 3
            rise: 2
            weight: 100
        }
        servers {
            server s1 { address: "10.0.1.1", port: 8080 }
            server s2 { address: "10.0.1.2", port: 8080 }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Verify default-server directive is in output
        assert "default-server check inter 3s" in output
        assert "weight 100" in output

        # Verify servers are defined (they inherit from default-server at runtime)
        assert "server s1 10.0.1.1:8080" in output
        assert "server s2 10.0.1.2:8080" in output

    def test_default_server_with_ssl_options(self, parser, codegen):
        """Test default-server with SSL options."""
        dsl_source = """
config test {
    backend api {
        default-server {
            ssl: true
            verify: "required"
            check: true
        }
        servers {
            server s1 { address: "10.0.1.1", port: 8443 }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "default-server" in output
        assert "ssl" in output
        assert "verify required" in output
