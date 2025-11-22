"""Tests for log-steps directive implementation."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestLogSteps:
    """Test log-steps directive for transaction processing logging."""

    def test_log_steps_defaults_accept_close(self):
        """Test log-steps in defaults with accept and close steps."""
        config = """
        config test {
            defaults {
                mode: http
                log-steps: "accept,close"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.log_steps == "accept,close"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps accept,close" in output

    def test_log_steps_defaults_all(self):
        """Test log-steps in defaults with 'all' keyword."""
        config = """
        config test {
            defaults {
                mode: http
                log-steps: "all"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.log_steps == "all"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps all" in output

    def test_log_steps_frontend_complete_tracking(self):
        """Test log-steps in frontend with complete transaction tracking."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
            }

            frontend web {
                bind *:80
                log-steps: "accept,connect,request,response,close"
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "192.168.1.10"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.frontends[0].log_steps == "accept,connect,request,response,close"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps accept,connect,request,response,close" in output

    def test_log_steps_listen_with_log_format(self):
        """Test log-steps in listen section combined with log-format."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
            }

            listen web {
                bind *:80
                balance: roundrobin
                log-format: "%ci:%cp [%tr] %ft %b/%s"
                log-steps: "request,response"
                servers {
                    server s1 {
                        address: "192.168.1.10"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].log_steps == "request,response"
        assert ir.listens[0].log_format == "%ci:%cp [%tr] %ft %b/%s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps request,response" in output
        assert "log-format %ci:%cp [%tr] %ft %b/%s" in output

    def test_log_steps_defaults_inheritance(self):
        """Test log-steps inheritance from defaults to frontend."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
                log-steps: "accept,request,response,close"
            }

            frontend web {
                bind *:80
                default_backend: servers
            }

            backend servers {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "192.168.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.log_steps == "accept,request,response,close"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps accept,request,response,close" in output

    def test_log_steps_debugging_config(self):
        """Test log-steps for debugging with all steps enabled."""
        config = """
        config test {
            global {
                daemon: false
            }

            defaults {
                mode: http
                option: "httplog"
            }

            frontend debug {
                bind *:8080
                log-steps: "all"
                log-format: "%ci:%cp [%tr] %ft %b/%s %ST %B %tsc"
                default_backend: test_servers
            }

            backend test_servers {
                balance: roundrobin
                servers {
                    server test1 {
                        address: "127.0.0.1"
                        port: 9000
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.frontends[0].log_steps == "all"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps all" in output

    def test_log_steps_production_config(self):
        """Test log-steps in production configuration."""
        config = """
        config test {
            global {
                daemon: true
                maxconn: 50000
            }

            defaults {
                mode: http
                option: ["httplog", "forwardfor"]
                log-steps: "response,close"
            }

            frontend api {
                bind *:443
                log-format-sd: "%ci:%cp [%tr] %ft %b/%s %ST %B"
                log-steps: "request,response,close"
                default_backend: api_servers
            }

            backend api_servers {
                balance: leastconn
                servers {
                    server api1 {
                        address: "10.0.1.10"
                        port: 8443
                        check: true
                    }
                    server api2 {
                        address: "10.0.1.11"
                        port: 8443
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.log_steps == "response,close"
        assert ir.frontends[0].log_steps == "request,response,close"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        default_section = output.split("defaults")[1].split("frontend")[0]
        assert "log-steps response,close" in default_section
        frontend_section = output.split("frontend api")[1].split("backend")[0]
        assert "log-steps request,response,close" in frontend_section

    def test_log_steps_listen_minimal(self):
        """Test log-steps in listen section with minimal configuration."""
        config = """
        config test {
            global {
                daemon: true
            }

            defaults {
                mode: http
            }

            listen stats {
                bind *:8888
                log-steps: "request,close"
                servers {
                    server stats1 {
                        address: "127.0.0.1"
                        port: 8000
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens[0].log_steps == "request,close"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps request,close" in output

    def test_log_steps_accept_only(self):
        """Test log-steps with only accept step for connection tracking."""
        config = """
        config test {
            defaults {
                mode: tcp
                log-steps: "accept"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.log_steps == "accept"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "log-steps accept" in output

    def test_log_steps_with_error_log_format(self):
        """Test log-steps combined with error-log-format."""
        config = """
        config test {
            defaults {
                mode: http
                error-log-format: "%ci:%cp [%tr] %ST %B"
                log-steps: "response,close"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.error_log_format == "%ci:%cp [%tr] %ST %B"
        assert ir.defaults.log_steps == "response,close"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "error-log-format %ci:%cp [%tr] %ST %B" in output
        assert "log-steps response,close" in output
