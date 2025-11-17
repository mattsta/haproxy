"""Tests for template expansion transformer."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.transformers.template_expander import TemplateExpander


class TestTemplateExpansion:
    """Test template expansion functionality."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_basic_template_expansion(self, parser):
        """Test basic template expansion."""
        source = """
        config test {
            template server_defaults {
                check: true
                inter: 3s
                rise: 5
                fall: 2
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        @server_defaults
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        ir = expander.expand()

        # Check server has template values
        server = ir.backends[0].servers[0]
        assert server.check is True
        assert server.check_interval == "3s"
        assert server.rise == 5
        assert server.fall == 2

    def test_template_with_override(self, parser):
        """Test template expansion with property override."""
        source = """
        config test {
            template defaults {
                check: true
                rise: 5
                fall: 2
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        rise: 3
                        @defaults
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        ir = expander.expand()

        # Explicit rise:3 should override template's rise:5
        server = ir.backends[0].servers[0]
        assert server.check is True  # From template
        assert server.rise == 3  # Overridden
        assert server.fall == 2  # From template

    def test_multiple_template_spreads(self, parser):
        """Test server with multiple template spreads."""
        source = """
        config test {
            template health_check {
                check: true
                inter: 3s
            }

            template weights {
                weight: 100
                rise: 5
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        @health_check
                        @weights
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        ir = expander.expand()

        # Should have properties from both templates
        server = ir.backends[0].servers[0]
        assert server.check is True  # From health_check
        assert server.check_interval == "3s"  # From health_check
        assert server.weight == 100  # From weights
        assert server.rise == 5  # From weights

    def test_server_without_template(self, parser):
        """Test server without template spread remains unchanged."""
        source = """
        config test {
            template defaults {
                check: true
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: false
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        ir = expander.expand()

        # Server should keep its explicit values
        server = ir.backends[0].servers[0]
        assert server.check is False
        assert server.check_interval is None

    def test_template_with_all_properties(self, parser):
        """Test template with all supported server properties."""
        source = """
        config test {
            template full {
                check: true
                inter: 3s
                rise: 5
                fall: 2
                weight: 100
                maxconn: 500
                ssl: true
                verify: "none"
                backup: true
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        @full
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        ir = expander.expand()

        server = ir.backends[0].servers[0]
        assert server.check is True
        assert server.check_interval == "3s"
        assert server.rise == 5
        assert server.fall == 2
        assert server.weight == 100
        assert server.maxconn == 500
        assert server.ssl is True
        assert server.ssl_verify == "none"
        assert server.backup is True

    def test_missing_template_reference(self, parser):
        """Test reference to non-existent template (should be gracefully handled)."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        @nonexistent
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        # Should not raise error, just skip the missing template
        ir = expander.expand()

        # Server should have default values
        server = ir.backends[0].servers[0]
        assert server.check is False
        assert server.rise == 2

    def test_multiple_servers_same_template(self, parser):
        """Test multiple servers using the same template."""
        source = """
        config test {
            template defaults {
                check: true
                rise: 5
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        @defaults
                    }
                    server web2 {
                        address: "10.0.1.2"
                        port: 8080
                        @defaults
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        ir = expander.expand()

        # Both servers should have template values
        backend = ir.backends[0]
        assert len(backend.servers) == 2
        for server in backend.servers:
            assert server.check is True
            assert server.rise == 5

    def test_multiple_backends(self, parser):
        """Test template expansion across multiple backends."""
        source = """
        config test {
            template defaults {
                check: true
                rise: 5
            }

            backend backend1 {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.1.1"
                        port: 8080
                        @defaults
                    }
                }
            }

            backend backend2 {
                balance: leastconn
                servers {
                    server s2 {
                        address: "10.0.2.1"
                        port: 8080
                        @defaults
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        expander = TemplateExpander(ir)
        ir = expander.expand()

        # Both backends should have servers with template values
        assert len(ir.backends) == 2
        for backend in ir.backends:
            server = backend.servers[0]
            assert server.check is True
            assert server.rise == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
