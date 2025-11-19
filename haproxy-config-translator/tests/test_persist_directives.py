"""Tests for force-persist and ignore-persist directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestForcePersistParsing:
    """Test force-persist directive parsing."""

    def test_frontend_force_persist_with_condition(self):
        """Test frontend force-persist with condition."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                force-persist if is_management
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert len(ir.frontends[0].force_persist_rules) == 1
        rule = ir.frontends[0].force_persist_rules[0]
        assert rule.condition == "if is_management"

    def test_backend_force_persist(self):
        """Test backend force-persist directive."""
        config = """
        config test {
            backend app {
                mode: http
                force-persist if from_admin
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends[0].force_persist_rules) == 1
        rule = ir.backends[0].force_persist_rules[0]
        assert rule.condition == "if from_admin"

    def test_listen_force_persist(self):
        """Test listen force-persist directive."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                force-persist if special_user
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert len(ir.listens[0].force_persist_rules) == 1
        rule = ir.listens[0].force_persist_rules[0]
        assert rule.condition == "if special_user"


class TestIgnorePersistParsing:
    """Test ignore-persist directive parsing."""

    def test_frontend_ignore_persist_with_condition(self):
        """Test frontend ignore-persist with condition."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                ignore-persist if health_check
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert len(ir.frontends[0].ignore_persist_rules) == 1
        rule = ir.frontends[0].ignore_persist_rules[0]
        assert rule.condition == "if health_check"

    def test_backend_ignore_persist(self):
        """Test backend ignore-persist directive."""
        config = """
        config test {
            backend app {
                mode: http
                ignore-persist if no_session
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends[0].ignore_persist_rules) == 1
        rule = ir.backends[0].ignore_persist_rules[0]
        assert rule.condition == "if no_session"

    def test_listen_ignore_persist(self):
        """Test listen ignore-persist directive."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                ignore-persist if monitoring
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert len(ir.listens[0].ignore_persist_rules) == 1
        rule = ir.listens[0].ignore_persist_rules[0]
        assert rule.condition == "if monitoring"


class TestPersistCodegen:
    """Test persistence directives code generation."""

    def test_frontend_force_persist_codegen(self):
        """Test frontend force-persist code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                force-persist if from_vpn
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "force-persist if from_vpn" in output

    def test_backend_ignore_persist_codegen(self):
        """Test backend ignore-persist code generation."""
        config = """
        config test {
            backend app {
                mode: http
                ignore-persist if api_call
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend app" in output
        assert "ignore-persist if api_call" in output

    def test_listen_both_persist_rules_codegen(self):
        """Test listen with both force and ignore persist code generation."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                force-persist if admin_user
                ignore-persist if health_probe
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "listen stats" in output
        assert "force-persist if admin_user" in output
        assert "ignore-persist if health_probe" in output


class TestPersistIntegration:
    """Integration tests for persistence directives."""

    def test_multiple_force_persist_rules(self):
        """Test multiple force-persist rules in backend."""
        config = """
        config test {
            backend app {
                mode: http
                force-persist if condition1
                force-persist if condition2
                force-persist if condition3
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends[0].force_persist_rules) == 3
        assert ir.backends[0].force_persist_rules[0].condition == "if condition1"
        assert ir.backends[0].force_persist_rules[1].condition == "if condition2"
        assert ir.backends[0].force_persist_rules[2].condition == "if condition3"

    def test_multiple_ignore_persist_rules(self):
        """Test multiple ignore-persist rules in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                ignore-persist if check1
                ignore-persist if check2
            }

            backend app {
                mode: http
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].ignore_persist_rules) == 2
        assert ir.frontends[0].ignore_persist_rules[0].condition == "if check1"
        assert ir.frontends[0].ignore_persist_rules[1].condition == "if check2"

    def test_persist_with_other_directives(self):
        """Test persistence directives alongside other proxy directives."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: "httplog"
                force-persist if trusted_source
                ignore-persist if health_check
                default_backend: app
            }

            backend app {
                mode: http
                balance: roundrobin
                force-persist if admin_session
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 check: true }
                    server app2 { address: "10.0.1.2" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "force-persist if trusted_source" in output
        assert "ignore-persist if health_check" in output
        assert "backend app" in output
        assert "force-persist if admin_session" in output

    def test_complete_persistence_config(self):
        """Test complete configuration with persistence rules."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: "httplog"
                force-persist if from_trusted_network
                ignore-persist if monitoring_request
                default_backend: app
            }

            backend app {
                mode: http
                balance: leastconn
                force-persist if maintenance_mode
                ignore-persist if api_healthcheck
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 check: true }
                    server app2 { address: "10.0.1.2" port: 8080 check: true }
                }
            }

            listen stats {
                bind *:9000
                mode: http
                force-persist if stats_admin
                ignore-persist if stats_public
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify parsing
        assert len(ir.frontends[0].force_persist_rules) == 1
        assert len(ir.frontends[0].ignore_persist_rules) == 1
        assert len(ir.backends[0].force_persist_rules) == 1
        assert len(ir.backends[0].ignore_persist_rules) == 1
        assert len(ir.listens[0].force_persist_rules) == 1
        assert len(ir.listens[0].ignore_persist_rules) == 1

        # Verify codegen
        assert "force-persist if from_trusted_network" in output
        assert "ignore-persist if monitoring_request" in output
        assert "force-persist if maintenance_mode" in output
        assert "ignore-persist if api_healthcheck" in output
        assert "force-persist if stats_admin" in output
        assert "ignore-persist if stats_public" in output
