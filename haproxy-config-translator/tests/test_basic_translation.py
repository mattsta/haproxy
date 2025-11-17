"""Basic end-to-end translation test."""

import pytest
from pathlib import Path

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


def test_basic_dsl_to_haproxy():
    """Test basic DSL to HAProxy translation."""
    dsl_source = """
config test_config {
  global {
    daemon: true
    maxconn: 2000
    log "/dev/log" local0 info
  }

  defaults {
    mode: http
    retries: 3
    timeout: {
      connect: 5s
      client: 50s
      server: 50s
    }
  }

  frontend test_front {
    bind *:80

    default_backend: test_back
  }

  backend test_back {
    balance: roundrobin

    servers {
      server test1 {
        address: "127.0.0.1"
        port: 8080
        check: true
      }
    }
  }
}
"""

    # Parse
    parser = DSLParser()
    ir = parser.parse(dsl_source)

    # Verify IR
    assert ir.name == "test_config"
    assert ir.global_config is not None
    assert ir.global_config.daemon is True
    assert ir.global_config.maxconn == 2000

    assert ir.defaults is not None
    assert len(ir.frontends) == 1
    assert ir.frontends[0].name == "test_front"

    assert len(ir.backends) == 1
    assert ir.backends[0].name == "test_back"
    assert len(ir.backends[0].servers) == 1

    # Generate HAProxy config
    generator = HAProxyCodeGenerator()
    output = generator.generate(ir)

    # Verify output contains expected sections
    assert "global" in output
    assert "defaults" in output
    assert "frontend test_front" in output
    assert "backend test_back" in output
    assert "server test1 127.0.0.1:8080" in output
    assert "daemon" in output
    assert "maxconn 2000" in output


def test_template_expansion():
    """Test template spreading."""
    dsl_source = """
config template_test {
  template server_defaults {
    check: true
    inter: 3s
    rise: 2
    fall: 3
  }

  backend test_back {
    balance: roundrobin

    servers {
      server test1 {
        address: "127.0.0.1"
        port: 8080
        @server_defaults
      }
    }
  }
}
"""

    parser = DSLParser()
    ir = parser.parse(dsl_source)

    assert len(ir.templates) == 1
    assert "server_defaults" in ir.templates

    # Check server has template properties
    backend = ir.backends[0]
    assert len(backend.servers) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
