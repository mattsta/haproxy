"""DSL parser using Lark."""

from importlib import resources
from pathlib import Path
from typing import cast

from lark import Lark, LarkError

from ..ir import ConfigIR
from ..transformers.dsl_transformer import DSLTransformer
from ..utils.errors import ParseError, SourceLocation
from .base import ConfigParser


class DSLParser(ConfigParser):
    """Parser for HAProxy DSL format."""

    def __init__(self) -> None:
        # Load grammar file using importlib.resources
        try:
            # Python 3.9+
            grammar_file = resources.files("haproxy_translator").joinpath(
                "grammars/haproxy_dsl.lark"
            )
            grammar = grammar_file.read_text()
        except AttributeError:
            # Python 3.7-3.8 fallback
            with resources.open_text("haproxy_translator.grammars", "haproxy_dsl.lark") as f:
                grammar = f.read()

        self.parser = Lark(
            grammar,
            start="config",
            parser="earley",  # Earley parser - handles ambiguity better than LALR
            # ambiguity="resolve" - automatically resolves ambiguities (default)
            propagate_positions=True,  # Track source positions
            maybe_placeholders=False,
        )

    @property
    def format_name(self) -> str:
        return "dsl"

    @property
    def file_extensions(self) -> list[str]:
        return [".hap", ".haproxy"]

    def parse(self, source: str, filepath: Path | None = None) -> ConfigIR:
        """Parse DSL source code into IR."""
        try:
            # Parse with Lark
            parse_tree = self.parser.parse(source)

            # Transform to IR
            transformer = DSLTransformer(filepath=str(filepath) if filepath else "<input>")
            return cast("ConfigIR", transformer.transform(parse_tree))

        except LarkError as e:
            # Convert Lark error to ParseError
            location = None
            if hasattr(e, "line") and hasattr(e, "column"):
                location = SourceLocation(
                    filepath=str(filepath) if filepath else "<input>",
                    line=e.line,
                    column=e.column,
                )

            raise ParseError(f"Syntax error: {e}", location=location) from e

        except Exception as e:
            # Catch any other errors
            raise ParseError(f"Parse error: {e}") from e
