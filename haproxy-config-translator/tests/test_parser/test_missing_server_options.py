"""Test missing server options for 100% coverage."""

from haproxy_translator.parsers import DSLParser


class TestMissingServerOptions:
    """Test server options that weren't covered in other tests."""

    def test_server_send_proxy_v2(self):
        """Test send-proxy-v2 server option."""
        config = """
        config test {
            frontend app {
                bind *:80
                default_backend servers
            }

            backend servers {
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
        result = parser.parse(config)
        assert result.backends
        assert result.backends[0].servers
        server = result.backends[0].servers[0]
        assert server.send_proxy_v2 is True

    def test_server_slowstart(self):
        """Test slowstart server option."""
        config = """
        config test {
            frontend app {
                bind *:80
                default_backend servers
            }

            backend servers {
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
        result = parser.parse(config)
        assert result.backends
        assert result.backends[0].servers
        server = result.backends[0].servers[0]
        assert server.slowstart == "30s"  # Converted to string by transformer

    def test_server_send_proxy_v2_and_slowstart(self):
        """Test both send-proxy-v2 and slowstart together."""
        config = """
        config test {
            frontend app {
                bind *:80
                default_backend servers
            }

            backend servers {
                servers {
                    server srv1 {
                        address: "192.168.1.10"
                        port: 8080
                        send-proxy-v2: true
                        slowstart: 1m
                        weight: 100
                        maxconn: 500
                    }
                }
            }
        }
        """

        parser = DSLParser()
        result = parser.parse(config)
        assert result.backends
        assert result.backends[0].servers
        server = result.backends[0].servers[0]
        assert server.send_proxy_v2 is True
        assert server.slowstart == "1m"  # Converted to string by transformer
        assert server.weight == 100
        assert server.maxconn == 500
