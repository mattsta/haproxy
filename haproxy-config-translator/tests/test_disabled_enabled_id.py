"""Tests for disabled, enabled, and id directives (Phases 4I, 4J)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestFrontendDisabled:
    """Test disabled directive in frontend."""

    def test_frontend_disabled_true(self):
        """Test frontend with disabled: true."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                disabled: true

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.frontends[0].disabled
        assert "disabled" in output


class TestFrontendEnabled:
    """Test enabled directive in frontend."""

    def test_frontend_enabled_false(self):
        """Test frontend with enabled: false."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                enabled: false

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert not ir.frontends[0].enabled
        assert "disabled" in output


class TestFrontendId:
    """Test id directive in frontend."""

    def test_frontend_id(self):
        """Test frontend with id."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                id: 100

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.frontends[0].id == 100
        assert "id 100" in output


class TestBackendDisabledEnabledId:
    """Test disabled, enabled, and id directives in backend."""

    def test_backend_disabled(self):
        """Test backend with disabled: true."""
        config = """
        config test {
            backend app {
                mode: http
                disabled: true

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].disabled
        assert "disabled" in output

    def test_backend_enabled_false(self):
        """Test backend with enabled: false."""
        config = """
        config test {
            backend app {
                mode: http
                enabled: false

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert not ir.backends[0].enabled
        assert "disabled" in output

    def test_backend_id(self):
        """Test backend with id."""
        config = """
        config test {
            backend app {
                mode: http
                id: 200

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].id == 200
        assert "id 200" in output


class TestListenDisabledEnabledId:
    """Test disabled, enabled, and id directives in listen."""

    def test_listen_disabled(self):
        """Test listen with disabled: true."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                disabled: true

                servers {
                    server stats1 {
                        address: "127.0.0.1"
                        port: 9090
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.listens[0].disabled
        assert "disabled" in output

    def test_listen_id(self):
        """Test listen with id."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                id: 300

                servers {
                    server stats1 {
                        address: "127.0.0.1"
                        port: 9090
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.listens[0].id == 300
        assert "id 300" in output


class TestIntegration:
    """Test disabled, enabled, and id with other directives."""

    def test_frontend_with_all_metadata(self):
        """Test frontend with description, disabled, and id."""
        config = """
        config production {
            frontend api {
                bind *:443
                mode: http
                description: "API gateway for external requests"
                disabled: true
                id: 1000

                default_backend: api_backend
            }

            backend api_backend {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        frontend = ir.frontends[0]
        assert frontend.description == "API gateway for external requests"
        assert frontend.disabled
        assert frontend.id == 1000

        assert "description API gateway for external requests" in output
        assert "disabled" in output
        assert "id 1000" in output

    def test_complete_production_config(self):
        """Test complete config with all metadata directives."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http
                description: "Main web frontend"
                id: 100

                maxconn: 10000
                backlog: 2048

                stats {
                    enable: true
                    uri: "/stats"
                }

                default_backend: web_backend
            }

            backend web_backend {
                mode: http
                description: "Web server pool"
                id: 200

                balance: roundrobin

                maxconn: 5000

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server web2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                    }
                }
            }

            listen admin {
                bind *:9999
                mode: http
                description: "Admin interface"
                id: 300

                servers {
                    server admin1 {
                        address: "127.0.0.1"
                        port: 9000
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify frontend
        frontend = ir.frontends[0]
        assert frontend.description == "Main web frontend"
        assert frontend.id == 100
        assert frontend.maxconn == 10000
        assert frontend.stats_config is not None

        # Verify backend
        backend = ir.backends[0]
        assert backend.description == "Web server pool"
        assert backend.id == 200
        assert backend.maxconn == 5000

        # Verify listen
        listen = ir.listens[0]
        assert listen.description == "Admin interface"
        assert listen.id == 300

        # Verify output
        assert "frontend web" in output
        assert "description Main web frontend" in output
        assert "id 100" in output

        assert "backend web_backend" in output
        assert "description Web server pool" in output
        assert "id 200" in output

        assert "listen admin" in output
        assert "description Admin interface" in output
        assert "id 300" in output

    def test_maintenance_mode_with_disabled(self):
        """Test using disabled for maintenance mode."""
        config = """
        config maintenance {
            frontend web {
                bind *:80
                mode: http
                description: "Maintenance mode - frontend disabled"
                disabled: true

                default_backend: maintenance
            }

            backend maintenance {
                mode: http
                description: "Maintenance page backend"

                servers {
                    server maint1 {
                        address: "127.0.0.1"
                        port: 8888
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        frontend = ir.frontends[0]
        assert frontend.description == "Maintenance mode - frontend disabled"
        assert frontend.disabled

        assert "disabled" in output
        assert "Maintenance mode - frontend disabled" in output

    def test_unique_ids_across_sections(self):
        """Test unique IDs for different proxy sections."""
        config = """
        config test {
            frontend fe1 {
                bind *:80
                mode: http
                id: 1

                default_backend: be1
            }

            frontend fe2 {
                bind *:8080
                mode: http
                id: 2

                default_backend: be2
            }

            backend be1 {
                id: 10

                servers {
                    server srv1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }

            backend be2 {
                id: 20

                servers {
                    server srv2 {
                        address: "10.0.2.1"
                        port: 8080
                    }
                }
            }

            listen stats {
                bind *:9000
                mode: http
                id: 100

                servers {
                    server stats1 {
                        address: "127.0.0.1"
                        port: 9090
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify all IDs are set correctly
        assert ir.frontends[0].id == 1
        assert ir.frontends[1].id == 2
        assert ir.backends[0].id == 10
        assert ir.backends[1].id == 20
        assert ir.listens[0].id == 100

        # Verify output contains all IDs
        assert "id 1" in output
        assert "id 2" in output
        assert "id 10" in output
        assert "id 20" in output
        assert "id 100" in output
