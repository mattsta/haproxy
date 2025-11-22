"""Tests for quic-initial directive implementation for QUIC Initial packet processing."""


from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestQuicInitial:
    """Test quic-initial directive for QUIC Initial packet processing rules."""

    def test_quic_initial_basic_accept(self):
        """Test basic quic-initial accept rule."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "accept" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "accept"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial accept" in output

    def test_quic_initial_basic_reject(self):
        """Test basic quic-initial reject rule."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "reject" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "reject"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial reject" in output

    def test_quic_initial_conditional_if(self):
        """Test quic-initial rule with if condition."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "reject", condition: "if bad_source" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "reject"
        assert ir.frontends[0].quic_initial_rules[0].condition == "if bad_source"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial reject if bad_source" in output

    def test_quic_initial_conditional_unless(self):
        """Test quic-initial rule with unless condition."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "accept", condition: "unless blocked" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "accept"
        assert ir.frontends[0].quic_initial_rules[0].condition == "unless blocked"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial accept unless blocked" in output

    def test_quic_initial_track_rule(self):
        """Test quic-initial track-sc0 rule with track_key."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "track-sc0", track_key: "src", condition: "if authenticated" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "track-sc0"
        assert ir.frontends[0].quic_initial_rules[0].parameters["track_key"] == "src"
        assert ir.frontends[0].quic_initial_rules[0].condition == "if authenticated"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial track-sc0 src if authenticated" in output

    def test_quic_initial_set_var_rule(self):
        """Test quic-initial set-var rule."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "set-var", var_name: "txn.quic_version", var_value: "req.quic_version" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "set-var"
        assert ir.frontends[0].quic_initial_rules[0].parameters["var_name"] == "txn.quic_version"
        assert ir.frontends[0].quic_initial_rules[0].parameters["var_value"] == "req.quic_version"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial set-var(txn.quic_version) req.quic_version" in output

    def test_quic_initial_multiple_rules(self):
        """Test multiple quic-initial rules in single config."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "reject", condition: "if bad_source" },
                    { action: "track-sc0", track_key: "src" },
                    { action: "accept", condition: "if valid_quic" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 3
        assert ir.frontends[0].quic_initial_rules[0].action == "reject"
        assert ir.frontends[0].quic_initial_rules[1].action == "track-sc0"
        assert ir.frontends[0].quic_initial_rules[2].action == "accept"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial reject if bad_source" in output
        assert "quic-initial track-sc0 src" in output
        assert "quic-initial accept if valid_quic" in output

    def test_quic_initial_defaults_section(self):
        """Test quic-initial rules in defaults section."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
                quic_initial: [
                    { action: "reject", condition: "if blocked_network" }
                ]
            }

            frontend quic_frontend {
                bind *:443
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.defaults.quic_initial_rules) == 1
        assert ir.defaults.quic_initial_rules[0].action == "reject"
        assert ir.defaults.quic_initial_rules[0].condition == "if blocked_network"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        defaults_section = output.split("defaults")[1].split("frontend")[0]
        assert "quic-initial reject if blocked_network" in defaults_section

    def test_quic_initial_listen_section(self):
        """Test quic-initial rules in listen section."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
            }

            listen quic_listener {
                bind *:443
                quic_initial: [
                    { action: "accept", condition: "if trusted_source" }
                ]
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens[0].quic_initial_rules) == 1
        assert ir.listens[0].quic_initial_rules[0].action == "accept"
        assert ir.listens[0].quic_initial_rules[0].condition == "if trusted_source"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        listen_section = output.split("listen quic_listener")[1]
        assert "quic-initial accept if trusted_source" in listen_section

    def test_quic_initial_production_config(self):
        """Test quic-initial in production QUIC load balancer configuration."""
        config = """
        config test {
            global {
                daemon: true
                maxconn: 100000
            }

            defaults {
                mode: http
                timeout: {
                    connect: 5s
                    client: 60s
                    server: 60s
                }
            }

            frontend quic_lb {
                bind *:443
                mode: http

                quic_initial: [
                    { action: "reject", condition: "if { src -f /etc/haproxy/blocked_ips.lst }" },
                    { action: "track-sc0", track_key: "src", condition: "if !whitelisted" },
                    { action: "set-var", var_name: "txn.client_ip", var_value: "src" },
                    { action: "accept", condition: "if valid_client" }
                ]

                default_backend: quic_app_servers
            }

            backend quic_app_servers {
                balance: roundrobin
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8443
                        check: true
                        maxconn: 1000
                    }
                    server app2 {
                        address: "10.0.1.11"
                        port: 8443
                        check: true
                        maxconn: 1000
                    }
                    server app3 {
                        address: "10.0.1.12"
                        port: 8443
                        check: true
                        maxconn: 1000
                        backup: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 4
        assert ir.frontends[0].quic_initial_rules[0].action == "reject"
        assert ir.frontends[0].quic_initial_rules[1].action == "track-sc0"
        assert ir.frontends[0].quic_initial_rules[2].action == "set-var"
        assert ir.frontends[0].quic_initial_rules[3].action == "accept"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        frontend_section = output.split("frontend quic_lb")[1].split("backend")[0]
        assert "quic-initial reject if { src -f /etc/haproxy/blocked_ips.lst }" in frontend_section
        assert "quic-initial track-sc0 src if !whitelisted" in frontend_section
        assert "quic-initial set-var(txn.client_ip) src" in frontend_section
        assert "quic-initial accept if valid_client" in frontend_section

    def test_quic_initial_expect_proxy_action(self):
        """Test quic-initial expect-proxy action for proxy protocol."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "expect-proxy", condition: "if proxy_required" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "expect-proxy"
        assert ir.frontends[0].quic_initial_rules[0].condition == "if proxy_required"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial expect-proxy if proxy_required" in output

    def test_quic_initial_track_sc1_sc2(self):
        """Test quic-initial with track-sc1 and track-sc2 actions."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "track-sc1", track_key: "src" },
                    { action: "track-sc2", track_key: "req.hdr(X-Forwarded-For)", condition: "if has_xff" }
                ]
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 2
        assert ir.frontends[0].quic_initial_rules[0].action == "track-sc1"
        assert ir.frontends[0].quic_initial_rules[0].parameters["track_key"] == "src"
        assert ir.frontends[0].quic_initial_rules[1].action == "track-sc2"
        assert ir.frontends[0].quic_initial_rules[1].parameters["track_key"] == "req.hdr(X-Forwarded-For)"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial track-sc1 src" in output
        assert "quic-initial track-sc2 req.hdr(X-Forwarded-For) if has_xff" in output

    def test_quic_initial_combined_sections(self):
        """Test quic-initial rules across defaults, frontend, and listen sections."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
                quic_initial: [
                    { action: "reject", condition: "if global_blocked" }
                ]
            }

            frontend quic_frontend {
                bind *:443
                quic_initial: [
                    { action: "accept", condition: "if frontend_allowed" }
                ]
                default_backend: quic_servers
            }

            listen quic_listener {
                bind *:8443
                quic_initial: [
                    { action: "reject", condition: "if listener_blocked" }
                ]
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Check defaults
        assert len(ir.defaults.quic_initial_rules) == 1
        assert ir.defaults.quic_initial_rules[0].action == "reject"
        assert ir.defaults.quic_initial_rules[0].condition == "if global_blocked"

        # Check frontend
        assert len(ir.frontends[0].quic_initial_rules) == 1
        assert ir.frontends[0].quic_initial_rules[0].action == "accept"
        assert ir.frontends[0].quic_initial_rules[0].condition == "if frontend_allowed"

        # Check listen
        assert len(ir.listens[0].quic_initial_rules) == 1
        assert ir.listens[0].quic_initial_rules[0].action == "reject"
        assert ir.listens[0].quic_initial_rules[0].condition == "if listener_blocked"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "quic-initial reject if global_blocked" in output
        assert "quic-initial accept if frontend_allowed" in output
        assert "quic-initial reject if listener_blocked" in output

    def test_quic_initial_empty_list(self):
        """Test frontend with empty quic_initial list."""
        config = """
        config test {
            defaults {
                mode: http
            }

            frontend quic_frontend {
                bind *:443
                default_backend: quic_servers
            }

            backend quic_servers {
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 8443
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].quic_initial_rules) == 0

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        # Should not contain any quic-initial directive
        frontend_section = output.split("frontend quic_frontend")[1].split("backend")[0]
        assert "quic-initial" not in frontend_section
