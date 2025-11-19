"""Final push to 100% test coverage - targeting remaining 138 lines."""

import sys

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.ir.nodes import TcpRequestRule, TcpResponseRule
from haproxy_translator.parsers import DSLParser


class TestFinal100PercentCoverage:
    """Tests targeting the final 138 uncovered lines."""

    # ========== TCP Rules with Named Parameters (lines 1039, 1056) ==========

    def test_tcp_request_with_named_parameters(self):
        """Test TCP request rule with explicit named parameters (line 1039)."""
        # Create IR directly with named parameters
        from haproxy_translator.ir.nodes import Backend, ConfigIR, Server

        tcp_rule = TcpRequestRule(
            rule_type="content",
            action="accept",
            condition="src_is_valid",
            parameters={"table": "st_src_global", "key": "src"}  # Named params, not "params" list
        )

        backend = Backend(
            name="test_backend",
            tcp_request_rules=[tcp_rule],
            servers=[Server(name="srv1", address="127.0.0.1", port=8080)]
        )

        config = ConfigIR(name="test", backends=[backend])
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(config)

        # Should format with named parameters
        assert "tcp-request content accept" in output
        assert "table st_src_global" in output
        assert "key src" in output

    def test_tcp_response_with_named_parameters(self):
        """Test TCP response rule with explicit named parameters (line 1056)."""
        from haproxy_translator.ir.nodes import Backend, ConfigIR, Server

        tcp_rule = TcpResponseRule(
            rule_type="content",
            action="accept",
            condition=None,
            parameters={"log-format": "%ci:%cp"}  # Named params
        )

        backend = Backend(
            name="test_backend",
            tcp_response_rules=[tcp_rule],
            servers=[Server(name="srv1", address="127.0.0.1", port=8080)]
        )

        config = ConfigIR(name="test", backends=[backend])
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(config)

        assert "tcp-response content accept" in output
        assert "log-format" in output

    # ========== Python 3.7 Fallback (lines 30-33) ==========

    @pytest.mark.skipif(sys.version_info >= (3, 9), reason="Test Python 3.7 fallback")
    def test_python_37_fallback_grammar_loading(self):
        """Test Python 3.7 resource loading fallback (lines 30-33)."""
        # This would only be hit on Python 3.7-3.8
        # On Python 3.9+ this is skipped
        parser = DSLParser()
        assert parser.parser is not None

    # ========== Single Lua Script (line 81) ==========

    def test_single_lua_script_not_in_list(self):
        """Test single LuaScript object processing (line 81)."""
        config = """
        config test {
            global {
                lua {
                    load "/etc/haproxy/script.lua"
                }
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config
        assert ir.global_config.lua_scripts
        # Lua scripts are stored as strings
        assert any("/etc/haproxy/script.lua" in str(script) for script in ir.global_config.lua_scripts)

    # ========== Frontend HTTP Response Single (lines 1292, 1296) ==========

    def test_frontend_http_response_single_rule(self):
        """Test frontend with single http-response rule (lines 1292, 1296)."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                http-response {
                    set_header name: "X-Powered-By" value: "HAProxy"
                }

                default_backend: app
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert ir.frontends[0].http_response_rules
        assert "http-response" in output

    # ========== Frontend TCP Single (lines 1300, 1304) ==========

    def test_frontend_tcp_rules_single(self):
        """Test frontend with single TCP rules (lines 1300, 1304)."""
        config = """
        config test {
            frontend tcp_front {
                bind *:3306
                mode: tcp

                tcp-request {
                    content accept
                }

                tcp-response {
                    content accept
                }

                default_backend: db
            }

            backend db {
                mode: tcp
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 3306
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.frontends[0].tcp_request_rules
        assert ir.frontends[0].tcp_response_rules

    # ========== Backend HTTP Request/Response Single (lines 1712, 1721, 1598, 1600) ==========

    def test_backend_http_rules_comprehensive(self):
        """Test backend with comprehensive HTTP rules (lines 1712, 1721, 1598, 1600)."""
        config = """
        config test {
            backend web_servers {
                mode: http

                http-request {
                    set_header name: "X-Request-ID" value: "%{+X}o\\%ci:%cp_%fi:%fp_%Ts_%rt:%pid"
                }

                http-response {
                    set_header name: "X-Server-ID" value: "%s"
                }

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert ir.backends[0].http_request_rules
        assert ir.backends[0].http_response_rules
        assert "http-request" in output
        assert "http-response" in output

    # ========== Backend Compression (lines 2653, 2656) ==========

    def test_backend_compression_configuration(self):
        """Test backend with compression settings (lines 2653, 2656)."""
        config = """
        config test {
            backend web_servers {
                compression {
                    algo: "gzip"
                    type: ["text/html", "text/plain"]
                }

                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "compression" in output
        assert "gzip" in output

    # ========== Defaults with More Timeout Types (lines 2113, 2121-2123) ==========

    def test_defaults_all_timeout_types(self):
        """Test defaults with all timeout types (lines 2113, 2121-2123)."""
        config = """
        config test {
            defaults {
                mode: http
                timeout: {
                    connect: 5s
                    client: 30s
                    server: 30s
                    check: 10s
                    http_request: 10s
                    http_keep_alive: 2s
                }
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults
        assert ir.defaults.timeout_check == "10s"
        assert ir.defaults.timeout_http_request == "10s"
        assert ir.defaults.timeout_http_keep_alive == "2s"

    # ========== Server with Backup and Other Options (lines 2059-2062, 2086) ==========

    def test_server_comprehensive_options(self):
        """Test server with multiple options including backup and weight (lines 2059-2062, 2086)."""
        config = """
        config test {
            backend web_servers {
                servers {
                    server primary1 {
                        address: "10.0.1.1"
                        port: 8080
                        weight: 100
                        check: true
                    }
                    server primary2 {
                        address: "10.0.1.2"
                        port: 8080
                        weight: 80
                        check: true
                    }
                    server backup1 {
                        address: "10.0.2.1"
                        port: 8080
                        backup: true
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "backup" in output
        assert "weight 100" in output
        assert "weight 80" in output

    # ========== Template Expander Line 40 ==========

    def test_template_spreads_single_value_not_list(self):
        """Test template_spreads as single string (line 40 in template_expander.py)."""
        from haproxy_translator.ir.nodes import Backend, ConfigIR, Server, Template
        from haproxy_translator.transformers.template_expander import TemplateExpander

        # Create a template
        template = Template(
            name="web_template",
            parameters={"check": True, "weight": 100}
        )

        # Create a server with template_spreads as single string (not list)
        server = Server(
            name="srv1",
            address="127.0.0.1",
            port=8080,
            metadata={"template_spreads": "web_template"}  # Single string, not list!
        )

        backend = Backend(
            name="app",
            servers=[server]
        )

        config = ConfigIR(
            name="test",
            backends=[backend],
            templates={"web_template": template}
        )

        # Expand templates - this should hit line 40
        expander = TemplateExpander(config)
        expanded_ir = expander.expand()

        # Verify template was applied
        assert expanded_ir.backends[0].servers[0].check is True
        assert expanded_ir.backends[0].servers[0].weight == 100

    # ========== Variable Resolver Line 105 ==========

    def test_variable_dict_value_resolution(self):
        """Test variable with dict value requiring resolution (line 105 in variable_resolver.py)."""
        from haproxy_translator.ir.nodes import Backend, ConfigIR, Server, Variable
        from haproxy_translator.transformers.variable_resolver import VariableResolver

        # Create variables
        port_var = Variable(name="port", value="8080")
        host_var = Variable(name="host", value="localhost")
        server_config_var = Variable(
            name="server_config",
            value={"address": "${host}", "port": "${port}"}  # Dict with var refs!
        )

        config = ConfigIR(
            name="test",
            variables={
                "port": port_var,
                "host": host_var,
                "server_config": server_config_var
            },
            backends=[Backend(name="app", servers=[Server(name="srv1", address="127.0.0.1", port=8080)])]
        )

        # Resolve variables - this should hit line 105 when resolving the dict
        resolver = VariableResolver(config)
        resolved_ir = resolver.resolve()

        # Verify dict was resolved
        assert resolved_ir.variables["server_config"].value == {"address": "localhost", "port": "8080"}
