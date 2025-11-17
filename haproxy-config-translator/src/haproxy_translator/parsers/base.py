"""Base parser interface and registry for pluggable parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..ir import ConfigIR
from ..utils.errors import ParseError


class ConfigParser(ABC):
    """Base class for all configuration format parsers."""

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the name of this format (e.g., 'dsl', 'yaml', 'hcl')."""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Return supported file extensions (e.g., ['.hap', '.haproxy'])."""
        pass

    @abstractmethod
    def parse(self, source: str, filepath: Optional[Path] = None) -> ConfigIR:
        """
        Parse source code into intermediate representation.

        Args:
            source: Source code as string
            filepath: Optional path for error reporting and imports

        Returns:
            ConfigIR: Intermediate representation

        Raises:
            ParseError: If source cannot be parsed
        """
        pass

    def parse_file(self, filepath: Path) -> ConfigIR:
        """
        Parse a file.

        Args:
            filepath: Path to file

        Returns:
            ConfigIR: Intermediate representation

        Raises:
            ParseError: If file cannot be parsed
        """
        if not filepath.exists():
            raise ParseError(f"File not found: {filepath}")

        source = filepath.read_text(encoding="utf-8")
        return self.parse(source, filepath)

    def validate_syntax(self, source: str) -> list[ParseError]:
        """
        Validate syntax without full parsing.

        Returns:
            List of syntax errors (empty if valid)
        """
        try:
            self.parse(source)
            return []
        except ParseError as e:
            return [e]


class ParserRegistry:
    """Registry for all available parsers."""

    _parsers: dict[str, type[ConfigParser]] = {}
    _extension_map: dict[str, str] = {}

    @classmethod
    def register(cls, parser_class: type[ConfigParser]) -> None:
        """Register a parser class."""
        parser = parser_class()
        cls._parsers[parser.format_name] = parser_class

        for ext in parser.file_extensions:
            cls._extension_map[ext] = parser.format_name

    @classmethod
    def get_parser(
        cls, format_name: Optional[str] = None, filepath: Optional[Path] = None
    ) -> ConfigParser:
        """Get parser by format name or auto-detect from file extension."""
        if format_name:
            if format_name not in cls._parsers:
                raise ValueError(
                    f"Unknown format: {format_name}. "
                    f"Available formats: {', '.join(cls._parsers.keys())}"
                )
            return cls._parsers[format_name]()

        if filepath:
            ext = filepath.suffix
            if ext in cls._extension_map:
                format_name = cls._extension_map[ext]
                return cls._parsers[format_name]()
            else:
                raise ValueError(
                    f"Cannot determine parser for file extension: {ext}. "
                    f"Supported extensions: {', '.join(cls._extension_map.keys())}"
                )

        raise ValueError("Must specify either format_name or filepath")

    @classmethod
    def list_formats(cls) -> list[str]:
        """List all registered format names."""
        return list(cls._parsers.keys())

    @classmethod
    def list_extensions(cls) -> dict[str, str]:
        """List all registered extensions and their format names."""
        return dict(cls._extension_map)
