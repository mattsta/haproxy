"""
Test Phase 12 Batch 3: HTTPClient Timeout Global Directive

This test module covers the HTTPClient timeout directive for controlling
connection timeouts when HAProxy acts as an HTTP client for health checks,
Lua scripts, or other external HTTP operations.

Coverage:
- httpclient.timeout.connect: Connection timeout for HTTP client operations
"""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase12HTTPClient:
    """Test cases for Phase 12 Batch 3: HTTPClient timeout directive."""

    def test_httpclient_timeout_connect_basic(self):
        """Test httpclient.timeout.connect directive with basic timeout."""
        config = """
        config test {
            global {
                httpclient.timeout.connect: "5s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.httpclient_timeout_connect == "5s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "httpclient.timeout.connect 5s" in output

    def test_httpclient_timeout_connect_short(self):
        """Test httpclient.timeout.connect with short timeout for fast failures."""
        config = """
        config test {
            global {
                httpclient.timeout.connect: "1s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.httpclient_timeout_connect == "1s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "httpclient.timeout.connect 1s" in output

    def test_httpclient_timeout_connect_milliseconds(self):
        """Test httpclient.timeout.connect with millisecond precision."""
        config = """
        config test {
            global {
                httpclient.timeout.connect: "500ms"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.httpclient_timeout_connect == "500ms"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "httpclient.timeout.connect 500ms" in output

    def test_httpclient_timeout_connect_long(self):
        """Test httpclient.timeout.connect with longer timeout for slow networks."""
        config = """
        config test {
            global {
                httpclient.timeout.connect: "30s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.httpclient_timeout_connect == "30s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "httpclient.timeout.connect 30s" in output

    def test_httpclient_timeout_connect_with_other_httpclient_settings(self):
        """Test httpclient.timeout.connect combined with other httpclient settings."""
        config = """
        config test {
            global {
                httpclient.retries: 3
                httpclient.timeout.connect: "5s"
                httpclient.ssl.verify: "required"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.httpclient_retries == 3
        assert ir.global_config.httpclient_timeout_connect == "5s"
        assert ir.global_config.httpclient_ssl_verify == "required"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "httpclient.retries 3" in output
        assert "httpclient.timeout.connect 5s" in output
        assert "httpclient.ssl.verify required" in output

    def test_httpclient_complete_configuration(self):
        """Test complete httpclient configuration with all settings."""
        config = """
        config test {
            global {
                httpclient.resolvers.id: "dns1"
                httpclient.resolvers.prefer: "ipv4"
                httpclient.retries: 5
                httpclient.timeout.connect: "10s"
                httpclient.ssl.verify: "none"
                httpclient.ssl.ca-file: "/etc/ssl/certs/ca-bundle.crt"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all httpclient settings
        assert ir.global_config.httpclient_resolvers_id == "dns1"
        assert ir.global_config.httpclient_resolvers_prefer == "ipv4"
        assert ir.global_config.httpclient_retries == 5
        assert ir.global_config.httpclient_timeout_connect == "10s"
        assert ir.global_config.httpclient_ssl_verify == "none"
        assert ir.global_config.httpclient_ssl_ca_file == "/etc/ssl/certs/ca-bundle.crt"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "httpclient.resolvers.id dns1" in output
        assert "httpclient.resolvers.prefer ipv4" in output
        assert "httpclient.retries 5" in output
        assert "httpclient.timeout.connect 10s" in output
        assert "httpclient.ssl.verify none" in output
        assert "httpclient.ssl.ca-file /etc/ssl/certs/ca-bundle.crt" in output

    def test_httpclient_health_check_scenario(self):
        """Test httpclient configuration for external health checks."""
        config = """
        config health_checks {
            global {
                httpclient.timeout.connect: "2s"
                httpclient.retries: 2
                httpclient.ssl.verify: "required"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify health check specific settings
        assert ir.global_config.httpclient_timeout_connect == "2s"
        assert ir.global_config.httpclient_retries == 2
        assert ir.global_config.httpclient_ssl_verify == "required"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "httpclient.timeout.connect 2s" in output
        assert "httpclient.retries 2" in output
        assert "httpclient.ssl.verify required" in output

    def test_httpclient_lua_integration(self):
        """Test httpclient configuration for Lua script HTTP calls."""
        config = """
        config lua_http {
            global {
                httpclient.timeout.connect: "3s"
                httpclient.retries: 1
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify Lua-specific HTTP client settings
        assert ir.global_config.httpclient_timeout_connect == "3s"
        assert ir.global_config.httpclient_retries == 1

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "httpclient.timeout.connect 3s" in output
        assert "httpclient.retries 1" in output

    def test_httpclient_production_config(self):
        """Test production-grade httpclient configuration."""
        config = """
        config production {
            global {
                daemon: true
                maxconn: 50000
                httpclient.resolvers.id: "internal-dns"
                httpclient.resolvers.prefer: "ipv4"
                httpclient.retries: 3
                httpclient.timeout.connect: "5s"
                httpclient.ssl.verify: "required"
                httpclient.ssl.ca-file: "/etc/haproxy/ca-certificates.crt"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify production settings
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.httpclient_resolvers_id == "internal-dns"
        assert ir.global_config.httpclient_resolvers_prefer == "ipv4"
        assert ir.global_config.httpclient_retries == 3
        assert ir.global_config.httpclient_timeout_connect == "5s"
        assert ir.global_config.httpclient_ssl_verify == "required"
        assert ir.global_config.httpclient_ssl_ca_file == "/etc/haproxy/ca-certificates.crt"

        # Verify codegen output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 50000" in output
        assert "httpclient.resolvers.id internal-dns" in output
        assert "httpclient.resolvers.prefer ipv4" in output
        assert "httpclient.retries 3" in output
        assert "httpclient.timeout.connect 5s" in output
        assert "httpclient.ssl.verify required" in output
        assert "httpclient.ssl.ca-file /etc/haproxy/ca-certificates.crt" in output
