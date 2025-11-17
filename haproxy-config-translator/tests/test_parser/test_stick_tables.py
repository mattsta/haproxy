"""Tests for stick-table and TCP request/response rule parsing and code generation."""

import pytest

from haproxy_translator.ir.nodes import (
    Backend,
    Frontend,
    StickRule,
    StickTable,
    TcpRequestRule,
    TcpResponseRule,
)
from haproxy_translator.parsers.dsl_parser import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


@pytest.fixture
def parser():
    """Create DSL parser instance."""
    return DSLParser()


@pytest.fixture
def codegen():
    """Create code generator instance."""
    return HAProxyCodeGenerator()


def parse_dsl_config(source):
    """Helper to parse DSL config."""
    parser = DSLParser()
    return parser.parse(source)


class TestStickTableParsing:
    """Test stick-table configuration parsing."""

    def test_basic_stick_table_in_frontend(self):
        """Test basic stick-table with type and size."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                stick-table {
                    type: ip
                    size: 100000
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        assert len(ir.frontends) == 1
        frontend = ir.frontends[0]
        assert frontend.stick_table is not None
        assert frontend.stick_table.type == "ip"
        assert frontend.stick_table.size == 100000
        assert frontend.stick_table.expire is None

    def test_stick_table_with_expire(self):
        """Test stick-table with expire duration."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                stick-table {
                    type: ip
                    size: 50000
                    expire: 30m
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert frontend.stick_table is not None
        assert frontend.stick_table.type == "ip"
        assert frontend.stick_table.size == 50000
        assert frontend.stick_table.expire == "30m"

    def test_stick_table_with_all_properties(self):
        """Test stick-table with all optional properties."""
        dsl = """
        config myapp {
            backend api {
                stick-table {
                    type: string
                    size: 200000
                    expire: 1h
                    nopurge: true
                    peers: mycluster
                    store: ["gpc0", "conn_rate(10s)", "http_req_rate(10s)"]
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert backend.stick_table is not None
        assert backend.stick_table.type == "string"
        assert backend.stick_table.size == 200000
        assert backend.stick_table.expire == "1h"
        assert backend.stick_table.nopurge is True
        assert backend.stick_table.peers == "mycluster"
        assert backend.stick_table.store == ["gpc0", "conn_rate(10s)", "http_req_rate(10s)"]

    def test_stick_table_types(self):
        """Test all stick-table types."""
        types = ["ip", "ipv6", "integer", "string", "binary"]

        for table_type in types:
            dsl = f"""
            config myapp {{
                frontend web {{
                    bind ":8080"

                    stick-table {{
                        type: {table_type}
                        size: 10000
                    }}
                }}
            }}
            """
            ir = parse_dsl_config(dsl)
            frontend = ir.frontends[0]
            assert frontend.stick_table.type == table_type


class TestStickRuleParsing:
    """Test stick rule parsing."""

    def test_stick_on_rule(self):
        """Test stick on rule."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                stick-table {
                    type: ip
                    size: 100000
                }

                stick on src
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert len(frontend.stick_rules) == 1
        rule = frontend.stick_rules[0]
        assert rule.rule_type == "on"
        assert rule.pattern == "src"
        assert rule.condition is None

    def test_stick_match_rule(self):
        """Test stick match rule."""
        dsl = """
        config myapp {
            backend api {
                stick-table {
                    type: ip
                    size: 50000
                }

                stick match src
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert len(backend.stick_rules) == 1
        rule = backend.stick_rules[0]
        assert rule.rule_type == "match"
        assert rule.pattern == "src"

    def test_stick_store_request_rule(self):
        """Test stick store-request rule."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                stick-table {
                    type: string
                    size: 100000
                }

                stick store-request req.hdr
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert len(frontend.stick_rules) == 1
        rule = frontend.stick_rules[0]
        assert rule.rule_type == "store-request"
        assert rule.pattern == "req.hdr"

    def test_stick_store_response_rule(self):
        """Test stick store-response rule."""
        dsl = """
        config myapp {
            backend api {
                stick-table {
                    type: string
                    size: 100000
                }

                stick store-response res.cook
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert len(backend.stick_rules) == 1
        rule = backend.stick_rules[0]
        assert rule.rule_type == "store-response"
        assert rule.pattern == "res.cook"

    def test_stick_rule_with_condition(self):
        """Test stick rule with conditional."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                acl is_api {
                    path_beg "/api"
                }

                stick-table {
                    type: ip
                    size: 100000
                }

                stick on src if is_api
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert len(frontend.stick_rules) == 1
        rule = frontend.stick_rules[0]
        assert rule.rule_type == "on"
        assert rule.pattern == "src"
        assert rule.condition == "is_api"

    def test_multiple_stick_rules(self):
        """Test multiple stick rules."""
        dsl = """
        config myapp {
            backend api {
                stick-table {
                    type: ip
                    size: 100000
                }

                stick on src
                stick match src
                stick store-request hdr(X-User-ID)
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert len(backend.stick_rules) == 3
        assert backend.stick_rules[0].rule_type == "on"
        assert backend.stick_rules[1].rule_type == "match"
        assert backend.stick_rules[2].rule_type == "store-request"


class TestTcpRequestRuleParsing:
    """Test TCP request rule parsing."""

    def test_tcp_request_connection_accept(self):
        """Test tcp-request connection accept rule."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                tcp-request {
                    connection accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert len(frontend.tcp_request_rules) == 1
        rule = frontend.tcp_request_rules[0]
        assert rule.rule_type == "connection"
        assert rule.action == "accept"
        assert rule.condition is None

    def test_tcp_request_connection_reject(self):
        """Test tcp-request connection reject rule."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                acl bad_network {
                    src "192.168.1.0/24"
                }

                tcp-request {
                    connection reject if bad_network
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert len(frontend.tcp_request_rules) == 1
        rule = frontend.tcp_request_rules[0]
        assert rule.rule_type == "connection"
        assert rule.action == "reject"
        assert rule.condition == "bad_network"

    def test_tcp_request_content_accept(self):
        """Test tcp-request content accept rule."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                tcp-request {
                    content accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert len(frontend.tcp_request_rules) == 1
        rule = frontend.tcp_request_rules[0]
        assert rule.rule_type == "content"
        assert rule.action == "accept"

    def test_tcp_request_inspect_delay(self):
        """Test tcp-request inspect-delay rule."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                tcp-request {
                    inspect-delay timeout 5s
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]
        assert len(frontend.tcp_request_rules) == 1
        rule = frontend.tcp_request_rules[0]
        assert rule.rule_type == "inspect-delay"
        assert rule.action == "timeout"

    def test_multiple_tcp_request_rules(self):
        """Test multiple tcp-request rules in one block."""
        dsl = """
        config myapp {
            backend api {
                tcp-request {
                    connection accept
                    content accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert len(backend.tcp_request_rules) == 2
        assert backend.tcp_request_rules[0].rule_type == "connection"
        assert backend.tcp_request_rules[0].action == "accept"
        assert backend.tcp_request_rules[1].rule_type == "content"
        assert backend.tcp_request_rules[1].action == "accept"


class TestTcpResponseRuleParsing:
    """Test TCP response rule parsing."""

    def test_tcp_response_content_accept(self):
        """Test tcp-response content accept rule."""
        dsl = """
        config myapp {
            backend api {
                tcp-response {
                    content accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert len(backend.tcp_response_rules) == 1
        rule = backend.tcp_response_rules[0]
        assert rule.rule_type == "content"
        assert rule.action == "accept"

    def test_tcp_response_with_condition(self):
        """Test tcp-response rule with condition."""
        dsl = """
        config myapp {
            backend api {
                acl is_valid {
                    src "10.0.0.0/8"
                }

                tcp-response {
                    content accept if is_valid
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert len(backend.tcp_response_rules) == 1
        rule = backend.tcp_response_rules[0]
        assert rule.rule_type == "content"
        assert rule.action == "accept"
        assert rule.condition == "is_valid"

    def test_tcp_response_inspect_delay(self):
        """Test tcp-response inspect-delay rule."""
        dsl = """
        config myapp {
            backend api {
                tcp-response {
                    inspect-delay timeout 3s
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]
        assert len(backend.tcp_response_rules) == 1
        rule = backend.tcp_response_rules[0]
        assert rule.rule_type == "inspect-delay"
        assert rule.action == "timeout"


class TestStickTableCodeGeneration:
    """Test stick-table code generation."""

    def test_generate_basic_stick_table(self, codegen):
        """Test code generation for basic stick-table."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                stick-table {
                    type: ip
                    size: 100000
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "stick-table type ip size 100000" in config

    def test_generate_stick_table_with_expire(self, codegen):
        """Test code generation for stick-table with expire."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                stick-table {
                    type: ip
                    size: 50000
                    expire: 30m
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "stick-table type ip size 50000 expire 30m" in config

    def test_generate_stick_table_complete(self, codegen):
        """Test code generation for stick-table with all properties."""
        dsl = """
        config myapp {
            backend api {
                stick-table {
                    type: string
                    size: 200000
                    expire: 1h
                    nopurge: true
                    peers: mycluster
                    store: ["gpc0", "conn_rate(10s)"]
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "stick-table type string size 200000" in config
        assert "expire 1h" in config
        assert "nopurge" in config
        assert "peers mycluster" in config
        assert "store gpc0 conn_rate(10s)" in config

    def test_generate_stick_on_rule(self, codegen):
        """Test code generation for stick on rule."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                stick-table {
                    type: ip
                    size: 100000
                }

                stick on src
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "stick on src" in config

    def test_generate_stick_rule_with_condition(self, codegen):
        """Test code generation for stick rule with condition."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                acl is_api {
                    path_beg "/api"
                }

                stick-table {
                    type: ip
                    size: 100000
                }

                stick on src if is_api
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "stick on src if is_api" in config

    def test_generate_multiple_stick_rules(self, codegen):
        """Test code generation for multiple stick rules."""
        dsl = """
        config myapp {
            backend api {
                stick-table {
                    type: ip
                    size: 100000
                }

                stick on src
                stick match src
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "stick on src" in config
        assert "stick match src" in config


class TestTcpRuleCodeGeneration:
    """Test TCP rule code generation."""

    def test_generate_tcp_request_connection(self, codegen):
        """Test code generation for tcp-request connection."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                tcp-request {
                    connection accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "tcp-request connection accept" in config

    def test_generate_tcp_request_with_condition(self, codegen):
        """Test code generation for tcp-request with condition."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                acl bad_network {
                    src "192.168.1.0/24"
                }

                tcp-request {
                    connection reject if bad_network
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "tcp-request connection reject if bad_network" in config

    def test_generate_tcp_response_content(self, codegen):
        """Test code generation for tcp-response content."""
        dsl = """
        config myapp {
            backend api {
                tcp-response {
                    content accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "tcp-response content accept" in config

    def test_generate_multiple_tcp_rules(self, codegen):
        """Test code generation for multiple TCP rules."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                tcp-request {
                    connection accept
                    content accept
                }

                tcp-response {
                    content accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)
        config = codegen.generate(ir)

        assert "tcp-request connection accept" in config
        assert "tcp-request content accept" in config
        assert "tcp-response content accept" in config


class TestIntegrationStickTableTcp:
    """Integration tests for stick-table and TCP rules together."""

    def test_frontend_with_stick_table_and_tcp_rules(self, codegen):
        """Test frontend with both stick-table and TCP rules."""
        dsl = """
        config myapp {
            frontend web {
                bind ":8080"

                acl is_trusted {
                    src "10.0.0.0/8"
                }

                stick-table {
                    type: ip
                    size: 100000
                    expire: 30s
                }

                stick on src

                tcp-request {
                    connection reject if is_trusted
                    content accept
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        frontend = ir.frontends[0]

        assert frontend.stick_table is not None
        assert frontend.stick_table.type == "ip"
        assert frontend.stick_table.size == 100000

        assert len(frontend.stick_rules) == 1
        assert frontend.stick_rules[0].rule_type == "on"

        assert len(frontend.tcp_request_rules) == 2

        config = codegen.generate(ir)

        assert "stick-table type ip size 100000 expire 30s" in config
        assert "stick on src" in config
        assert "tcp-request connection reject if is_trusted" in config
        assert "tcp-request content accept" in config

    def test_backend_with_stick_table_and_acls(self, codegen):
        """Test backend with stick-table, ACLs, and TCP rules."""
        dsl = """
        config myapp {
            backend api {
                balance: roundrobin

                acl is_local {
                    src "127.0.0.1"
                }

                stick-table {
                    type: ip
                    size: 50000
                    expire: 5m
                }

                stick on src

                tcp-request {
                    content accept if is_local
                }

                servers {
                    server s1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        backend = ir.backends[0]

        assert len(backend.acls) == 1
        assert backend.acls[0].name == "is_local"

        assert backend.stick_table is not None

        assert len(backend.stick_rules) == 1

        assert len(backend.tcp_request_rules) == 1

        assert len(backend.servers) == 1

        config = codegen.generate(ir)

        assert "backend api" in config
        assert "acl is_local" in config
        assert "stick-table type ip size 50000 expire 5m" in config
        assert "stick on src" in config
        assert "tcp-request content accept if is_local" in config

    def test_complete_rate_limiting_config(self, codegen):
        """Test complete rate limiting configuration with stick-tables and TCP rules."""
        dsl = """
        config rate_limited {
            frontend web {
                bind ":80"
                mode: http

                stick-table {
                    type: ip
                    size: 1000000
                    expire: 30s
                }

                stick on src

                acl is_local {
                    src "127.0.0.1"
                }

                tcp-request {
                    connection accept if is_local
                    content accept
                }

                http-request {
                    deny if is_local
                }

                default_backend: api
            }

            backend api {
                balance: leastconn

                servers {
                    server s1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }

                    server s2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parse_dsl_config(dsl)

        assert len(ir.frontends) == 1
        assert len(ir.backends) == 1

        frontend = ir.frontends[0]

        assert frontend.stick_table is not None
        assert frontend.stick_table.type == "ip"
        assert frontend.stick_table.size == 1000000

        assert len(frontend.stick_rules) == 1

        assert len(frontend.acls) == 1

        assert len(frontend.tcp_request_rules) == 2

        assert len(frontend.http_request_rules) == 1

        config = codegen.generate(ir)

        assert "frontend web" in config
        assert "bind :80" in config
        assert "stick-table type ip size 1000000 expire 30s" in config
        assert "stick on src" in config
        assert "acl is_local" in config
        assert "tcp-request connection accept if is_local" in config
        assert "tcp-request content accept" in config
        assert "http-request deny if is_local" in config
        assert "default_backend api" in config
        assert "backend api" in config
        assert "balance leastconn" in config
