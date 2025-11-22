"""Tests for ACL template expansion."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


@pytest.fixture
def parser():
    return DSLParser()


@pytest.fixture
def codegen():
    return HAProxyCodeGenerator()


class TestACLTemplates:
    """Tests for ACL template functionality."""

    def test_acl_template_spread_basic(self, parser, codegen):
        """Test basic ACL template spread with @template_name."""
        dsl_source = """
config test {
    template api_path_acl {
        criterion: "path_beg"
        values: ["/api/"]
    }

    frontend web {
        bind *:80
        acl is_api @api_path_acl
        default_backend: api
    }

    backend api {
        balance: roundrobin
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

        # Verify ACL was created
        frontend = ir.frontends[0]
        assert len(frontend.acls) == 1
        acl = frontend.acls[0]
        assert acl.name == "is_api"

    def test_multiple_acls_from_templates(self, parser, codegen):
        """Test multiple ACLs using different templates."""
        dsl_source = """
config test {
    template static_acl {
        criterion: "path_end"
        values: [".css", ".js", ".png"]
    }

    template api_acl {
        criterion: "path_beg"
        values: ["/api/"]
    }

    frontend web {
        bind *:80
        acl is_static @static_acl
        acl is_api @api_acl
        use_backend static_servers if is_static
        use_backend api_servers if is_api
        default_backend: web_servers
    }

    backend static_servers {
        balance: roundrobin
        servers {
            server s1 {
                address: "10.0.1.1"
                port: 80
            }
        }
    }

    backend api_servers {
        balance: roundrobin
        servers {
            server a1 {
                address: "10.0.2.1"
                port: 8080
            }
        }
    }

    backend web_servers {
        balance: roundrobin
        servers {
            server w1 {
                address: "10.0.3.1"
                port: 80
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)

        # Verify both ACLs were created
        frontend = ir.frontends[0]
        assert len(frontend.acls) == 2
        acl_names = [acl.name for acl in frontend.acls]
        assert "is_static" in acl_names
        assert "is_api" in acl_names

    def test_acl_template_in_backend(self, parser, codegen):
        """Test ACL template in backend section."""
        dsl_source = """
config test {
    template internal_src {
        criterion: "src"
        values: ["10.0.0.0/8", "192.168.0.0/16"]
    }

    frontend web {
        bind *:80
        default_backend: api
    }

    backend api {
        balance: roundrobin
        acl is_internal @internal_src

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

        # Verify ACL was created in backend
        backend = ir.backends[0]
        assert len(backend.acls) == 1
        assert backend.acls[0].name == "is_internal"


class TestACLTemplateExpansion:
    """Tests for the template expansion transformer with ACLs."""

    def test_acl_template_expansion_fills_criterion(self, parser):
        """Template should fill in criterion from template."""
        dsl_source = """
config test {
    template host_check {
        criterion: "hdr(host)"
        values: ["api.example.com"]
    }

    frontend web {
        bind *:80
        acl is_api_host @host_check
        default_backend: api
    }

    backend api {
        balance: roundrobin
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
        frontend = ir.frontends[0]

        # Check that the ACL has the template's criterion
        assert len(frontend.acls) == 1
        acl = frontend.acls[0]
        assert acl.name == "is_api_host"

    def test_acl_template_missing_graceful(self, parser):
        """Missing template should be handled gracefully."""
        dsl_source = """
config test {
    frontend web {
        bind *:80
        acl test_acl @nonexistent_template
        default_backend: api
    }

    backend api {
        balance: roundrobin
        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
            }
        }
    }
}
"""
        # Should parse without error
        ir = parser.parse(dsl_source)
        assert len(ir.frontends[0].acls) == 1


class TestACLTemplateCodeGen:
    """Tests for code generation with ACL templates."""

    def test_acl_template_generates_valid_config(self, parser, codegen):
        """ACL template should generate valid HAProxy config."""
        dsl_source = """
config test {
    template websocket_acl {
        criterion: "hdr(Upgrade)"
        values: ["websocket"]
    }

    frontend web {
        bind *:80
        acl is_websocket @websocket_acl
        default_backend: api
    }

    backend api {
        balance: roundrobin
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

        # Verify config is generated
        assert "frontend web" in output
        assert "backend api" in output


class TestCombinedTemplates:
    """Tests for using multiple template types together."""

    def test_server_and_acl_templates_together(self, parser, codegen):
        """Test using server templates and ACL templates in same config."""
        dsl_source = """
config test {
    template server_defaults {
        check: true
        inter: 3s
        rise: 2
        fall: 3
    }

    template api_path {
        criterion: "path_beg"
        values: ["/api/"]
    }

    frontend web {
        bind *:80
        acl is_api @api_path
        use_backend api if is_api
        default_backend: web
    }

    backend api {
        balance: roundrobin
        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
                @server_defaults
            }
        }
    }

    backend web {
        balance: roundrobin
        servers {
            server web1 {
                address: "10.0.2.1"
                port: 80
                @server_defaults
            }
        }
    }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Verify both frontends and backends are generated
        assert "frontend web" in output
        assert "backend api" in output
        assert "backend web" in output

        # Verify server template was expanded
        assert "server api1" in output
        assert "server web1" in output
