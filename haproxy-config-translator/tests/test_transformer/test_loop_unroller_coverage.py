"""Tests to cover loop_unroller coverage gaps."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.utils.errors import ParseError


class TestLoopUnrollerCoverage:
    """Test cases to achieve 100% loop_unroller coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_for_loop_with_list_iterable(self, parser, codegen):
        """Test for loop with a list iterable."""
        source = """
        config test {
            backend app {
                servers {
                    for dc in ["us-east", "us-west", "eu-central"] {
                        server ${dc}-srv {
                            address: "${dc}.example.com"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "us-east-srv us-east.example.com:8080" in output
        assert "us-west-srv us-west.example.com:8080" in output
        assert "eu-central-srv eu-central.example.com:8080" in output

    def test_for_loop_with_expression(self, parser, codegen):
        """Test for loop with expression substitution."""
        source = """
        config test {
            backend app {
                servers {
                    for i in 1..3 {
                        server web${i * 10} {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)
        assert "web10 10.0.1.1:8080" in output
        assert "web20 10.0.1.2:8080" in output
        assert "web30 10.0.1.3:8080" in output

    def test_for_loop_with_invalid_iterable(self, parser, codegen):
        """Test for loop with unsupported iterable type raises error."""
        # This would need to be constructed programmatically since
        # the grammar doesn't allow invalid iterables
        from haproxy_translator.ir.nodes import Backend, ForLoop, Server, ConfigIR
        from haproxy_translator.transformers.loop_unroller import LoopUnroller

        # Create a loop with invalid iterable (a string instead of tuple/list)
        loop = ForLoop(
            variable="i",
            iterable="invalid",  # String is not a valid iterable
            body=[Server(name="test", address="10.0.1.1", port=8080)]
        )

        backend = Backend(
            name="test",
            servers=[],
            metadata={"server_loops": loop}
        )

        config = ConfigIR(
            name="test",
            backends=[backend],
            frontends=[],
            defaults=None,
            global_config=None
        )

        unroller = LoopUnroller(config)
        with pytest.raises(ParseError, match="Unsupported iterable type"):
            unroller.unroll()

    def test_for_loop_with_expression_error(self, parser, codegen):
        """Test for loop with invalid expression raises error."""
        source = """
        config test {
            backend app {
                servers {
                    for i in 1..2 {
                        server web${undefined_var} {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        # This should raise an error during loop unrolling
        with pytest.raises(ParseError, match="Failed to evaluate expression"):
            ir = parser.parse(source)

    def test_backend_with_single_loop_not_list(self, parser, codegen):
        """Test backend with single loop (not wrapped in list) in metadata."""
        # This tests the code path where loops is not a list and gets converted
        from haproxy_translator.ir.nodes import Backend, ForLoop, Server, ConfigIR
        from haproxy_translator.transformers.loop_unroller import LoopUnroller

        # Create a loop
        loop = ForLoop(
            variable="i",
            iterable=(1, 2),
            body=[Server(name="srv${i}", address="10.0.1.${i}", port=8080)]
        )

        # Store single loop (not as list) in metadata
        backend = Backend(
            name="test",
            servers=[],
            metadata={"server_loops": loop}  # Single loop, not [loop]
        )

        config = ConfigIR(
            name="test",
            backends=[backend],
            frontends=[],
            defaults=None,
            global_config=None
        )

        unroller = LoopUnroller(config)
        result = unroller.unroll()

        # Should have 2 servers
        assert len(result.backends[0].servers) == 2

    def test_backend_with_non_forloop_in_metadata(self, parser, codegen):
        """Test backend with non-ForLoop items in server_loops metadata."""
        from haproxy_translator.ir.nodes import Backend, ConfigIR
        from haproxy_translator.transformers.loop_unroller import LoopUnroller

        # Create a backend with invalid loop item
        backend = Backend(
            name="test",
            servers=[],
            metadata={"server_loops": ["not a ForLoop object", "another invalid"]}
        )

        config = ConfigIR(
            name="test",
            backends=[backend],
            frontends=[],
            defaults=None,
            global_config=None
        )

        unroller = LoopUnroller(config)
        result = unroller.unroll()

        # Should just skip invalid items and return empty servers
        assert len(result.backends[0].servers) == 0

    def test_for_loop_with_nested_list_body(self, parser, codegen):
        """Test for loop with nested list in body."""
        # This would need to be constructed programmatically
        from haproxy_translator.ir.nodes import Backend, ForLoop, Server, ConfigIR
        from haproxy_translator.transformers.loop_unroller import LoopUnroller

        server1 = Server(name="srv${i}", address="10.0.1.${i}", port=8080)
        server2 = Server(name="srv${i}-backup", address="10.0.2.${i}", port=8080)

        # Create a loop with nested list in body
        loop = ForLoop(
            variable="i",
            iterable=(1, 2),
            body=[[server1, server2]]  # Nested list structure
        )

        backend = Backend(
            name="test",
            servers=[],
            metadata={"server_loops": [loop]}
        )

        config = ConfigIR(
            name="test",
            backends=[backend],
            frontends=[],
            defaults=None,
            global_config=None
        )

        unroller = LoopUnroller(config)
        result = unroller.unroll()

        # Should have 4 servers (2 iterations × 2 servers per iteration)
        assert len(result.backends[0].servers) == 4
