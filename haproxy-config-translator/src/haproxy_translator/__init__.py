"""HAProxy Configuration Translator.

A modern, powerful configuration translation system for HAProxy.
"""

__version__ = "0.1.0"

from .parsers.base import ConfigParser, ParserRegistry
from .ir.nodes import ConfigIR
from .codegen.haproxy import HAProxyCodeGenerator

__all__ = [
    "ConfigParser",
    "ParserRegistry",
    "ConfigIR",
    "HAProxyCodeGenerator",
]
