"""Tests for guid directive (global unique identifier)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestFrontendGuid:
    """Test frontend guid directive."""

    def test_frontend_guid(self):
        """Test frontend guid directive parsing."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                guid: "frontend-web-12345"
                default_backend: app
            }

            backend app {
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert ir.frontends[0].guid == "frontend-web-12345"

    def test_frontend_guid_codegen(self):
        """Test frontend guid code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                guid: "frontend-web-12345"
                default_backend: app
            }

            backend app {
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "guid frontend-web-12345" in output
        assert "frontend web" in output

    def test_frontend_without_guid(self):
        """Test frontend without guid (should be None)."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }

            backend app {
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.frontends[0].guid is None


class TestBackendGuid:
    """Test backend guid directive."""

    def test_backend_guid(self):
        """Test backend guid directive parsing."""
        config = """
        config test {
            backend app {
                mode: http
                guid: "backend-app-67890"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].guid == "backend-app-67890"

    def test_backend_guid_codegen(self):
        """Test backend guid code generation."""
        config = """
        config test {
            backend app {
                mode: http
                guid: "backend-app-67890"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "guid backend-app-67890" in output
        assert "backend app" in output

    def test_backend_without_guid(self):
        """Test backend without guid (should be None)."""
        config = """
        config test {
            backend app {
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].guid is None


class TestGuidIntegration:
    """Integration tests for guid directive."""

    def test_multiple_frontends_with_guid(self):
        """Test multiple frontends with different guids."""
        config = """
        config test {
            frontend web1 {
                bind *:80
                mode: http
                guid: "web1-guid"
                default_backend: app1
            }

            frontend web2 {
                bind *:8080
                mode: http
                guid: "web2-guid"
                default_backend: app2
            }

            backend app1 {
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }

            backend app2 {
                servers {
                    server s2 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.frontends) == 2
        assert ir.frontends[0].guid == "web1-guid"
        assert ir.frontends[1].guid == "web2-guid"

    def test_multiple_backends_with_guid(self):
        """Test multiple backends with different guids."""
        config = """
        config test {
            backend app1 {
                mode: http
                guid: "app1-guid"
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }

            backend app2 {
                mode: http
                guid: "app2-guid"
                servers {
                    server s2 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].guid == "app1-guid"
        assert ir.backends[1].guid == "app2-guid"

    def test_frontend_and_backend_with_guid(self):
        """Test frontend and backend both with guid."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                guid: "frontend-guid-123"
                default_backend: app
            }

            backend app {
                mode: http
                guid: "backend-guid-456"
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.frontends[0].guid == "frontend-guid-123"
        assert ir.backends[0].guid == "backend-guid-456"
        assert "guid frontend-guid-123" in output
        assert "guid backend-guid-456" in output

    def test_guid_max_length(self):
        """Test guid with maximum allowed length (127 characters)."""
        # Generate a 127-character GUID
        long_guid = "a" * 127
        config = f"""
        config test {{
            backend app {{
                mode: http
                guid: "{long_guid}"
                servers {{
                    server app1 {{ address: "10.0.1.1" port: 8080 }}
                }}
            }}
        }}
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].guid == long_guid
        assert len(ir.backends[0].guid) == 127
