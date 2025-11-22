"""Test code generator edge cases for improved coverage."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.ir.nodes import (
    Backend,
    BalanceAlgorithm,
    Bind,
    ConfigIR,
    Frontend,
    HttpRequestRule,
    Mode,
    Server,
    StickRule,
    StickTable,
    TcpRequestRule,
    TcpResponseRule,
)
from haproxy_translator.parsers import DSLParser


class TestCodeGenEdgeCases:
    """Test edge cases in code generation for coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_default_server_send_proxy_v2(self, parser, codegen):
        """Test default-server with send-proxy-v2."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                default-server {
                    send-proxy-v2: true
                    check: true
                }
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
        output = codegen.generate(ir)
        assert "default-server check send-proxy-v2" in output

    def test_server_options_dict(self, codegen):
        """Test server with additional options dict."""

        server = Server(
            name="api1",
            address="10.0.1.1",
            port=8080,
            options={"resolvers": "dns", "init-addr": "last"},
        )
        backend = Backend(name="api", balance=BalanceAlgorithm.ROUNDROBIN, servers=[server])
        ir = ConfigIR(backends=[backend])

        output = codegen.generate(ir)
        # Options should be in the output
        assert "resolvers dns" in output or "init-addr last" in output

    def test_stick_rule_with_table(self, codegen):
        """Test stick-on rule with table reference."""
        stick_table = StickTable(type="ip", size=100000, expire="30m")
        stick_rule = StickRule(rule_type="on", pattern="src", table="other_backend")
        server = Server(name="api1", address="10.0.1.1", port=8080)
        backend = Backend(
            name="api",
            balance=BalanceAlgorithm.ROUNDROBIN,
            stick_table=stick_table,
            stick_rules=[stick_rule],
            servers=[server],
        )
        ir = ConfigIR(backends=[backend])

        output = codegen.generate(ir)
        assert "table other_backend" in output

    def test_tcp_request_with_params_list(self, codegen):
        """Test TCP request rule with params list."""
        tcp_rule = TcpRequestRule(
            rule_type="connection", action="accept", parameters={"params": ["if", "!local"]}
        )
        frontend = Frontend(
            name="web",
            binds=[Bind(address="*:80")],
            mode=Mode.TCP,
            tcp_request_rules=[tcp_rule],
            default_backend="api",
        )
        backend = Backend(
            name="api",
            balance=BalanceAlgorithm.ROUNDROBIN,
            servers=[Server(name="api1", address="10.0.1.1", port=8080)],
        )
        ir = ConfigIR(frontends=[frontend], backends=[backend])

        output = codegen.generate(ir)
        assert "tcp-request connection accept if !local" in output

    def test_tcp_response_with_params_list(self, codegen):
        """Test TCP response rule with params list."""
        tcp_rule = TcpResponseRule(
            rule_type="content", action="accept", parameters={"params": ["if", "valid"]}
        )
        backend = Backend(
            name="api",
            balance=BalanceAlgorithm.ROUNDROBIN,
            mode=Mode.TCP,
            tcp_response_rules=[tcp_rule],
            servers=[Server(name="api1", address="10.0.1.1", port=8080)],
        )
        ir = ConfigIR(backends=[backend])

        output = codegen.generate(ir)
        assert "tcp-response content accept if valid" in output

    def test_tcp_response_with_condition(self, codegen):
        """Test TCP response rule with condition."""
        tcp_rule = TcpResponseRule(rule_type="content", action="accept", condition="valid_response")
        backend = Backend(
            name="api",
            balance=BalanceAlgorithm.ROUNDROBIN,
            mode=Mode.TCP,
            tcp_response_rules=[tcp_rule],
            servers=[Server(name="api1", address="10.0.1.1", port=8080)],
        )
        ir = ConfigIR(backends=[backend])

        output = codegen.generate(ir)
        assert "tcp-response content accept if valid_response" in output

    def test_http_request_rule_with_quoted_param(self, codegen):
        """Test HTTP request rule with parameter containing spaces."""
        http_rule = HttpRequestRule(
            action="set-header", parameters={"X-Custom": "value with spaces"}
        )
        frontend = Frontend(
            name="web",
            binds=[Bind(address="*:80")],
            http_request_rules=[http_rule],
            default_backend="api",
        )
        backend = Backend(
            name="api",
            balance=BalanceAlgorithm.ROUNDROBIN,
            servers=[Server(name="api1", address="10.0.1.1", port=8080)],
        )
        ir = ConfigIR(frontends=[frontend], backends=[backend])

        output = codegen.generate(ir)
        # The codegen should quote values with spaces
        assert 'http-request set-header X-Custom "value with spaces"' in output
