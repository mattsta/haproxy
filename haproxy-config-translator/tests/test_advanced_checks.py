"""Tests for advanced health checks and use-server directives (Phase 3)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestAdvancedHealthChecks:
    """Test advanced health check features: use-server, http-check, tcp-check."""

    # ===== use-server Directive =====

    def test_use_server_basic(self):
        """Test basic use-server directive without condition first."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                acl is_premium {
                    src "10.0.1.0/24"
                }

                default_backend: app
            }

            backend app {
                use-server premium_srv1 if is_premium

                servers {
                    server premium_srv1 {
                        address: "10.0.2.1"
                        port: 8080
                    }
                    server regular_srv1 {
                        address: "10.0.3.1"
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

        assert len(ir.backends[0].use_server_rules) == 1
        assert ir.backends[0].use_server_rules[0].server == "premium_srv1"
        assert "if is_premium" in ir.backends[0].use_server_rules[0].condition

        assert "use-server premium_srv1 if is_premium" in output

    def test_use_server_multiple(self):
        """Test multiple use-server directives."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                acl is_vip {
                    src "10.0.1.0/24"
                }
                acl is_premium {
                    src "10.0.2.0/24"
                }

                default_backend: app
            }

            backend app {
                use-server vip_srv if is_vip
                use-server premium_srv if is_premium

                servers {
                    server vip_srv {
                        address: "10.0.5.1"
                        port: 8080
                    }
                    server premium_srv {
                        address: "10.0.5.2"
                        port: 8080
                    }
                    server regular_srv {
                        address: "10.0.5.3"
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

        assert len(ir.backends[0].use_server_rules) == 2
        assert "use-server vip_srv if is_vip" in output
        assert "use-server premium_srv if is_premium" in output

    # ===== http-check Directives =====

    def test_http_check_send_basic(self):
        """Test basic http-check send directive."""
        config = """
        config test {
            backend api {
                http-check {
                    send method "GET" uri "/health"
                    expect status 200
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert len(ir.backends[0].http_check_rules) == 2
        assert ir.backends[0].http_check_rules[0].type == "send"
        assert ir.backends[0].http_check_rules[0].method == "GET"
        assert ir.backends[0].http_check_rules[0].uri == "/health"

        assert ir.backends[0].http_check_rules[1].type == "expect"
        assert ir.backends[0].http_check_rules[1].expect_type == "status"
        assert ir.backends[0].http_check_rules[1].expect_value == 200

        assert "http-check send meth GET uri /health" in output
        assert "http-check expect status 200" in output

    def test_http_check_expect_string(self):
        """Test http-check expect with string match."""
        config = """
        config test {
            backend api {
                http-check {
                    send method "GET" uri "/api/status"
                    expect string "OK"
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].http_check_rules[1].expect_type == "string"
        assert ir.backends[0].http_check_rules[1].expect_value == "OK"

        assert "http-check expect string OK" in output

    def test_http_check_expect_rstatus(self):
        """Test http-check expect with regex status match."""
        config = """
        config test {
            backend api {
                http-check {
                    send method "HEAD" uri "/ping"
                    expect rstatus "^2[0-9][0-9]$"
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].http_check_rules[1].expect_type == "rstatus"
        assert ir.backends[0].http_check_rules[1].expect_value == "^2[0-9][0-9]$"

        assert "http-check expect rstatus ^2[0-9][0-9]$" in output

    def test_http_check_connect(self):
        """Test http-check connect directive."""
        config = """
        config test {
            backend api {
                http-check {
                    connect port 8443
                    send method "GET" uri "/health"
                    expect status 200
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].http_check_rules[0].type == "connect"
        assert ir.backends[0].http_check_rules[0].port == 8443

        assert "http-check connect port 8443" in output

    # ===== tcp-check Directives =====

    def test_tcp_check_connect_send_expect(self):
        """Test tcp-check with connect, send, and expect."""
        config = """
        config test {
            backend redis {
                mode: tcp

                tcp-check {
                    connect port 6379
                    send "PING\\r\\n"
                    expect string "PONG"
                }

                servers {
                    server redis1 {
                        address: "10.0.1.1"
                        port: 6379
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert len(ir.backends[0].tcp_check_rules) == 3
        assert ir.backends[0].tcp_check_rules[0].type == "connect"
        assert ir.backends[0].tcp_check_rules[0].port == 6379

        assert ir.backends[0].tcp_check_rules[1].type == "send"
        assert "PING" in ir.backends[0].tcp_check_rules[1].data

        assert ir.backends[0].tcp_check_rules[2].type == "expect"
        assert "PONG" in ir.backends[0].tcp_check_rules[2].pattern

        assert "tcp-check connect port 6379" in output
        assert "tcp-check send" in output
        assert "tcp-check expect" in output

    def test_tcp_check_send_binary(self):
        """Test tcp-check with send-binary."""
        config = """
        config test {
            backend custom {
                mode: tcp

                tcp-check {
                    send-binary "0x48454C4C4F"
                    expect string "WORLD"
                }

                servers {
                    server srv1 {
                        address: "10.0.1.1"
                        port: 9000
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].tcp_check_rules[0].type == "send-binary"
        assert "0x48454C4C4F" in ir.backends[0].tcp_check_rules[0].data

        assert "tcp-check send-binary 0x48454C4C4F" in output

    def test_tcp_check_comment(self):
        """Test tcp-check with comment."""
        config = """
        config test {
            backend postgres {
                mode: tcp

                tcp-check {
                    comment "PostgreSQL health check"
                    connect port 5432
                    expect string "PostgreSQL"
                }

                servers {
                    server pg1 {
                        address: "10.0.1.1"
                        port: 5432
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].tcp_check_rules[0].type == "comment"
        assert "PostgreSQL health check" in ir.backends[0].tcp_check_rules[0].comment

        assert "tcp-check comment PostgreSQL health check" in output

    # ===== Integration Tests =====

    def test_all_advanced_features_together(self):
        """Test use-server, http-check, and routing together."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                acl is_admin {
                    src "10.0.0.0/8"
                }

                default_backend: api
            }

            backend api {
                mode: http

                use-server admin_api if is_admin

                http-check {
                    send method "GET" uri "/api/health"
                    expect status 200
                }

                servers {
                    server admin_api {
                        address: "10.0.1.1"
                        port: 8080
                    }
                    server regular_api {
                        address: "10.0.2.1"
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

        # Verify IR
        assert len(ir.backends[0].use_server_rules) == 1
        assert len(ir.backends[0].http_check_rules) == 2
        assert len(ir.backends[0].servers) == 2

        # Verify output
        assert "use-server admin_api if is_admin" in output
        assert "http-check send meth GET uri /api/health" in output
        assert "http-check expect status 200" in output


class TestHttpCheckCoverageGaps:
    """Tests for HTTP check edge cases to improve coverage."""

    def test_http_check_send_with_headers(self):
        """Test http-check send with custom headers."""
        config = """
        config test {
            backend api {
                http-check {
                    send method "GET" uri "/health" headers { header "X-Health-Check" "true" header "Accept" "application/json" }
                    expect status 200
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].http_check_rules[0].type == "send"
        assert ir.backends[0].http_check_rules[0].headers is not None
        assert "X-Health-Check" in ir.backends[0].http_check_rules[0].headers

        assert "http-check send meth GET uri /health" in output
        assert "hdr X-Health-Check true" in output
        assert "hdr Accept application/json" in output

    def test_http_check_expect_negate(self):
        """Test http-check expect with negation using ! syntax."""
        config = """
        config test {
            backend api {
                http-check {
                    send method "GET" uri "/health"
                    expect ! status 500
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].http_check_rules[1].type == "expect"
        assert ir.backends[0].http_check_rules[1].expect_negate is True

        assert "http-check expect ! status 500" in output

    def test_http_check_expect_rstring(self):
        """Test http-check expect with regex string match."""
        config = """
        config test {
            backend api {
                http-check {
                    send method "GET" uri "/api/status"
                    expect rstring ".*healthy.*"
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.backends[0].http_check_rules[1].expect_type == "rstring"
        assert ir.backends[0].http_check_rules[1].expect_value == ".*healthy.*"

        assert "http-check expect rstring .*healthy.*" in output

    def test_http_check_connect_ssl_options(self):
        """Test http-check connect with SSL options."""
        config = """
        config test {
            backend api {
                http-check {
                    connect port 8443 ssl sni "api.example.com" alpn "h2,http/1.1"
                    send method "GET" uri "/health"
                    expect status 200
                }

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8443
                        ssl: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        connect_rule = ir.backends[0].http_check_rules[0]
        assert connect_rule.type == "connect"
        assert connect_rule.port == 8443
        assert connect_rule.ssl is True
        assert connect_rule.sni == "api.example.com"
        assert connect_rule.alpn == "h2,http/1.1"

        assert "http-check connect port 8443 ssl sni api.example.com alpn h2,http/1.1" in output

    def test_http_check_disable_on_404(self):
        """Test http-check disable-on-404 directive."""
        config = """
        config test {
            backend api {
                http-check {
                    send method "GET" uri "/health"
                    expect status 200
                    disable-on-404
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
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Find the disable-on-404 rule
        disable_rule = [r for r in ir.backends[0].http_check_rules if r.type == "disable-on-404"]
        assert len(disable_rule) == 1

        assert "http-check disable-on-404" in output


class TestTcpCheckCoverageGaps:
    """Tests for TCP check edge cases to improve coverage."""

    def test_tcp_check_connect_ssl_options(self):
        """Test tcp-check connect with SSL options."""
        config = """
        config test {
            backend secure_redis {
                mode: tcp

                tcp-check {
                    connect port 6380 ssl sni "redis.example.com" alpn "redis"
                    send "PING\\r\\n"
                    expect string "PONG"
                }

                servers {
                    server redis1 {
                        address: "10.0.1.1"
                        port: 6380
                        ssl: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        connect_rule = ir.backends[0].tcp_check_rules[0]
        assert connect_rule.type == "connect"
        assert connect_rule.port == 6380
        assert connect_rule.ssl is True
        assert connect_rule.sni == "redis.example.com"
        assert connect_rule.alpn == "redis"

        assert "tcp-check connect port 6380 ssl sni redis.example.com alpn redis" in output

    def test_tcp_check_empty_type_fallback(self):
        """Test tcp-check with unknown type returns empty string."""
        from haproxy_translator.ir.nodes import TcpCheckRule
        codegen = HAProxyCodeGenerator()

        # Create a tcp-check with an unknown type to hit the fallback
        unknown_rule = TcpCheckRule(type="unknown")
        result = codegen._format_tcp_check_rule(unknown_rule)
        assert result == ""

    def test_http_check_empty_type_fallback(self):
        """Test http-check with unknown type returns empty string."""
        from haproxy_translator.ir.nodes import HttpCheckRule
        codegen = HAProxyCodeGenerator()

        # Create a http-check with an unknown type to hit the fallback
        unknown_rule = HttpCheckRule(type="unknown")
        result = codegen._format_http_check_rule(unknown_rule)
        assert result == ""
