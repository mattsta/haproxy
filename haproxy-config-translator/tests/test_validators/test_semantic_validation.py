"""Tests for semantic validation."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.utils.errors import ValidationError
from haproxy_translator.validators.semantic import SemanticValidator


class TestSemanticValidation:
    """Test semantic validation functionality."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_valid_configuration(self, parser):
        """Test that valid configuration passes validation."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SemanticValidator(ir)

        # Should not raise any errors
        result = validator.validate()
        assert result == ir

    def test_invalid_backend_reference(self, parser):
        """Test error when frontend references non-existent backend."""
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: nonexistent
            }

            backend servers {
                balance: roundrobin
            }
        }
        """
        # Validation is now integrated into parser
        with pytest.raises(ValidationError, match="default_backend 'nonexistent' does not exist"):
            parser.parse(source)

    def test_invalid_use_backend_reference(self, parser):
        """Test error when use_backend references non-existent backend."""
        source = """
        config test {
            frontend web {
                bind *:80

                acl is_api {
                    path_beg "/api"
                }

                route {
                    to nonexistent if is_api
                    default: servers
                }
            }

            backend servers {
                balance: roundrobin
            }
        }
        """
        # Validation is now integrated into parser
        with pytest.raises(ValidationError, match="non-existent backend 'nonexistent'"):
            parser.parse(source)

    def test_duplicate_server_names(self, parser):
        """Test error when backend has duplicate server names."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                    server web1 {
                        address: "10.0.1.2"
                        port: 8080
                    }
                }
            }
        }
        """
        # Validation is now integrated into parser
        with pytest.raises(ValidationError, match="duplicate server names: web1"):
            parser.parse(source)

    def test_http_option_in_tcp_mode(self, parser):
        """Test error when HTTP option used in TCP mode."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: tcp
                option: ["httplog", "forwardfor"]
            }

            backend servers {
                balance: roundrobin
                mode: tcp
            }
        }
        """
        # Validation is now integrated into parser
        with pytest.raises(ValidationError, match="HTTP option 'httplog' used in TCP mode"):
            parser.parse(source)

    def test_invalid_health_check_method(self, parser):
        """Test error when health check has invalid HTTP method."""
        source = """
        config test {
            backend servers {
                balance: roundrobin

                health-check {
                    method: "INVALID"
                    uri: "/health"
                    expect: status 200
                }

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        # Validation is now integrated into parser
        with pytest.raises(ValidationError, match="invalid health check method 'INVALID'"):
            parser.parse(source)

    def test_invalid_health_check_status(self, parser):
        """Test error when health check expect status is out of range."""
        source = """
        config test {
            backend servers {
                balance: roundrobin

                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: status 999
                }

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        # Validation is now integrated into parser, so ValidationError is raised during parse
        with pytest.raises(ValidationError, match="invalid health check expect status 999"):
            parser.parse(source)

    def test_warning_for_backend_without_servers(self, parser):
        """Test warning when backend has no servers defined."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        validator = SemanticValidator(ir)

        # Should not raise error, but should generate warning
        validator.validate()
        assert len(validator.warnings) > 0
        assert any("no servers defined" in w for w in validator.warnings)

    def test_warning_for_frontend_without_binds(self, parser):
        """Test warning when frontend has no bind directives."""
        source = """
        config test {
            frontend web {
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
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
        assert len(validator.warnings) > 0
        assert any("no bind directives" in w for w in validator.warnings)

    def test_multiple_backends_validation(self, parser):
        """Test validation across multiple backends."""
        source = """
        config test {
            frontend web {
                bind *:80

                route {
                    to api if is_api
                    to cdn if is_static
                    default: web
                }
            }

            backend web {
                balance: roundrobin
                servers {
                    server w1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }

            backend api {
                balance: leastconn
                servers {
                    server a1 {
                        address: "10.0.2.1"
                        port: 8081
                    }
                }
            }

            backend cdn {
                balance: roundrobin
                servers {
                    server c1 {
                        address: "10.0.3.1"
                        port: 8082
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SemanticValidator(ir)

        # Should validate successfully
        result = validator.validate()
        assert result == ir

    def test_valid_health_check(self, parser):
        """Test that valid health check passes validation."""
        source = """
        config test {
            backend servers {
                balance: roundrobin

                health-check {
                    method: "POST"
                    uri: "/api/health"
                    expect: status 200
                }

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SemanticValidator(ir)

        # Should validate successfully
        result = validator.validate()
        assert result == ir

    def test_mode_compatibility_http(self, parser):
        """Test that HTTP mode allows HTTP-specific options."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: ["httplog", "forwardfor", "http-server-close"]
            }

            backend servers {
                balance: roundrobin
                mode: http
                option: ["httpchk", "forwardfor"]
            }
        }
        """
        ir = parser.parse(source)
        validator = SemanticValidator(ir)

        # Should validate successfully
        result = validator.validate()
        assert result == ir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
