"""Test Listen section parsing and generation."""

import pytest

from haproxy_translator.parsers import DSLParser


class TestListenSection:
    """Test listen section with various configurations."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_basic_listen(self, parser):
        """Test basic listen section."""
        source = """
        config test {
            listen stats {
                bind *:8404
                mode: http
                balance: roundrobin

                servers {
                    server stats1 {
                        address: "127.0.0.1"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.listens) == 1
        listen = ir.listens[0]
        assert listen.name == "stats"
        assert len(listen.binds) == 1
        assert listen.mode.value == "http"
        assert listen.balance.value == "roundrobin"
        assert len(listen.servers) == 1
        assert listen.servers[0].name == "stats1"

    def test_listen_with_acls(self, parser):
        """Test listen section with ACLs."""
        source = """
        config test {
            listen web {
                bind *:80
                mode: http

                acl {
                    is_api path_beg "/api"
                    is_static path_beg "/static"
                }

                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.listens) == 1
        listen = ir.listens[0]
        assert len(listen.acls) == 2
        assert listen.acls[0].name == "is_api"
        assert listen.acls[1].name == "is_static"

    def test_listen_with_options(self, parser):
        """Test listen section with options."""
        source = """
        config test {
            listen app {
                bind *:8080
                mode: http
                balance: leastconn
                option: ["httplog", "forwardfor"]
                maxconn: 1000

                servers {
                    server app1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.listens) == 1
        listen = ir.listens[0]
        assert len(listen.options) == 2
        assert "httplog" in listen.options
        assert "forwardfor" in listen.options
        assert listen.metadata.get("maxconn") == 1000

    def test_listen_with_timeouts(self, parser):
        """Test listen section with timeouts."""
        source = """
        config test {
            listen app {
                bind *:8080
                timeout_client: 30s
                timeout_server: 30s
                timeout_connect: 5s

                servers {
                    server app1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert len(ir.listens) == 1
        listen = ir.listens[0]
        assert listen.metadata.get("timeout_client") == "30s"
        assert listen.metadata.get("timeout_server") == "30s"
        assert listen.metadata.get("timeout_connect") == "5s"
