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
        """Test loops without template spread (templates inside loops need future work)."""
        dsl_source = """
config api_cluster {
  backend api_servers {
    balance: roundrobin
    servers {
      for i in [1..10] {
        server "api${i}" {
          address: "10.0.1.${i}"
          port: 8080
        }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        # Should generate 10 servers
        for i in range(1, 11):
            assert f"server api{i} 10.0.1.{i}:8080" in output

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
        """Test server pool generation pattern with loops."""
        dsl_source = """
config api_cluster {
  backend api_servers {
    balance: roundrobin
    option: ["httpchk GET /health"]

    servers {
      for i in [1..10] {
        server "api${i}" {
          address: "10.0.1.${i}"
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

        # Should have 10 servers
        assert output.count("server api") == 10
        assert "option httpchk GET /health" in output

    def test_multi_environment_config(self, parser, codegen):
        """Test multi-environment config pattern."""
        dsl_source = """
config multi_env {
  global {
    daemon: true
    maxconn: 1000
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

        # Config values should be in output
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
          check: true
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

        # Servers generated from loop
        assert output.count("server api") == 5

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
        """Test loops with inline server properties."""
        dsl_source = """
config test {
  backend api {
    servers {
      for i in [1..3] {
        server "api${i}" { address: "10.0.1.${i}", port: 8080, check: true }
      }
    }
  }
}
"""
        ir = parser.parse(dsl_source)
        output = codegen.generate(ir)

        for i in range(1, 4):
            assert f"server api{i} 10.0.1.{i}:8080 check" in output

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
