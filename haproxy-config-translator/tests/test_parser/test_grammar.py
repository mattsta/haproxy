"""Test Lark grammar rules for HAProxy DSL."""

import pytest

from haproxy_translator.parsers.dsl_parser import DSLParser
from haproxy_translator.utils.errors import ParseError


@pytest.fixture
def parser():
    """Create DSL parser instance."""
    return DSLParser()


class TestBasicParsing:
    """Test basic parsing and grammar structure."""

    def test_minimal_config(self, parser):
        """Test parsing minimal valid configuration."""
        source = """
        config minimal {
            global {
                maxconn: 1000
            }
        }
        """
        ir = parser.parse(source)
        assert ir.name == "minimal"
        assert ir.global_config is not None
        assert ir.global_config.maxconn == 1000

    def test_config_with_all_sections(self, parser):
        """Test parsing config with all major sections."""
        source = """
        config full {
            global {
                maxconn: 2000
            }

            defaults {
                mode: http
                retries: 3
            }

            frontend web {
                bind *:80
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server s1 address: "127.0.0.1" port: 8080
                }
            }
        }
        """
        ir = parser.parse(source)
        assert ir.name == "full"
        assert ir.global_config is not None
        assert ir.defaults is not None
        assert len(ir.frontends) == 1
        assert len(ir.backends) == 1


class TestGlobalSection:
    """Test global section parsing."""

    def test_global_daemon(self, parser):
        """Test parsing daemon flag."""
        source = """
        config test {
            global {
                daemon: true
            }
        }
        """
        ir = parser.parse(source)
        assert ir.global_config.daemon is True

    def test_global_maxconn(self, parser):
        """Test parsing maxconn."""
        source = """
        config test {
            global {
                maxconn: 4096
            }
        }
        """
        ir = parser.parse(source)
        assert ir.global_config.maxconn == 4096

    def test_global_user_group(self, parser):
        """Test parsing user and group."""
        source = """
        config test {
            global {
                user: "haproxy"
                group: "haproxy"
            }
        }
        """
        ir = parser.parse(source)
        assert ir.global_config.user == "haproxy"
        assert ir.global_config.group == "haproxy"

    def test_global_log(self, parser):
        """Test parsing log target."""
        source = """
        config test {
            global {
                log "/dev/log" local0 info
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.global_config.log_targets) == 1
        log = ir.global_config.log_targets[0]
        assert log.address == "/dev/log"
        assert log.facility.value == "local0"
        assert log.level.value == "info"


class TestDefaultsSection:
    """Test defaults section parsing."""

    def test_defaults_mode(self, parser):
        """Test parsing mode."""
        source = """
        config test {
            defaults {
                mode: http
            }
        }
        """
        ir = parser.parse(source)
        assert ir.defaults.mode.value == "http"

    def test_defaults_retries(self, parser):
        """Test parsing retries."""
        source = """
        config test {
            defaults {
                retries: 5
            }
        }
        """
        ir = parser.parse(source)
        assert ir.defaults.retries == 5

    def test_defaults_timeouts(self, parser):
        """Test parsing timeout block."""
        source = """
        config test {
            defaults {
                timeout: {
                    connect: 5s
                    client: 50s
                    server: 50s
                    check: 10s
                }
            }
        }
        """
        ir = parser.parse(source)
        assert ir.defaults.timeout_connect == "5s"
        assert ir.defaults.timeout_client == "50s"
        assert ir.defaults.timeout_server == "50s"
        assert ir.defaults.timeout_check == "10s"

    def test_defaults_options(self, parser):
        """Test parsing options."""
        source = """
        config test {
            defaults {
                option: ["httplog", "dontlognull"]
            }
        }
        """
        ir = parser.parse(source)
        assert "httplog" in ir.defaults.options
        assert "dontlognull" in ir.defaults.options


class TestFrontendSection:
    """Test frontend section parsing."""

    def test_frontend_basic(self, parser):
        """Test basic frontend parsing."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: servers
            }
            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.frontends) == 1
        frontend = ir.frontends[0]
        assert frontend.name == "web"
        assert frontend.mode.value == "http"
        assert frontend.default_backend == "servers"

    def test_frontend_bind_simple(self, parser):
        """Test simple bind directive."""
        source = """
        config test {
            frontend web {
                bind *:80
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert len(frontend.binds) == 1
        assert frontend.binds[0].address == "*:80"

    def test_frontend_bind_with_ssl(self, parser):
        """Test bind with SSL options."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    alpn: ["h2", "http/1.1"]
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]
        assert bind.address == "*:443"
        assert bind.ssl is True
        assert bind.ssl_cert == "/etc/ssl/cert.pem"
        assert "h2" in bind.alpn

    def test_frontend_acl(self, parser):
        """Test ACL definition in frontend."""
        source = """
        config test {
            frontend web {
                acl is_api { path_beg "/api" }
                default_backend: servers
            }
            backend servers {
                balance: roundrobin
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        assert len(frontend.acls) == 1
        acl = frontend.acls[0]
        assert acl.name == "is_api"
        assert acl.criterion == "path_beg"


class TestBackendSection:
    """Test backend section parsing."""

    def test_backend_basic(self, parser):
        """Test basic backend parsing."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                mode: http
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.backends) == 1
        backend = ir.backends[0]
        assert backend.name == "servers"
        assert backend.balance.value == "roundrobin"
        assert backend.mode.value == "http"

    def test_backend_with_servers(self, parser):
        """Test backend with server definitions."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "127.0.0.1"
                        port: 8080
                        check: true
                        weight: 100
                    }
                    server s2 {
                        address: "127.0.0.2"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert len(backend.servers) == 2
        assert backend.servers[0].name == "s1"
        assert backend.servers[0].address == "127.0.0.1"
        assert backend.servers[0].port == 8080
        assert backend.servers[0].check is True
        assert backend.servers[0].weight == 100

    def test_backend_inline_server(self, parser):
        """Test inline server definition syntax."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server s1 address: "127.0.0.1" port: 8080 check: true
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert len(backend.servers) == 1
        assert backend.servers[0].name == "s1"
        assert backend.servers[0].address == "127.0.0.1"
        assert backend.servers[0].check is True

    def test_backend_health_check(self, parser):
        """Test health check configuration."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: status 200
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.health_check is not None
        assert backend.health_check.method == "GET"
        assert backend.health_check.uri == "/health"
        assert backend.health_check.expect_status == 200

    def test_backend_compression(self, parser):
        """Test compression configuration."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                compression {
                    algo: "gzip"
                    type: ["text/html", "text/plain", "application/json"]
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.compression is not None
        assert backend.compression.algo == "gzip"
        assert "text/html" in backend.compression.types
        assert "application/json" in backend.compression.types


