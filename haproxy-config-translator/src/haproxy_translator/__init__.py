"""HAProxy Configuration Translator.

A modern, powerful configuration translation system for HAProxy.
"""

__version__ = "0.1.0"

from .codegen.haproxy import HAProxyCodeGenerator
from .ir.nodes import ConfigIR
from .parsers.base import ConfigParser, ParserRegistry

__all__ = [
    "ConfigIR",
    "ConfigParser",
    "HAProxyCodeGenerator",
    "ParserRegistry",
]
