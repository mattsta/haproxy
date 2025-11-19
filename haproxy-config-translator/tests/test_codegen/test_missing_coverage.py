"""Test codegen edge cases to reach 100% coverage."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestCodegenMissingCoverage:
    """Test codegen paths that weren't covered in other tests."""

    def test_server_send_proxy_v2_codegen(self):
        """Test send-proxy-v2 generates correctly."""
        config = """
        config test {
            backend app {
                servers {
                    server srv1 {
                        address: "192.168.1.10"
                        port: 8080
                        send-proxy-v2: true
                    }
                }
            }
        }
        """

        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "send-proxy-v2" in output

    def test_server_slowstart_codegen(self):
        """Test slowstart generates correctly."""
        config = """
        config test {
            backend app {
                servers {
                    server srv1 {
                        address: "192.168.1.10"
                        port: 8080
                        slowstart: 30s
                    }
                }
            }
        }
        """

        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "slowstart 30s" in output

    def test_defaults_timeout_tunnel(self):
        """Test defaults timeout tunnel option."""
        config = """
        config test {
            defaults {
                timeout: {
                    connect: 5s
                    client: 30s
                    server: 30s
                    tunnel: 1h
                }
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

        assert "timeout tunnel 1h" in output

    def test_defaults_timeout_tarpit(self):
        """Test defaults timeout tarpit option."""
        config = """
        config test {
            defaults {
                timeout: {
                    connect: 5s
                    client: 30s
                    server: 30s
                    tarpit: 10s
                }
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

        assert "timeout tarpit 10s" in output