class TestParsingErrors:
    """Test error handling in parsing."""

    def test_invalid_syntax(self, parser):
        """Test that invalid syntax raises ParseError."""
        source = """
        config test {
            invalid syntax here
        }
        """
        with pytest.raises(ParseError):
            parser.parse(source)

    def test_missing_braces(self, parser):
        """Test that missing braces raises ParseError."""
        source = """
        config test {
            global {
                maxconn: 1000
        }
        """
        with pytest.raises(ParseError):
            parser.parse(source)

    def test_empty_config(self, parser):
        """Test that completely empty config fails."""
        source = ""
        with pytest.raises(ParseError):
            parser.parse(source)


class TestComments:
    """Test comment handling."""

    def test_cpp_style_comments(self, parser):
        """Test C++ style comments."""
        source = """
        config test {
            // This is a comment
            global {
                maxconn: 1000  // Inline comment
            }
        }
        """
        ir = parser.parse(source)
        assert ir.name == "test"
        assert ir.global_config.maxconn == 1000

    def test_c_style_comments(self, parser):
        """Test C style block comments."""
        source = """
        config test {
            /* This is a
               multi-line comment */
            global {
                maxconn: 1000
            }
        }
        """
        ir = parser.parse(source)
        assert ir.name == "test"
        assert ir.global_config.maxconn == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
