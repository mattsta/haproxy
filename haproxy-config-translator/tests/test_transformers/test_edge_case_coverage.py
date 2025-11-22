"""Tests for edge case coverage in transformers."""

import pytest

from haproxy_translator.parsers import DSLParser


class TestVariableResolverEdgeCases:
    """Test edge cases in variable resolver."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_variable_in_global_maxconn(self, parser):
        """Test variable resolution in global maxconn."""
        source = '''
        config test {
            let max_connections = 10000
            global {
                maxconn: ${max_connections}
            }
        }
        '''
        ir = parser.parse(source)
        assert ir.global_config is not None
        assert ir.global_config.maxconn == 10000

    def test_weight_variable_resolution(self, parser):
        """Test weight variable resolution in servers."""
        source = '''
        config test {
            let server_weight = 100
            backend api {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                        weight: ${server_weight}
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.servers[0].weight == 100


class TestTemplateExpanderEdgeCases:
    """Test edge cases in template expander."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_backend_template_with_timeout_check(self, parser):
        """Test backend template with timeout_check."""
        source = '''
        config test {
            template backend_template {
                balance: "roundrobin"
                timeout_check: "5s"
            }

            backend api {
                @backend_template
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.timeout_check == "5s"

    def test_backend_template_with_options_single(self, parser):
        """Test backend template with single option value."""
        source = '''
        config test {
            template backend_template {
                balance: "roundrobin"
                option: "httpchk"
            }

            backend api {
                @backend_template
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert "httpchk" in backend.options


class TestHealthCheckTemplateEdgeCases:
    """Test edge cases in health check templates."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_health_check_with_template_spread(self, parser):
        """Test health check with template spread."""
        source = '''
        config test {
            template health_template {
                method: "GET"
                uri: "/health"
            }

            backend api {
                balance: roundrobin
                health-check @health_template
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert backend.health_check is not None
        assert backend.health_check.method == "GET"
        assert backend.health_check.uri == "/health"


class TestACLTemplateEdgeCases:
    """Test edge cases in ACL templates."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_acl_template_spread(self, parser):
        """Test ACL template spread."""
        source = '''
        config test {
            template acl_block_ips {
                criterion: "src"
                pattern: "192.168.1.0/24"
            }

            frontend web {
                bind *:80
                mode: http
                acl blocked_ips @acl_block_ips
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        blocked_acls = [a for a in frontend.acls if a.name == "blocked_ips"]
        assert len(blocked_acls) == 1
        assert blocked_acls[0].criterion == "src"


class TestForLoopVariables:
    """Test for loop variable handling."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_for_loop_with_weight_variable(self, parser):
        """Test for loop with weight variable."""
        source = '''
        config test {
            let base_weight = 10
            backend api {
                balance: roundrobin
                servers {
                    for i in [1..3] {
                        server "web${i}" {
                            address: "10.0.0.${i}"
                            port: 8080
                            weight: ${base_weight}
                        }
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert len(backend.servers) == 3
        for server in backend.servers:
            assert server.weight == 10

    def test_for_loop_with_different_ports(self, parser):
        """Test for loop generating servers with different ports."""
        source = '''
        config test {
            backend api {
                balance: roundrobin
                servers {
                    for i in [1..3] {
                        server "web${i}" {
                            address: "10.0.0.${i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        backend = ir.backends[0]
        assert len(backend.servers) == 3
        assert backend.servers[0].name == "web1"
        assert backend.servers[1].name == "web2"
        assert backend.servers[2].name == "web3"


class TestListenSectionCoverage:
    """Test listen section coverage."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_listen_with_quic_initial(self, parser):
        """Test listen section with quic-initial rules."""
        source = '''
        config test {
            listen quic_listen {
                bind *:443
                mode: http
                balance: roundrobin
                quic_initial: [
                    { action: "accept" }
                ]
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert len(listen.quic_initial_rules) >= 1

    def test_listen_with_log_format(self, parser):
        """Test listen section with log-format."""
        source = '''
        config test {
            listen api {
                bind *:8080
                mode: http
                balance: roundrobin
                log-format: "%ci:%cp [%t] %ft %b/%s %Tq/%Tw/%Tc/%Tr/%Tt"
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 9000
                    }
                }
            }
        }
        '''
        ir = parser.parse(source)
        listen = ir.listens[0]
        assert listen.log_format is not None
        assert "%ci:" in listen.log_format


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
