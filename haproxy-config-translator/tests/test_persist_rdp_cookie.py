"""Tests for persist rdp-cookie directive implementation."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPersistRdpCookie:
    """Test persist rdp-cookie directive for RDP cookie-based persistence."""

    def test_persist_rdp_cookie_defaults_default_cookie(self):
        """Test persist rdp-cookie in defaults with default msts cookie."""
        config = """
        config test {
            defaults {
                mode: tcp
                persist rdp-cookie
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.persist_rdp_cookie == ""  # Empty string = use default "msts"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "persist rdp-cookie" in output

    def test_persist_rdp_cookie_defaults_custom_cookie(self):
        """Test persist rdp-cookie in defaults with custom cookie name."""
        config = """
        config test {
            defaults {
                mode: tcp
                persist rdp-cookie("custom_rdp")
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.persist_rdp_cookie == "custom_rdp"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "persist rdp-cookie(custom_rdp)" in output

    def test_persist_rdp_cookie_backend_default(self):
        """Test persist rdp-cookie in backend with default cookie."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: tcp
            }

            backend rdp_servers {
                mode: tcp
                balance: rdp-cookie
                persist rdp-cookie
                servers {
                    server rdp1 {
                        address: "10.0.1.10"
                        port: 3389
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].persist_rdp_cookie == ""  # Empty string = default "msts"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        backend_section = output.split("backend rdp_servers")[1]
        assert "persist rdp-cookie" in backend_section

    def test_persist_rdp_cookie_backend_custom(self):
        """Test persist rdp-cookie in backend with custom cookie name."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: tcp
            }

            backend rdp_servers {
                mode: tcp
                balance: rdp-cookie
                persist rdp-cookie("terminal_cookie")
                servers {
                    server rdp1 {
                        address: "10.0.1.10"
                        port: 3389
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].persist_rdp_cookie == "terminal_cookie"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        backend_section = output.split("backend rdp_servers")[1]
        assert "persist rdp-cookie(terminal_cookie)" in backend_section

    def test_persist_rdp_cookie_listen_complete_example(self):
        """Test persist rdp-cookie in listen section with complete RDP config."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: tcp
            }

            listen tse_farm {
                bind *:3389
                mode: tcp
                balance: rdp-cookie
                persist rdp-cookie
                servers {
                    server srv1 {
                        address: "1.1.1.1"
                        port: 3389
                        check: true
                    }
                    server srv2 {
                        address: "1.1.1.2"
                        port: 3389
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].persist_rdp_cookie == ""  # Empty string = default cookie

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        listen_section = output.split("listen tse_farm")[1]
        assert "persist rdp-cookie" in listen_section
        assert "balance rdp-cookie" in listen_section

    def test_persist_rdp_cookie_listen_custom_cookie(self):
        """Test persist rdp-cookie in listen with custom cookie name."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: tcp
            }

            listen rdp_load_balancer {
                bind *:3389
                mode: tcp
                persist rdp-cookie("rdp_session")
                balance: rdp-cookie
                servers {
                    server terminal1 {
                        address: "192.168.1.100"
                        port: 3389
                    }
                    server terminal2 {
                        address: "192.168.1.101"
                        port: 3389
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].persist_rdp_cookie == "rdp_session"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "persist rdp-cookie(rdp_session)" in output

    def test_persist_rdp_cookie_production_config(self):
        """Test persist rdp-cookie in production RDP load balancer configuration."""
        config = """
        config test {
            global {
                daemon: true
                maxconn: 10000
            }

            defaults {
                mode: tcp
                timeout: {
                    connect: 10s
                    client: 30m
                    server: 30m
                }
            }

            listen rdp_cluster {
                bind *:3389
                mode: tcp
                balance: rdp-cookie
                persist rdp-cookie
                option: "tcplog"
                servers {
                    server rdp1 {
                        address: "10.0.1.10"
                        port: 3389
                        check: true
                        maxconn: 100
                    }
                    server rdp2 {
                        address: "10.0.1.11"
                        port: 3389
                        check: true
                        maxconn: 100
                    }
                    server rdp3 {
                        address: "10.0.1.12"
                        port: 3389
                        check: true
                        maxconn: 100
                        backup: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].persist_rdp_cookie == ""  # Empty string = default cookie

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "persist rdp-cookie" in output
        assert "balance rdp-cookie" in output
        assert "option tcplog" in output

    def test_persist_rdp_cookie_defaults_inheritance(self):
        """Test persist rdp-cookie inheritance from defaults to backend."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: tcp
                persist rdp-cookie("inherited_cookie")
            }

            backend rdp_backend {
                balance: rdp-cookie
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 3389
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.persist_rdp_cookie == "inherited_cookie"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        defaults_section = output.split("defaults")[1].split("backend")[0]
        assert "persist rdp-cookie(inherited_cookie)" in defaults_section

    def test_persist_rdp_cookie_multiple_backends(self):
        """Test persist rdp-cookie with multiple backend configurations."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: tcp
            }

            backend rdp_dev {
                persist rdp-cookie("dev_cookie")
                balance: rdp-cookie
                servers {
                    server dev1 {
                        address: "10.0.2.10"
                        port: 3389
                    }
                }
            }

            backend rdp_prod {
                persist rdp-cookie("prod_cookie")
                balance: rdp-cookie
                servers {
                    server prod1 {
                        address: "10.0.1.10"
                        port: 3389
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].persist_rdp_cookie == "dev_cookie"
        assert ir.backends[1].persist_rdp_cookie == "prod_cookie"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "persist rdp-cookie(dev_cookie)" in output
        assert "persist rdp-cookie(prod_cookie)" in output

    def test_persist_rdp_cookie_without_balance(self):
        """Test persist rdp-cookie without balance rdp-cookie (unusual but valid)."""
        config = """
        config test {
            defaults {
                mode: tcp
            }

            backend rdp_test {
                balance: roundrobin
                persist rdp-cookie
                servers {
                    server srv1 {
                        address: "10.0.1.10"
                        port: 3389
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].persist_rdp_cookie == ""  # Empty string = default cookie

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        backend_section = output.split("backend rdp_test")[1]
        assert "persist rdp-cookie" in backend_section
        assert "balance roundrobin" in backend_section
