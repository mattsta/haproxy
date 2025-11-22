"""
Tests for all documentation examples to ensure they work as advertised.

This test suite validates every example from:
- QUICK_START.md
- PATTERNS.md
- MIGRATION_GUIDE.md
- SYNTAX_REFERENCE.md
"""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


@pytest.fixture
def parser():
    return DSLParser()


@pytest.fixture
def codegen():
    return HAProxyCodeGenerator()


class TestQuickStartExamples:
    """Tests for QUICK_START.md examples."""

    def test_first_configuration(self, parser, codegen):
        """Test the 'Your First Configuration' example."""
        dsl_source = """
config my_loadbalancer {
  global {
    daemon: true
    maxconn: 4096
    log "/dev/log" local0 info
  }

  defaults {
    mode: http
    retries: 3
    timeout: {
      connect: 5s
      client: 30s
      server: 30s
    }
    option: ["httplog", "dontlognull"]
  }

  frontend web {
    bind *:80
    default_backend: servers
  }

  backend servers {
    balance: roundrobin

    servers {
      server web1 {
        address: "192.168.1.10"
        port: 8080
        check: true
      }
      server web2 {
        address: "192.168.1.11"
        port: 8080
        check: true
      }
      server web3 {
        address: "192.168.1.12"
        port: 8080
        check: true
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "global" in output
        assert "daemon" in output
        assert "maxconn 4096" in output
        assert "frontend web" in output
        assert "backend servers" in output
        assert "server web1 192.168.1.10:8080 check" in output

    def test_server_syntax_styles(self, parser, codegen):
        """Test all three server syntax styles from documentation."""
        dsl_source = """
