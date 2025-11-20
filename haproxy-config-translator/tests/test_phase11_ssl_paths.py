"""Tests for Phase 11 batch 1 - SSL & Paths directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase11SSLPaths:
    """Test Phase 11 batch 1 SSL & Paths directives."""

    def test_ca_base(self):
        """Test ca-base directive - base directory for CA certificates."""
        config = """
        config test {
            global {
                ca-base: "/etc/ssl/certs"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ca_base == "/etc/ssl/certs"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ca-base /etc/ssl/certs" in output

    def test_ca_base_custom_path(self):
        """Test ca-base with custom path."""
        config = """
        config test {
            global {
                ca-base: "/opt/haproxy/ca"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ca_base == "/opt/haproxy/ca"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ca-base /opt/haproxy/ca" in output

    def test_crt_base(self):
        """Test crt-base directive - base directory for certificate files."""
        config = """
        config test {
            global {
                crt-base: "/etc/ssl/private"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.crt_base == "/etc/ssl/private"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "crt-base /etc/ssl/private" in output

    def test_crt_base_custom_path(self):
        """Test crt-base with custom path."""
        config = """
        config test {
            global {
                crt-base: "/opt/haproxy/certs"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.crt_base == "/opt/haproxy/certs"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "crt-base /opt/haproxy/certs" in output

    def test_key_base(self):
        """Test key-base directive - base directory for key files."""
        config = """
        config test {
            global {
                key-base: "/etc/ssl/keys"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.key_base == "/etc/ssl/keys"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "key-base /etc/ssl/keys" in output

    def test_key_base_custom_path(self):
        """Test key-base with custom path."""
        config = """
        config test {
            global {
                key-base: "/opt/haproxy/keys"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.key_base == "/opt/haproxy/keys"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "key-base /opt/haproxy/keys" in output

    def test_all_ssl_paths(self):
        """Test all SSL path directives together."""
        config = """
        config test {
            global {
                ca-base: "/etc/ssl/certs"
                crt-base: "/etc/ssl/private"
                key-base: "/etc/ssl/keys"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ca_base == "/etc/ssl/certs"
        assert ir.global_config.crt_base == "/etc/ssl/private"
        assert ir.global_config.key_base == "/etc/ssl/keys"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ca-base /etc/ssl/certs" in output
        assert "crt-base /etc/ssl/private" in output
        assert "key-base /etc/ssl/keys" in output

    def test_ssl_dh_param_file(self):
        """Test ssl-dh-param-file directive - Diffie-Hellman parameters."""
        config = """
        config test {
            global {
                ssl-dh-param-file: "/etc/ssl/dhparam.pem"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_dh_param_file == "/etc/ssl/dhparam.pem"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-dh-param-file /etc/ssl/dhparam.pem" in output

    def test_ssl_dh_param_file_custom(self):
        """Test ssl-dh-param-file with custom location."""
        config = """
        config test {
            global {
                ssl-dh-param-file: "/opt/haproxy/dh4096.pem"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_dh_param_file == "/opt/haproxy/dh4096.pem"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-dh-param-file /opt/haproxy/dh4096.pem" in output

    def test_ssl_engine(self):
        """Test ssl-engine directive - OpenSSL engine selection."""
        config = """
        config test {
            global {
                ssl-engine: "aesni"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_engine == "aesni"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-engine aesni" in output

    def test_ssl_engine_custom(self):
        """Test ssl-engine with different engine."""
        config = """
        config test {
            global {
                ssl-engine: "rdrand"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_engine == "rdrand"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-engine rdrand" in output

    def test_ssl_server_verify_none(self):
        """Test ssl-server-verify directive set to none."""
        config = """
        config test {
            global {
                ssl-server-verify: "none"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_server_verify == "none"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-server-verify none" in output

    def test_ssl_server_verify_required(self):
        """Test ssl-server-verify directive set to required."""
        config = """
        config test {
            global {
                ssl-server-verify: "required"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_server_verify == "required"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-server-verify required" in output

    def test_ssl_complete_config(self):
        """Test comprehensive SSL configuration with all directives."""
        config = """
        config test {
            global {
                ca-base: "/etc/ssl/certs"
                crt-base: "/etc/ssl/private"
                key-base: "/etc/ssl/keys"
                ssl-dh-param-file: "/etc/ssl/dhparam.pem"
                ssl-engine: "aesni"
                ssl-server-verify: "required"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ca_base == "/etc/ssl/certs"
        assert ir.global_config.crt_base == "/etc/ssl/private"
        assert ir.global_config.key_base == "/etc/ssl/keys"
        assert ir.global_config.ssl_dh_param_file == "/etc/ssl/dhparam.pem"
        assert ir.global_config.ssl_engine == "aesni"
        assert ir.global_config.ssl_server_verify == "required"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ca-base /etc/ssl/certs" in output
        assert "crt-base /etc/ssl/private" in output
        assert "key-base /etc/ssl/keys" in output
        assert "ssl-dh-param-file /etc/ssl/dhparam.pem" in output
        assert "ssl-engine aesni" in output
        assert "ssl-server-verify required" in output

    def test_ssl_paths_in_production_config(self):
        """Test SSL paths in a production configuration."""
        config = """
        config production {
            global {
                daemon: true
                maxconn: 100000
                ca-base: "/etc/ssl/certs"
                crt-base: "/etc/ssl/private"
                ssl-dh-param-file: "/etc/ssl/dhparam.pem"
                ssl-default-bind-ciphers: "ECDHE-RSA-AES128-GCM-SHA256"
                ssl-default-bind-options: ["ssl-min-ver TLSv1.2"]
                user: "haproxy"
                group: "haproxy"
            }

            defaults {
                mode: http
            }

            frontend web {
                mode: http
            }

            backend servers {
                mode: http
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 100000
        assert ir.global_config.ca_base == "/etc/ssl/certs"
        assert ir.global_config.crt_base == "/etc/ssl/private"
        assert ir.global_config.ssl_dh_param_file == "/etc/ssl/dhparam.pem"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "daemon" in output
        assert "maxconn 100000" in output
        assert "ca-base /etc/ssl/certs" in output
        assert "crt-base /etc/ssl/private" in output
        assert "ssl-dh-param-file /etc/ssl/dhparam.pem" in output

    def test_ssl_paths_with_relative_dirs(self):
        """Test SSL paths with relative directory references."""
        config = """
        config test {
            global {
                ca-base: "./certs/ca"
                crt-base: "./certs/server"
                key-base: "./keys"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ca_base == "./certs/ca"
        assert ir.global_config.crt_base == "./certs/server"
        assert ir.global_config.key_base == "./keys"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ca-base ./certs/ca" in output
        assert "crt-base ./certs/server" in output
        assert "key-base ./keys" in output
