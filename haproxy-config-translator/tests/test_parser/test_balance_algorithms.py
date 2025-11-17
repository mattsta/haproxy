"""Test all balance algorithm parsing and generation."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestBalanceAlgorithms:
    """Test all supported balance algorithms."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    @pytest.mark.parametrize("algorithm", [
        "roundrobin",
        "leastconn",
        "source",
        "uri",
        "url_param",
        "random",
        "static-rr",
        "first",
        "hdr",
        "rdp-cookie",
    ])
    def test_balance_algorithm(self, parser, codegen, algorithm):
        """Test each balance algorithm."""
        source = f"""
        config test {{
            backend servers {{
                balance: {algorithm}
                servers {{
                    server web1 {{
                        address: "10.0.1.1"
                        port: 8080
                    }}
                    server web2 {{
                        address: "10.0.1.2"
                        port: 8080
                    }}
                }}
            }}
        }}
        """
        ir = parser.parse(source)
        assert len(ir.backends) == 1
        backend = ir.backends[0]
        assert backend.balance.value == algorithm.replace("-", "-")  # Keep original format

        # Test code generation
        output = codegen.generate(ir)
        assert f"balance {algorithm}" in output