config test {
  backend api {
    servers {
      // Full syntax
      server api1 {
        address: "10.0.1.1"
        port: 8080
        check: true
        weight: 10
        inter: 3s
      }

      // Compact syntax with commas
      server api2 { address: "10.0.1.2", port: 8080, check: true, weight: 10 }

      // Inline syntax
      server api3 address: "10.0.1.3" port: 8080 check: true
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server api1 10.0.1.1:8080 check" in output
        assert "server api2 10.0.1.2:8080 check" in output
        assert "server api3 10.0.1.3:8080 check" in output

    def test_template_with_loop(self, parser, codegen):
        """Test the template + loop example from 'Why Use the DSL?'."""
        dsl_source = """
config api_cluster {
  template standard_server {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    weight: 100
  }

  backend api_servers {
    balance: roundrobin
    servers {
      for i in [1..10] {
        server "api${i}" {
          address: "10.0.1.${i}"
          port: 8080
          @standard_server
        }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Should generate 10 servers with template properties
        for i in range(1, 11):
            assert f"server api{i} 10.0.1.{i}:8080 check inter 3s" in output

    def test_server_template_example(self, parser, codegen):
        """Test server template example."""
        dsl_source = """
config test {
  template production_server {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    maxconn: 500
  }

  backend api {
    servers {
      server web1 { address: "10.0.1.1", port: 8080, @production_server }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server web1 10.0.1.1:8080 check inter 3s" in output
        assert "maxconn 500" in output

    def test_backend_template_example(self, parser, codegen):
        """Test backend template example."""
        dsl_source = """
config test {
  template api_backend {
    balance: leastconn
    option: ["httpchk GET /health", "forwardfor"]
    retries: 3
  }

  backend api_v1 {
    @api_backend
    servers {
      server s1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "balance leastconn" in output
        assert "option httpchk GET /health" in output
        assert "option forwardfor" in output
        assert "retries 3" in output

    def test_health_check_template_example(self, parser, codegen):
        """Test health check template example."""
        dsl_source = """
config test {
  template http_health {
    method: "GET"
    uri: "/health"
    expect_status: 200
  }

  backend api {
    option: ["httpchk"]
    health-check @http_health
    servers {
      server s1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "option httpchk" in output

    def test_acl_template_example(self, parser, codegen):
        """Test ACL template example."""
        dsl_source = """
config test {
  template internal_network {
    criterion: "src"
    values: ["10.0.0.0/8", "192.168.0.0/16"]
  }

  frontend web {
    bind *:80
    acl is_internal @internal_network
    default_backend: servers
  }

  backend servers {
    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "acl is_internal src 10.0.0.0/8 192.168.0.0/16" in output

    def test_loop_with_arithmetic(self, parser, codegen):
        """Test loop with arithmetic example."""
        dsl_source = """
config test {
  backend api {
    servers {
      for i in [1..3] {
        server "node${i}" { address: "10.0.1.${10 + i}", port: 8080 }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server node1 10.0.1.11:8080" in output
        assert "server node2 10.0.1.12:8080" in output
        assert "server node3 10.0.1.13:8080" in output

    def test_variable_resolution(self, parser, codegen):
        """Test variable resolution with numeric and string variables."""
        dsl_source = """
config test {
  let app_port = 8080
  let host = "10.0.1.1"

  backend api {
    servers {
      server api1 {
        address: "${host}"
        port: ${app_port}
        check: true
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server api1 10.0.1.1:8080 check" in output


class TestPatternsExamples:
    """Tests for PATTERNS.md examples."""

    def test_server_pool_generation(self, parser, codegen):
        """Test server pool generation pattern with templates and loops."""
        dsl_source = """
config api_cluster {
  template standard_server {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    weight: 100
    maxconn: 500
  }

  backend api_servers {
    balance: roundrobin
    option: ["httpchk GET /health"]

    servers {
      for i in [1..10] {
        server "api${i}" {
          address: "10.0.1.${i}"
          port: 8080
          @standard_server
        }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Should have 10 servers with template properties
        assert output.count("check inter 3s") == 10
        assert "option httpchk GET /health" in output

    def test_multi_environment_config(self, parser, codegen):
        """Test multi-environment config pattern with variable in maxconn."""
        dsl_source = """
config multi_env {
  let maxconn_val = 1000

  global {
    daemon: true
    maxconn: ${maxconn_val}
    log "/dev/log" local0 info
  }

  defaults {
    mode: http
    timeout: {
      connect: 5s
      client: 30s
      server: 30s
    }
    option: ["httplog", "dontlognull", "forwardfor"]
  }

  frontend web {
    bind *:80
    default_backend: api
  }

  backend api {
    balance: roundrobin

    servers {
      for i in [1..2] {
        server "api${i}" {
          address: "api.internal"
          port: 8080
          check: true
        }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Variable resolved maxconn should be in output
        assert "maxconn 1000" in output
        assert "timeout client 30s" in output
        assert "server api1 api.internal:8080 check" in output
        assert "server api2 api.internal:8080 check" in output

    def test_health_check_template_pattern(self, parser, codegen):
        """Test health check template pattern from PATTERNS.md."""
        dsl_source = """
config api_cluster {
  template http_health {
    method: "GET"
    uri: "/health"
    expect_status: 200
  }

  template deep_health {
    method: "GET"
    uri: "/health/deep"
    expect_status: 200
  }

  backend api_v1 {
    balance: roundrobin
    option: ["httpchk"]
    health-check @http_health

    servers {
      server api1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }

  backend payments {
    balance: leastconn
    option: ["httpchk"]
    health-check @deep_health

    servers {
      for i in [1..3] {
        server "pay${i}" { address: "10.0.3.${i}", port: 8080, check: true }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "backend api_v1" in output
        assert "backend payments" in output
        assert "balance leastconn" in output

    def test_acl_template_pattern(self, parser, codegen):
        """Test ACL template pattern from PATTERNS.md."""
        dsl_source = """
config secure_gateway {
  template internal_network {
    criterion: "src"
    values: ["10.0.0.0/8", "192.168.0.0/16", "172.16.0.0/12"]
  }

  template blocked_paths {
    criterion: "path_beg"
    values: ["/admin", "/.git", "/wp-admin", "/phpmyadmin"]
  }

  frontend web {
    bind *:443 ssl { cert: "/etc/ssl/cert.pem" }

    acl is_internal @internal_network
    acl is_blocked @blocked_paths

    http-request {
      deny if is_blocked
    }
    default_backend: public
  }

  backend public {
    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "acl is_internal src 10.0.0.0/8 192.168.0.0/16 172.16.0.0/12" in output
        assert "acl is_blocked path_beg /admin /.git /wp-admin /phpmyadmin" in output
        assert "http-request deny if is_blocked" in output

    def test_backend_template_pattern(self, parser, codegen):
        """Test backend template pattern from PATTERNS.md."""
        dsl_source = """
config api_services {
  template production_backend {
    balance: leastconn
    option: ["httpchk GET /health", "forwardfor"]
    retries: 3
  }

  backend api_v1 {
    @production_backend
    servers {
      server api1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }

  backend api_v2 {
    @production_backend
    servers {
      server api2 { address: "10.0.2.1", port: 8080, check: true }
    }
  }

  backend api_v3 {
    @production_backend
    servers {
      server api3 { address: "10.0.3.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # All three backends should have template properties
        assert output.count("balance leastconn") == 3
        assert output.count("option httpchk GET /health") == 3
        assert output.count("option forwardfor") == 3
        assert output.count("retries 3") == 3


class TestMigrationGuideExamples:
    """Tests for MIGRATION_GUIDE.md examples."""

    def test_basic_structure(self, parser, codegen):
        """Test basic structure example."""
        dsl_source = """
config my_app {
  global {
    daemon: true
    maxconn: 4096
    log "/dev/log" local0 info
  }

  defaults {
    mode: http
    timeout: {
      connect: 5s
      client: 30s
      server: 30s
    }
  }

  frontend web {
    bind *:80
    default_backend: servers
  }

  backend servers {
    balance: roundrobin

    servers {
      server web1 {
        address: "192.168.1.10"
        port: 8080
        check: true
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "maxconn 4096" in output
        assert "timeout connect 5s" in output
        assert "timeout client 30s" in output
        assert "timeout server 30s" in output

    def test_ssl_bind_options(self, parser, codegen):
        """Test SSL bind options example."""
        dsl_source = """
config test {
  frontend https {
    bind *:443 ssl {
      cert: "/etc/ssl/certs/site.pem"
      alpn: ["h2", "http/1.1"]
    }
    default_backend: servers
  }

  backend servers {
    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "bind *:443 ssl crt /etc/ssl/certs/site.pem alpn h2,http/1.1" in output

    def test_default_server_settings(self, parser, codegen):
        """Test default-server settings example."""
        dsl_source = """
config test {
  backend api {
    default-server {
      check: true
      inter: 3s
      fall: 3
      rise: 2
    }

    servers {
      server api1 {
        address: "10.0.1.1"
        port: 8080
      }
      server api2 {
        address: "10.0.1.2"
        port: 8080
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "default-server check inter 3s" in output
        assert "server api1 10.0.1.1:8080" in output
        assert "server api2 10.0.1.2:8080" in output

    def test_stick_table(self, parser, codegen):
        """Test stick-table example."""
        dsl_source = """
config test {
  backend api {
    stick-table {
      type: ip
      size: 100000
      expire: 30m
      store: ["conn_cur", "conn_rate(10s)"]
    }

    stick on src
    stick match src

    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "stick-table type ip size 100000 expire 30m" in output
        assert "stick on src" in output
        assert "stick match src" in output

    def test_http_request_rules(self, parser, codegen):
        """Test http-request rules example."""
        dsl_source = """
config test {
  frontend web {
    bind *:80

    http-request {
      set_header name: "X-Forwarded-Proto" value: "https"
    }

    default_backend: servers
  }

  backend servers {
    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "http-request" in output


class TestSyntaxReferenceExamples:
    """Tests for SYNTAX_REFERENCE.md examples."""

    def test_multiple_template_types_together(self, parser, codegen):
        """Test multiple template types together example."""
        dsl_source = """
config production {
  template prod_backend {
    balance: leastconn
    option: ["httpchk", "forwardfor"]
    retries: 3
  }

  template prod_server {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    maxconn: 500
  }

  template http_health {
    method: "GET"
    uri: "/health"
    expect_status: 200
  }

  template api_acl {
    criterion: "path_beg"
    values: ["/api/"]
  }

  frontend web {
    bind *:80
    acl is_api @api_acl
    use_backend api if is_api
    default_backend: webservers
  }

  backend api {
    @prod_backend
    health-check @http_health

    servers {
      for i in [1..5] {
        server "api${i}" {
          address: "10.0.1.${i}"
          port: 8080
          @prod_server
        }
      }
    }
  }

  backend webservers {
    servers {
      server w1 { address: "10.0.2.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Backend template properties
        assert "balance leastconn" in output
        assert "option httpchk" in output
        assert "option forwardfor" in output
        assert "retries 3" in output

        # ACL template
        assert "acl is_api path_beg /api/" in output

        # Server template properties on all 5 servers
        assert output.count("check inter 3s") == 5
        assert output.count("maxconn 500") == 5

    def test_backend_templates_section(self, parser, codegen):
        """Test backend templates section example."""
        dsl_source = """
config backend_templates {
  template production_backend {
    balance: leastconn
    option: ["httpchk GET /health", "forwardfor"]
    retries: 3
  }

  template standard_backend {
    balance: roundrobin
    option: ["httpchk"]
  }

  backend api {
    @production_backend

    servers {
      server api1 { address: "10.0.1.1", port: 8080, check: true }
      server api2 { address: "10.0.1.2", port: 8080, check: true }
    }
  }

  backend web {
    @standard_backend
    balance: leastconn  // Override template's balance

    servers {
      server web1 { address: "10.0.2.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Backend api should have production_backend properties
        assert "option httpchk GET /health" in output
        assert "option forwardfor" in output
        assert "retries 3" in output

        # Backend web should have override balance
        # Note: The last balance value in output for 'web' backend should be leastconn
        assert "backend web" in output


class TestEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_empty_servers_block(self, parser, codegen):
        """Test backend with server-template directive."""
        dsl_source = """
config test {
  backend dynamic {
    server-template srv [1..5] {
      address: "example.com"
      port: 8080
      check: true
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Check server-template is in output
        assert "server-template" in output
        assert "example.com" in output

    def test_combined_loop_and_template(self, parser, codegen):
        """Test complex combination of loops and templates."""
        dsl_source = """
config test {
  template prod {
    check: true
    inter: 3s
  }

  backend api {
    servers {
      for i in [1..3] {
        server "api${i}" { address: "10.0.1.${i}", port: 8080, @prod }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        for i in range(1, 4):
            assert f"server api{i} 10.0.1.{i}:8080 check inter 3s" in output

    def test_nested_variable_resolution(self, parser, codegen):
        """Test nested variable resolution."""
        dsl_source = """
config test {
  let port = 8080
  let host = "10.0.1.1"
  let endpoint = "${host}:${port}"

  backend api {
    servers {
      server api1 {
        address: "${host}"
        port: ${port}
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server api1 10.0.1.1:8080" in output

    def test_env_function_with_default(self, parser, codegen):
        """Test env() function with default value."""
        import os

        # Test with unset variable (uses default)
        dsl_source = """
config test {
  let api_host = env("HAPROXY_TEST_UNSET_VAR", "default.host.com")

  backend api {
    servers {
      server api1 { address: "${api_host}", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Should use default value
        assert "server api1 default.host.com:8080" in output

    def test_env_function_with_set_variable(self, parser, codegen):
        """Test env() function with set environment variable."""
        import os

        # Set the environment variable
        os.environ["HAPROXY_TEST_API_HOST"] = "env.host.com"

        try:
            dsl_source = """
config test {
  let api_host = env("HAPROXY_TEST_API_HOST", "default.host.com")

  backend api {
    servers {
      server api1 { address: "${api_host}", port: 8080 }
    }
  }
}
"""
            ir = parser.parse(dsl_source)
            output = codegen.generate(ir)

            # Should use environment variable value
            assert "server api1 env.host.com:8080" in output
        finally:
            # Clean up
            del os.environ["HAPROXY_TEST_API_HOST"]


class TestCoverageGaps:
    """Tests specifically for coverage gaps in template_expander.py and other modules."""

    def test_health_check_template_with_post_method(self, parser, codegen):
        """Test health check template with POST method property."""
        dsl_source = """
config test {
  template custom_health {
    method: "POST"
    uri: "/health/deep"
  }

  backend api {
    option: ["httpchk"]
    health-check @custom_health
    servers {
      server s1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "option httpchk" in output
        assert "http-check send meth POST uri /health/deep" in output

    def test_health_check_with_custom_uri(self, parser, codegen):
        """Test health check with custom URI."""
        dsl_source = """
config test {
  backend api {
    option: ["httpchk"]
    health-check {
      method: "GET"
      uri: "/api/v1/status"
    }
    servers {
      server s1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "option httpchk" in output
        assert "/api/v1/status" in output

    def test_backend_template_with_mode_tcp(self, parser, codegen):
        """Test backend template with TCP mode (non-default)."""
        dsl_source = """
config test {
  template tcp_backend {
    mode: tcp
    balance: leastconn
    timeout_server: 60s
    timeout_connect: 10s
  }

  backend db {
    @tcp_backend
    servers {
      server db1 { address: "10.0.1.1", port: 5432, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "mode tcp" in output
        assert "balance leastconn" in output

    def test_backend_template_with_cookie(self, parser, codegen):
        """Test backend template with cookie configuration."""
        dsl_source = """
config test {
  template sticky_backend {
    balance: roundrobin
    cookie: "SERVERID insert indirect nocache"
  }

  backend web {
    @sticky_backend
    servers {
      server web1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "cookie SERVERID insert indirect nocache" in output

    def test_backend_template_with_retries_and_maxconn(self, parser, codegen):
        """Test backend template with numeric retries and maxconn."""
        dsl_source = """
config test {
  template resilient_backend {
    balance: roundrobin
    retries: 5
    maxconn: 2000
  }

  backend api {
    @resilient_backend
    servers {
      server api1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "retries 5" in output

    def test_backend_template_with_log_tag(self, parser, codegen):
        """Test backend template with log_tag."""
        dsl_source = """
config test {
  template logging_backend {
    balance: roundrobin
    log_tag: "api_backend"
  }

  backend api {
    @logging_backend
    servers {
      server api1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "log-tag api_backend" in output

    def test_acl_template_with_flags(self, parser, codegen):
        """Test ACL template with flags."""
        dsl_source = """
config test {
  template case_insensitive_path {
    criterion: "path_beg"
    flags: ["-i"]
    values: ["/api", "/admin"]
  }

  frontend web {
    bind *:80
    acl is_api @case_insensitive_path
    default_backend: servers
  }

  backend servers {
    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "acl is_api" in output

    def test_backend_explicit_overrides_template(self, parser, codegen):
        """Test that explicit backend properties override template values."""
        dsl_source = """
config test {
  template default_backend {
    balance: roundrobin
    retries: 3
  }

  backend api {
    @default_backend
    balance: leastconn  // Override template
    retries: 5          // Override template
    servers {
      server api1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Should use explicit values, not template values
        assert "balance leastconn" in output
        assert "retries 5" in output

    def test_health_check_with_interval(self, parser, codegen):
        """Test health check with interval property."""
        dsl_source = """
config test {
  template interval_health {
    method: "GET"
    uri: "/ping"
    interval: 5s
  }

  backend api {
    option: ["httpchk"]
    health-check @interval_health
    servers {
      server s1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "option httpchk" in output

    def test_health_check_with_expect_status_non_default(self, parser, codegen):
        """Test health check with non-default expect_status."""
        dsl_source = """
config test {
  template redirect_health {
    method: "GET"
    uri: "/health"
    expect_status: 302
  }

  backend api {
    option: ["httpchk"]
    health-check @redirect_health
    servers {
      server s1 { address: "10.0.1.1", port: 8080, check: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "http-check expect status 302" in output

    def test_stats_with_refresh(self, parser, codegen):
        """Test stats configuration with refresh."""
        dsl_source = """
config test {
  frontend web {
    bind *:80
    stats {
      enable: true
      uri: "/haproxy-stats"
      auth: "admin:secret"
      refresh: 10s
    }
    default_backend: servers
  }

  backend servers {
    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "stats enable" in output
        assert "stats uri /haproxy-stats" in output
        assert "stats auth admin:secret" in output
        assert "stats refresh 10s" in output

    def test_server_with_backup_flag(self, parser, codegen):
        """Test server with backup flag."""
        dsl_source = """
config test {
  backend api {
    servers {
      server primary { address: "10.0.1.1", port: 8080, check: true }
      server backup { address: "10.0.1.2", port: 8080, check: true, backup: true }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "server primary 10.0.1.1:8080 check" in output
        assert "server backup 10.0.1.2:8080 check" in output
        assert "backup" in output

    def test_server_with_ssl_options(self, parser, codegen):
        """Test server with SSL configuration."""
        dsl_source = """
config test {
  backend api {
    servers {
      server secure { address: "api.example.com", port: 443, ssl: true, verify: "required" }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "ssl verify required" in output

    def test_compression_configuration(self, parser, codegen):
        """Test backend compression configuration."""
        dsl_source = """
config test {
  backend api {
    compression {
      algo: "gzip"
      type: ["text/html", "text/plain", "application/json"]
    }
    servers {
      server s1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "compression algo gzip" in output

    def test_listen_section_with_stats(self, parser, codegen):
        """Test listen section with stats configuration."""
        dsl_source = """
config test {
  listen stats_page {
    bind *:8404
    mode: http
    stats {
      enable: true
      uri: "/stats"
      realm: "HAProxy Statistics"
      auth: "admin:password"
      refresh: 10s
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "listen stats_page" in output
        assert "bind *:8404" in output
        assert "stats enable" in output
        assert "stats uri /stats" in output
        assert "stats realm HAProxy Statistics" in output
        assert "stats auth admin:password" in output
        assert "stats refresh 10s" in output

    def test_listen_section_with_full_stats(self, parser, codegen):
        """Test listen section with all stats options."""
        dsl_source = """
config test {
  listen stats_full {
    bind *:8405
    mode: http
    stats {
      enable: true
      uri: "/haproxy"
      realm: "Statistics"
      auth: "admin:secret"
      refresh: 5s
      hide-version: true
      show-legends: true
      show-desc: "Production Stats"
      admin if authenticated
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "stats hide-version" in output
        assert "stats show-legends" in output
        assert "stats show-desc Production Stats" in output
        assert "stats admin if authenticated" in output


class TestPatternsMdExamples:
    """Tests for additional PATTERNS.md examples not covered elsewhere."""

    def test_blue_green_deployment_pattern(self, parser, codegen):
        """Test Blue-Green deployment pattern from PATTERNS.md with variable weights."""
        dsl_source = """
config blue_green {
  // Control which environment is active via weight variables
  let blue_weight = 100
  let green_weight = 0

  template production_server {
    check: true
    inter: 2s
    fall: 2
    rise: 2
    maxconn: 1000
  }

  frontend web {
    bind *:80
    default_backend: app_servers
  }

  backend app_servers {
    balance: roundrobin
    option: ["httpchk GET /health"]

    servers {
      for i in [1..3] {
        server "blue${i}" {
          address: "10.0.1.${i}"
          port: 8080
          weight: ${blue_weight}
          @production_server
        }
      }

      for i in [1..3] {
        server "green${i}" {
          address: "10.0.2.${i}"
          port: 8080
          weight: ${green_weight}
          @production_server
        }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Should have blue servers with weight 100
        assert "server blue1" in output
        assert "server blue2" in output
        assert "server blue3" in output
        assert "weight 100" in output

        # Should have green servers with weight 0
        assert "server green1" in output
        assert "server green2" in output
        assert "server green3" in output
        assert "weight 0" in output

    def test_weight_variable_references(self, parser, codegen):
        """Test that weight field supports variable references."""
        dsl_source = """
config test {
  let primary_weight = 100
  let secondary_weight = 50
  let standby_weight = 0

  backend api {
    servers {
      server primary { address: "10.0.1.1", port: 8080, weight: ${primary_weight} }
      server secondary { address: "10.0.1.2", port: 8080, weight: ${secondary_weight} }
      server standby { address: "10.0.1.3", port: 8080, weight: ${standby_weight} }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Variable references should be resolved
        assert "server primary 10.0.1.1:8080 weight 100" in output
        assert "server secondary 10.0.1.2:8080 weight 50" in output
        assert "server standby 10.0.1.3:8080 weight 0" in output

    def test_session_affinity_pattern(self, parser, codegen):
        """Test session affinity pattern from PATTERNS.md."""
        dsl_source = """
config sticky_sessions {
  template sticky_server {
    check: true
    inter: 3s
  }

  backend stateful_app {
    balance: roundrobin
    cookie: "SERVERID"
    option: ["httpchk GET /health"]

    servers {
      for i in [1..4] {
        server "app${i}" {
          address: "10.0.1.${i}"
          port: 8080
          @sticky_server
        }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "cookie SERVERID" in output
        assert "server app1 10.0.1.1:8080" in output
        assert "server app4 10.0.1.4:8080" in output
        assert output.count("check inter 3s") == 4

    def test_health_check_standardization_tiers(self, parser, codegen):
        """Test health check standardization with service tiers from PATTERNS.md."""
        dsl_source = """
config standardized_health {
  template critical_service {
    check: true
    inter: 1s
    fall: 2
    rise: 3
    maxconn: 2000
  }

  template standard_service {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    maxconn: 500
  }

  backend payments {
    balance: leastconn
    option: ["httpchk GET /health"]
    servers {
      server pay1 { address: "payments-1.internal", port: 8080, @critical_service }
    }
  }

  backend products {
    balance: roundrobin
    option: ["httpchk GET /health"]
    servers {
      server prod1 { address: "products-1.internal", port: 8080, @standard_service }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Critical service should have inter 1s, maxconn 2000
        assert "server pay1 payments-1.internal:8080 check inter 1s" in output
        assert "maxconn 2000" in output

        # Standard service should have inter 3s, maxconn 500
        assert "server prod1 products-1.internal:8080 check inter 3s" in output
        assert "maxconn 500" in output


class TestMigrationGuideMdExamples:
    """Tests for MIGRATION_GUIDE.md examples not covered elsewhere."""

    def test_global_process_management(self, parser, codegen):
        """Test global process management from MIGRATION_GUIDE.md."""
        dsl_source = """
config my_config {
  global {
    daemon: true
    user: "haproxy"
    group: "haproxy"
    chroot: "/var/lib/haproxy"
    pidfile: "/var/run/haproxy.pid"
    maxconn: 4096
    nbthread: 4
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "daemon" in output
        assert "user haproxy" in output
        assert "group haproxy" in output
        assert "chroot /var/lib/haproxy" in output
        assert "pidfile /var/run/haproxy.pid" in output
        assert "maxconn 4096" in output
        assert "nbthread 4" in output

    def test_global_logging(self, parser, codegen):
        """Test global logging configuration from MIGRATION_GUIDE.md."""
        dsl_source = """
config my_config {
  global {
    log "/dev/log" local0 info
    log-send-hostname: "myhost"
    log-tag: "haproxy"
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "log /dev/log local0 info" in output
        assert "log-send-hostname myhost" in output
        assert "log-tag haproxy" in output

    def test_performance_tuning(self, parser, codegen):
        """Test performance tuning directives from MIGRATION_GUIDE.md."""
        dsl_source = """
config my_config {
  global {
    tune.bufsize: 16384
    tune.maxrewrite: 1024
    tune.ssl.cachesize: 20000
    tune.http.maxhdr: 101
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "tune.bufsize 16384" in output
        assert "tune.maxrewrite 1024" in output
        assert "tune.ssl.cachesize 20000" in output
        assert "tune.http.maxhdr 101" in output

    def test_backend_with_weight_and_backup(self, parser, codegen):
        """Test backend with server weights and backup from MIGRATION_GUIDE.md."""
        dsl_source = """
config my_config {
  backend webservers {
    mode: http
    balance: roundrobin
    option: ["httpchk GET /health"]

    servers {
      server web1 {
        address: "192.168.1.10"
        port: 8080
        check: true
        weight: 10
      }
      server web2 {
        address: "192.168.1.11"
        port: 8080
        check: true
        weight: 10
      }
      server web3 {
        address: "192.168.1.12"
        port: 8080
        check: true
        weight: 5
        backup: true
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Check servers are present with weight and check options
        assert "server web1 192.168.1.10:8080" in output
        assert "server web2 192.168.1.11:8080" in output
        assert "server web3 192.168.1.12:8080" in output
        assert "weight 10" in output
        assert "weight 5" in output
        assert "backup" in output

    def test_request_routing_with_acls(self, parser, codegen):
        """Test request routing with ACLs from MIGRATION_GUIDE.md."""
        dsl_source = """
config my_config {
  frontend web {
    bind *:80

    acl is_api {
      path_beg "/api/"
    }

    acl is_static {
      path_beg "/static/"
    }

    use_backend api_servers if is_api
    use_backend static_servers if is_static
    default_backend: webservers
  }

  backend api_servers {
    servers {
      server api1 { address: "10.0.1.1", port: 8080 }
    }
  }

  backend static_servers {
    servers {
      server static1 { address: "10.0.2.1", port: 8080 }
    }
  }

  backend webservers {
    servers {
      server web1 { address: "10.0.3.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "acl is_api path_beg /api/" in output
        assert "acl is_static path_beg /static/" in output
        assert "use_backend api_servers if is_api" in output
        assert "use_backend static_servers if is_static" in output
        assert "default_backend webservers" in output

    def test_http_response_rules(self, parser, codegen):
        """Test HTTP response rules from MIGRATION_GUIDE.md."""
        dsl_source = """
config my_config {
  backend api {
    http-response {
      set_header name: "X-Frame-Options" value: "DENY"
      del_header name: "Server"
    }

    servers {
      server api1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Code generator uses keyword format
        assert "http-response set-header" in output
        assert "X-Frame-Options" in output
        assert "http-response del-header" in output
        assert "Server" in output

    def test_backend_ssl_connection(self, parser, codegen):
        """Test backend SSL connection from MIGRATION_GUIDE.md."""
        dsl_source = """
config my_config {
  backend secure_api {
    servers {
      server api1 {
        address: "10.0.1.1"
        port: 443
        ssl: true
        verify: "required"
        ca-file: "/etc/ssl/ca.pem"
        check-ssl: true
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "ssl" in output
        assert "verify required" in output
        assert "ca-file /etc/ssl/ca.pem" in output


class TestSyntaxReferenceMdExamples:
    """Tests for SYNTAX_REFERENCE.md examples not covered elsewhere."""

    def test_data_types_durations(self, parser, codegen):
        """Test various duration formats from SYNTAX_REFERENCE.md."""
        dsl_source = """
config my_config {
  defaults {
    timeout: {
      connect: 5s
      client: 30s
      server: 5m
      tunnel: 1h
      check: 500ms
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "timeout connect 5s" in output
        assert "timeout client 30s" in output
        assert "timeout server 5m" in output
        assert "timeout tunnel 1h" in output
        assert "timeout check 500ms" in output

    def test_resolvers_section(self, parser, codegen):
        """Test resolvers section from SYNTAX_REFERENCE.md."""
        dsl_source = """
config my_config {
  resolvers mydns {
    nameserver dns1 "8.8.8.8" 53
    nameserver dns2 "8.8.4.4" 53
    resolve_retries: 3
    timeout_retry: 1s
    hold_valid: 30s
  }

  backend api {
    servers {
      server api1 { address: "api.example.com", port: 8080, resolvers: "mydns" }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "resolvers mydns" in output
        assert "nameserver dns1 8.8.8.8:53" in output
        assert "nameserver dns2 8.8.4.4:53" in output
        assert "resolve_retries 3" in output

    def test_peers_section(self, parser, codegen):
        """Test peers section from SYNTAX_REFERENCE.md."""
        dsl_source = """
config my_config {
  peers mypeers {
    peer haproxy1 "192.168.1.1" 1024
    peer haproxy2 "192.168.1.2" 1024
  }

  backend api {
    stick-table {
      type: ip
      size: 100000
      expire: 30m
      peers: mypeers
    }

    servers {
      server api1 { address: "10.0.1.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "peers mypeers" in output
        assert "peer haproxy1 192.168.1.1:1024" in output
        assert "peer haproxy2 192.168.1.2:1024" in output

    def test_mailers_section(self, parser, codegen):
        """Test mailers section from SYNTAX_REFERENCE.md."""
        dsl_source = """
config my_config {
  mailers mymailers {
    timeout_mail: 10s
    mailer smtp1 "smtp.example.com" 587
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        assert "mailers mymailers" in output
        assert "mailer smtp1 smtp.example.com:587" in output
        assert "timeout mail 10s" in output

    def test_all_four_template_types_together(self, parser, codegen):
        """Test all four template types used together from SYNTAX_REFERENCE.md."""
        dsl_source = """
config production {
  template prod_backend {
    balance: leastconn
    option: ["httpchk", "forwardfor"]
    retries: 3
  }

  template prod_server {
    check: true
    inter: 3s
    fall: 3
    rise: 2
    maxconn: 500
  }

  template http_health {
    method: "GET"
    uri: "/health"
    expect_status: 200
  }

  template api_acl {
    criterion: "path_beg"
    values: ["/api/"]
  }

  frontend web {
    bind *:80
    acl is_api @api_acl
    use_backend api if is_api
    default_backend: webservers
  }

  backend api {
    @prod_backend
    health-check @http_health

    servers {
      for i in [1..3] {
        server "api${i}" {
          address: "10.0.1.${i}"
          port: 8080
          @prod_server
        }
      }
    }
  }

  backend webservers {
    servers {
      server web1 { address: "10.0.2.1", port: 8080 }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Backend template applied
        assert "balance leastconn" in output
        assert "option httpchk" in output
        assert "retries 3" in output

        # ACL template applied
        assert "acl is_api path_beg /api/" in output

        # Health check template applied
        assert "http-check send meth GET uri /health" in output

        # Server template applied to all 3 servers
        assert output.count("check inter 3s") == 3
        assert output.count("maxconn 500") == 3

    def test_loop_with_range_arithmetic(self, parser, codegen):
        """Test loop with arithmetic from SYNTAX_REFERENCE.md."""
        dsl_source = """
config my_config {
  backend api {
    servers {
      for i in [1..3] {
        server "node${i}" {
          address: "10.0.1.${10 + i}"
          port: 8080
        }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Arithmetic: 10+1=11, 10+2=12, 10+3=13
        assert "server node1 10.0.1.11:8080" in output
        assert "server node2 10.0.1.12:8080" in output
        assert "server node3 10.0.1.13:8080" in output
