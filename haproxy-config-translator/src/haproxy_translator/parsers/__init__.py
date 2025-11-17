"""Parsers for different configuration formats."""

from .base import ConfigParser, ParserRegistry
from .dsl_parser import DSLParser

# Auto-register parsers
ParserRegistry.register(DSLParser)

__all__ = [
    "ConfigParser",
    "ParserRegistry",
    "DSLParser",
]
