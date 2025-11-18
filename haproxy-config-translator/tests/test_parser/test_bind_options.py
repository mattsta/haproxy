"""Test bind directive options."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestBindOptions:
    """Test bind directive option support."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_bind_accept_proxy(self, parser, codegen):
        """Test accept-proxy bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 accept-proxy true
                default_backend: api
            }
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        # Verify bind has accept-proxy option
        assert "accept-proxy" in bind.options
        assert bind.options["accept-proxy"] is True

        output = codegen.generate(ir)
        assert "bind *:80 accept-proxy" in output

    def test_bind_transparent(self, parser, codegen):
        """Test transparent bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 transparent true
                default_backend: api
            }
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert "transparent" in bind.options
        assert bind.options["transparent"] is True

        output = codegen.generate(ir)
        assert "bind *:80 transparent" in output

    def test_bind_defer_accept(self, parser, codegen):
        """Test defer-accept bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 defer-accept true
                default_backend: api
            }
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert "defer-accept" in bind.options
        assert bind.options["defer-accept"] is True

        output = codegen.generate(ir)
        assert "bind *:80 defer-accept" in output

    def test_bind_name(self, parser, codegen):
        """Test name bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 name "web_frontend"
                default_backend: api
            }
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert "name" in bind.options
        assert bind.options["name"] == "web_frontend"

        output = codegen.generate(ir)
        assert 'bind *:80 name "web_frontend"' in output or "bind *:80 name web_frontend" in output

    def test_bind_maxconn(self, parser, codegen):
        """Test maxconn bind option."""
        source = """
        config test {
            frontend web {
                bind *:80 maxconn 5000
                default_backend: api
            }
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert "maxconn" in bind.options
        assert bind.options["maxconn"] == 5000

        output = codegen.generate(ir)
        assert "bind *:80 maxconn 5000" in output

    def test_bind_multiple_options(self, parser, codegen):
        """Test multiple bind options together."""
        source = """
        config test {
            frontend web {
                bind *:80 accept-proxy true defer-accept true maxconn 5000
                default_backend: api
            }
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.options["accept-proxy"] is True
        assert bind.options["defer-accept"] is True
        assert bind.options["maxconn"] == 5000

        output = codegen.generate(ir)
        assert "bind *:80" in output
        assert "accept-proxy" in output
        assert "defer-accept" in output
        assert "maxconn 5000" in output

    def test_bind_with_ssl_and_options(self, parser, codegen):
        """Test bind with both SSL and other options."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    alpn: ["h2", "http/1.1"]
                } accept-proxy true
                default_backend: api
            }
            backend api {
                balance: roundrobin
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        # Verify SSL
        assert bind.ssl is True
        assert bind.ssl_cert == "/etc/ssl/cert.pem"
        assert bind.alpn == ["h2", "http/1.1"]

        # Verify other options
        assert "accept-proxy" in bind.options
        assert bind.options["accept-proxy"] is True

        output = codegen.generate(ir)
        assert "bind *:443 ssl" in output
        assert "crt /etc/ssl/cert.pem" in output
        assert "alpn h2,http/1.1" in output
        assert "accept-proxy" in output

    def test_production_bind_with_all_options(self, parser, codegen):
        """Test production bind configuration with all options."""
        source = """
        config production {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/production.pem"
                    alpn: ["h2", "http/1.1"]
                    ssl-min-ver: "TLSv1.2"
                    ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
                } accept-proxy true defer-accept true maxconn 10000 name "production_https"

                default_backend: api
            }

            backend api {
                balance: leastconn
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        # Verify SSL options
        assert bind.ssl is True
        assert bind.ssl_cert == "/etc/ssl/production.pem"
        assert bind.alpn == ["h2", "http/1.1"]
        assert "ssl-min-ver" in bind.options
        assert bind.options["ssl-min-ver"] == "TLSv1.2"
        assert "ciphers" in bind.options

        # Verify bind options
        assert bind.options["accept-proxy"] is True
        assert bind.options["defer-accept"] is True
        assert bind.options["maxconn"] == 10000
        assert bind.options["name"] == "production_https"

        output = codegen.generate(ir)
        assert "bind *:443 ssl" in output
        assert "crt /etc/ssl/production.pem" in output
        assert "alpn h2,http/1.1" in output
        assert "accept-proxy" in output
        assert "defer-accept" in output
        assert "maxconn 10000" in output
        assert "production_https" in output
