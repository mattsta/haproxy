"""Test enhanced http-check expect capabilities."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHealthCheckExpect:
    """Test http-check expect enhancements: string, rstatus, rstring, negation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_expect_status(self, parser, codegen):
        """Test basic expect status (existing functionality)."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: status 200
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_status == 200
        assert hc.expect_string is None
        assert hc.expect_negate is False

        output = codegen.generate(ir)
        assert "http-check send meth GET uri /health" in output
        assert "http-check expect status 200" in output

    def test_expect_string(self, parser, codegen):
        """Test expect string pattern."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: string "OK"
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_status is None
        assert hc.expect_string == "OK"
        assert hc.expect_negate is False

        output = codegen.generate(ir)
        assert "http-check expect string OK" in output

    def test_expect_rstatus(self, parser, codegen):
        """Test expect rstatus (regex status pattern)."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: rstatus "^2[0-9][0-9]$"
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_status is None
        assert hc.expect_rstatus == "^2[0-9][0-9]$"
        assert hc.expect_negate is False

        output = codegen.generate(ir)
        assert "http-check expect rstatus ^2[0-9][0-9]$" in output

    def test_expect_rstring(self, parser, codegen):
        """Test expect rstring (regex string pattern)."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: rstring "status.*ok"
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_rstring == "status.*ok"
        assert hc.expect_negate is False

        output = codegen.generate(ir)
        assert "http-check expect rstring status.*ok" in output

    def test_expect_not_status(self, parser, codegen):
        """Test expect !status (negated status)."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: !status 503
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_status == 503
        assert hc.expect_negate is True

        output = codegen.generate(ir)
        assert "http-check expect ! status 503" in output

    def test_expect_not_string(self, parser, codegen):
        """Test expect !string (negated string)."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: !string "error"
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_string == "error"
        assert hc.expect_negate is True

        output = codegen.generate(ir)
        assert "http-check expect ! string error" in output

    def test_expect_not_rstatus(self, parser, codegen):
        """Test expect !rstatus (negated regex status)."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: !rstatus "^5[0-9][0-9]$"
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_rstatus == "^5[0-9][0-9]$"
        assert hc.expect_negate is True

        output = codegen.generate(ir)
        assert "http-check expect ! rstatus ^5[0-9][0-9]$" in output

    def test_expect_not_rstring(self, parser, codegen):
        """Test expect !rstring (negated regex string)."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/health"
                    expect: !rstring "(error|fail|exception)"
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_rstring == "(error|fail|exception)"
        assert hc.expect_negate is True

        output = codegen.generate(ir)
        assert "http-check expect ! rstring (error|fail|exception)" in output

    def test_production_health_check_with_regex(self, parser, codegen):
        """Test production health check with regex patterns."""
        source = """
        config production {
            backend api {
                balance: leastconn
                health-check {
                    method: "GET"
                    uri: "/api/health"
                    expect: rstatus "^2[0-9][0-9]$"
                }
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.method == "GET"
        assert hc.uri == "/api/health"
        assert hc.expect_rstatus == "^2[0-9][0-9]$"
        assert hc.expect_negate is False

        output = codegen.generate(ir)
        assert "http-check send meth GET uri /api/health" in output
        assert "http-check expect rstatus ^2[0-9][0-9]$" in output

    def test_health_check_negative_string_pattern(self, parser, codegen):
        """Test health check ensuring response doesn't contain error keywords."""
        source = """
        config test {
            backend api {
                balance: roundrobin
                health-check {
                    method: "GET"
                    uri: "/status"
                    expect: !rstring "(?i)(error|fail|down|unavailable)"
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
        backend = ir.backends[0]
        hc = backend.health_check

        assert hc.expect_rstring == "(?i)(error|fail|down|unavailable)"
        assert hc.expect_negate is True

        output = codegen.generate(ir)
        assert "http-check expect ! rstring (?i)(error|fail|down|unavailable)" in output
