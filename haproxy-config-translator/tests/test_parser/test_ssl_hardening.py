"""Test SSL/TLS hardening features."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestSSLHardening:
    """Test SSL/TLS hardening features."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_bind_ssl_min_max_ver(self, parser, codegen):
        """Test bind with SSL version constraints."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    ssl-min-ver: "TLSv1.2"
                    ssl-max-ver: "TLSv1.3"
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.ssl is True
        assert bind.ssl_cert == "/etc/ssl/cert.pem"
        assert bind.options["ssl-min-ver"] == "TLSv1.2"
        assert bind.options["ssl-max-ver"] == "TLSv1.3"

        # Test code generation
        output = codegen.generate(ir)
        assert "bind *:443 ssl crt /etc/ssl/cert.pem" in output
        assert "ssl-min-ver TLSv1.2" in output
        assert "ssl-max-ver TLSv1.3" in output

    def test_bind_ssl_ciphers(self, parser, codegen):
        """Test bind with cipher suite configuration."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.options["ciphers"] == "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"

        # Test code generation
        output = codegen.generate(ir)
        assert "ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384" in output

    def test_bind_ssl_ciphersuites(self, parser, codegen):
        """Test bind with TLS 1.3 cipher suites."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    ciphersuites: "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.options["ciphersuites"] == "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"

        # Test code generation
        output = codegen.generate(ir)
        assert "ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384" in output

    def test_bind_ssl_curves(self, parser, codegen):
        """Test bind with elliptic curves configuration."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    curves: "secp384r1:prime256v1"
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.options["curves"] == "secp384r1:prime256v1"

        # Test code generation
        output = codegen.generate(ir)
        assert "curves secp384r1:prime256v1" in output

    def test_bind_ssl_client_verification(self, parser, codegen):
        """Test bind with client certificate verification."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    verify: "required"
                    ca-file: "/etc/ssl/ca.pem"
                    crl-file: "/etc/ssl/crl.pem"
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.options["verify"] == "required"
        assert bind.options["ca-file"] == "/etc/ssl/ca.pem"
        assert bind.options["crl-file"] == "/etc/ssl/crl.pem"

        # Test code generation
        output = codegen.generate(ir)
        assert "verify required" in output
        assert "ca-file /etc/ssl/ca.pem" in output
        assert "crl-file /etc/ssl/crl.pem" in output

    def test_bind_ssl_no_old_versions(self, parser, codegen):
        """Test bind with disabled old SSL/TLS versions."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    no-sslv3: true
                    no-tlsv10: true
                    no-tlsv11: true
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.options["no-sslv3"] is True
        assert bind.options["no-tlsv10"] is True
        assert bind.options["no-tlsv11"] is True

        # Test code generation
        output = codegen.generate(ir)
        assert "no-sslv3" in output
        assert "no-tlsv10" in output
        assert "no-tlsv11" in output

    def test_bind_ssl_comprehensive_hardening(self, parser, codegen):
        """Test bind with comprehensive SSL hardening configuration."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    alpn: ["h2", "http/1.1"]
                    ssl-min-ver: "TLSv1.2"
                    ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
                    curves: "secp384r1:prime256v1"
                    no-sslv3: true
                    no-tlsv10: true
                    no-tlsv11: true
                }
            }
        }
        """
        ir = parser.parse(source)
        frontend = ir.frontends[0]
        bind = frontend.binds[0]

        assert bind.ssl is True
        assert bind.ssl_cert == "/etc/ssl/cert.pem"
        assert bind.alpn == ["h2", "http/1.1"]
        assert bind.options["ssl-min-ver"] == "TLSv1.2"
        assert bind.options["ciphers"] == "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
        assert bind.options["curves"] == "secp384r1:prime256v1"
        assert bind.options["no-sslv3"] is True
        assert bind.options["no-tlsv10"] is True
        assert bind.options["no-tlsv11"] is True

        # Test code generation
        output = codegen.generate(ir)
        assert "bind *:443 ssl" in output
        assert "crt /etc/ssl/cert.pem" in output
        assert "alpn h2,http/1.1" in output
        assert "ssl-min-ver TLSv1.2" in output
        assert "ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384" in output
        assert "curves secp384r1:prime256v1" in output
        assert "no-sslv3" in output
        assert "no-tlsv10" in output
        assert "no-tlsv11" in output

    def test_global_ssl_default_bind_ciphers(self, parser, codegen):
        """Test global SSL default bind ciphers."""
        source = """
        config test {
            global {
                daemon: true
                ssl-default-bind-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
            }
        }
        """
        ir = parser.parse(source)
        assert ir.global_config.ssl_default_bind_ciphers == "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"

        # Test code generation
        output = codegen.generate(ir)
        assert "ssl-default-bind-ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384" in output

    def test_global_ssl_default_bind_options(self, parser, codegen):
        """Test global SSL default bind options."""
        source = """
        config test {
            global {
                daemon: true
                ssl-default-bind-options: ["no-sslv3", "no-tlsv10", "no-tlsv11"]
            }
        }
        """
        ir = parser.parse(source)
        assert ir.global_config.ssl_default_bind_options == ["no-sslv3", "no-tlsv10", "no-tlsv11"]

        # Test code generation
        output = codegen.generate(ir)
        assert "ssl-default-bind-options no-sslv3" in output
        assert "ssl-default-bind-options no-tlsv10" in output
        assert "ssl-default-bind-options no-tlsv11" in output

    def test_global_ssl_comprehensive(self, parser, codegen):
        """Test comprehensive global SSL configuration."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 4096
                ssl-default-bind-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
                ssl-default-bind-options: ["no-sslv3", "no-tlsv10", "no-tlsv11", "no-tls-tickets"]
            }

            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                    alpn: ["h2", "http/1.1"]
                }
            }
        }
        """
        ir = parser.parse(source)

        # Verify global config
        assert ir.global_config.ssl_default_bind_ciphers == "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
        assert ir.global_config.ssl_default_bind_options == ["no-sslv3", "no-tlsv10", "no-tlsv11", "no-tls-tickets"]

        # Verify frontend bind
        bind = ir.frontends[0].binds[0]
        assert bind.ssl is True
        assert bind.ssl_cert == "/etc/ssl/cert.pem"
        assert bind.alpn == ["h2", "http/1.1"]

        # Test code generation
        output = codegen.generate(ir)

        # Global SSL
        assert "ssl-default-bind-ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384" in output
        assert "ssl-default-bind-options no-sslv3" in output
        assert "ssl-default-bind-options no-tlsv10" in output
        assert "ssl-default-bind-options no-tlsv11" in output
        assert "ssl-default-bind-options no-tls-tickets" in output

        # Bind SSL
        assert "bind *:443 ssl crt /etc/ssl/cert.pem alpn h2,http/1.1" in output
