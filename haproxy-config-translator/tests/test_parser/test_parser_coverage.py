"""Tests to cover dsl_parser coverage gaps."""

from unittest.mock import patch

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.utils.errors import ParseError


class TestParserCoverage:
    """Test cases to achieve 100% parser coverage."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_generic_exception_handling(self, parser):
        """Test generic exception handling during transformation."""
        # We need to cause an exception that's not ValidationError or ParseError
        # during the transformation phase

        # Mock DSLTransformer to raise a generic exception
        with patch(
            "haproxy_translator.parsers.dsl_parser.DSLTransformer"
        ) as mock_transformer_class:
            mock_transformer = mock_transformer_class.return_value
            mock_transformer.transform.side_effect = RuntimeError("Unexpected transformer error")

            source = """
            config test {
                frontend web {
                    bind *:80
                }
            }
            """

            with pytest.raises(ParseError, match="Parse error: Unexpected transformer error"):
                parser.parse(source)

    def test_grammar_loading_python39_path(self, parser):
        """Test that grammar is loaded successfully (Python 3.9+ path)."""
        # This just verifies the normal path works
        source = """
        config test {
            frontend web {
                bind *:80
                default_backend: app
            }
            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        assert ir is not None
        assert len(ir.frontends) == 1
        assert len(ir.backends) == 1
