"""DSL parser using Lark."""

from importlib import resources
from pathlib import Path
from typing import cast

from lark import Lark, LarkError

from ..ir import ConfigIR
from ..transformers.dsl_transformer import DSLTransformer
from ..transformers.loop_unroller import LoopUnroller
from ..transformers.template_expander import TemplateExpander
from ..transformers.variable_resolver import VariableResolver
from ..utils.errors import ParseError, SourceLocation, ValidationError
from ..validators.semantic import SemanticValidator
from .base import ConfigParser


class DSLParser(ConfigParser):
    """Parser for HAProxy DSL format."""

    def __init__(self) -> None:
        # Load grammar file using importlib.resources (Python 3.9+)
        grammar_file = resources.files("haproxy_translator").joinpath(
            "grammars/haproxy_dsl.lark"
        )
        grammar = grammar_file.read_text()

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
        """Parse DSL source code into IR and apply transformations.

        Pipeline:
        1. Parse source to AST
        2. Transform AST to IR
        3. Expand templates (first pass - non-loop servers)
        4. Resolve variables (first pass - non-loop values)
        5. Unroll loops
        6. Expand templates (second pass - loop-generated servers)
        7. Resolve variables (second pass - loop-generated server values)
        8. Validate semantics
        """
        try:
            # Step 1: Parse with Lark
            parse_tree = self.parser.parse(source)

            # Step 2: Transform to IR
            transformer = DSLTransformer(filepath=str(filepath) if filepath else "<input>")
            ir = cast("ConfigIR", transformer.transform(parse_tree))

            # Step 3: Expand templates (first pass - for non-loop servers)
            template_expander = TemplateExpander(ir)
            ir = template_expander.expand()

            # Step 4: Resolve variables (first pass - multi-pass for nested references)
            variable_resolver = VariableResolver(ir)
            ir = variable_resolver.resolve()

            # Step 5: Unroll loops
            loop_unroller = LoopUnroller(ir)
            ir = loop_unroller.unroll()

            # Step 6: Expand templates (second pass - for loop-generated servers)
            template_expander2 = TemplateExpander(ir)
            ir = template_expander2.expand()

            # Step 7: Resolve variables (second pass - for loop-generated server values)
            variable_resolver2 = VariableResolver(ir)
            ir = variable_resolver2.resolve()

            # Step 8: Validate semantics
            validator = SemanticValidator(ir)
            return validator.validate()

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

        except (ValidationError, ParseError):
            # Re-raise validation and parse errors as-is
            raise

        except Exception as e:
            # Catch any other errors
            raise ParseError(f"Parse error: {e}") from e
