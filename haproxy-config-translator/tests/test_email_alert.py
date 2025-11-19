"""Tests for email-alert directive (email alerting configuration)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestEmailAlertParsing:
    """Test email-alert directive parsing."""

    def test_frontend_email_alert_basic(self):
        """Test frontend email-alert with basic configuration."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                email-alert {
                    level: alert
                    mailers: mymailers
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert ir.frontends[0].email_alert is not None
        assert ir.frontends[0].email_alert.level == "alert"
        assert ir.frontends[0].email_alert.mailers == "mymailers"

    def test_backend_email_alert_full(self):
        """Test backend email-alert with all properties."""
        config = """
        config test {
            backend app {
                mode: http
                email-alert {
                    level: warning
                    mailers: alertmailers
                    from: "haproxy@example.com"
                    to: "admin@example.com"
                    myhostname: "lb1.example.com"
                }
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].email_alert is not None
        assert ir.backends[0].email_alert.level == "warning"
        assert ir.backends[0].email_alert.mailers == "alertmailers"
        assert ir.backends[0].email_alert.from_email == "haproxy@example.com"
        assert ir.backends[0].email_alert.to_email == "admin@example.com"
        assert ir.backends[0].email_alert.myhostname == "lb1.example.com"

    def test_listen_email_alert(self):
        """Test listen email-alert directive."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                email-alert {
                    level: notice
                    mailers: statsmailers
                }
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert ir.listens[0].email_alert is not None
        assert ir.listens[0].email_alert.level == "notice"
        assert ir.listens[0].email_alert.mailers == "statsmailers"

    def test_defaults_email_alert(self):
        """Test defaults email-alert directive."""
        config = """
        config test {
            defaults {
                mode: http
                email-alert {
                    level: alert
                    mailers: defaultmailers
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults is not None
        assert ir.defaults.email_alert is not None
        assert ir.defaults.email_alert.level == "alert"
        assert ir.defaults.email_alert.mailers == "defaultmailers"

    def test_email_alert_minimal(self):
        """Test email-alert with minimal configuration."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                email-alert {
                    mailers: mymailers
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.frontends[0].email_alert is not None
        assert ir.frontends[0].email_alert.mailers == "mymailers"
        assert ir.frontends[0].email_alert.level is None


class TestEmailAlertCodegen:
    """Test email-alert code generation."""

    def test_frontend_email_alert_codegen(self):
        """Test frontend email-alert code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                email-alert {
                    level: alert
                    mailers: mymailers
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "email-alert level alert" in output
        assert "email-alert mailers mymailers" in output

    def test_backend_email_alert_full_codegen(self):
        """Test backend email-alert with all properties code generation."""
        config = """
        config test {
            backend app {
                mode: http
                email-alert {
                    level: warning
                    mailers: alertmailers
                    from: "haproxy@example.com"
                    to: "admin@example.com"
                    myhostname: "lb1.example.com"
                }
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
        assert "email-alert level warning" in output
        assert "email-alert mailers alertmailers" in output
        assert "email-alert from haproxy@example.com" in output
        assert "email-alert to admin@example.com" in output
        assert "email-alert myhostname lb1.example.com" in output

    def test_listen_email_alert_codegen(self):
        """Test listen email-alert code generation."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                email-alert {
                    level: notice
                    mailers: statsmailers
                }
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
        assert "email-alert level notice" in output
        assert "email-alert mailers statsmailers" in output

    def test_defaults_email_alert_codegen(self):
        """Test defaults email-alert code generation."""
        config = """
        config test {
            defaults {
                mode: http
                email-alert {
                    level: alert
                    mailers: defaultmailers
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "defaults" in output
        assert "email-alert level alert" in output
        assert "email-alert mailers defaultmailers" in output


class TestEmailAlertIntegration:
    """Integration tests for email-alert directive."""

    def test_email_alert_with_other_directives(self):
        """Test email-alert alongside other frontend directives."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: "httplog"
                email-alert {
                    level: alert
                    mailers: mymailers
                    from: "haproxy@example.com"
                }
                default_backend: app
            }

            backend app {
                mode: http
                email-alert {
                    level: warning
                    mailers: backendmailers
                }
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "email-alert level alert" in output
        assert "email-alert mailers mymailers" in output
        assert "email-alert from haproxy@example.com" in output
        assert "backend app" in output
        assert "email-alert level warning" in output
        assert "email-alert mailers backendmailers" in output

    def test_email_alert_various_levels(self):
        """Test email-alert with various alert levels."""
        levels = ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]

        for level in levels:
            config = f"""
            config test {{
                frontend web {{
                    bind *:80
                    mode: http
                    email-alert {{
                        level: {level}
                        mailers: mymailers
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.frontends[0].email_alert.level == level

    def test_multiple_proxies_with_email_alert(self):
        """Test multiple proxies with email-alert configuration."""
        config = """
        config test {
            defaults {
                mode: http
                email-alert {
                    mailers: defaultmailers
                }
            }

            frontend web {
                bind *:80
                mode: http
                email-alert {
                    level: alert
                    mailers: webmailers
                }
                default_backend: app
            }

            backend app {
                mode: http
                email-alert {
                    level: warning
                    mailers: appmailers
                }
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }

            listen stats {
                bind *:9000
                mode: http
                email-alert {
                    level: notice
                    mailers: statsmailers
                }
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

        assert "defaults" in output
        assert ir.defaults.email_alert is not None
        assert ir.frontends[0].email_alert is not None
        assert ir.backends[0].email_alert is not None
        assert ir.listens[0].email_alert is not None

    def test_email_alert_partial_config(self):
        """Test email-alert with partial configuration."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                email-alert {
                    mailers: mymailers
                    from: "lb@example.com"
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "email-alert mailers mymailers" in output
        assert "email-alert from lb@example.com" in output
        assert "email-alert level" not in output  # level not set
