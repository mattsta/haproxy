"""Tests for base parser classes."""

import tempfile
from pathlib import Path

import pytest

from haproxy_translator.ir import ConfigIR
from haproxy_translator.parsers.base import ConfigParser, ParserRegistry
from haproxy_translator.utils.errors import ParseError


# Mock parser for testing
class MockParser(ConfigParser):
    """Mock parser for testing base functionality."""

    @property
    def format_name(self) -> str:
        return "mock"

    @property
    def file_extensions(self) -> list[str]:
        return [".mock", ".test"]

    def parse(self, source: str, filepath: Path | None = None) -> ConfigIR:
        if "INVALID" in source:
            raise ParseError("Invalid syntax")
        return ConfigIR(name="mock_config")


class AnotherMockParser(ConfigParser):
    """Another mock parser for registry testing."""

    @property
    def format_name(self) -> str:
        return "another"

    @property
    def file_extensions(self) -> list[str]:
        return [".other"]

    def parse(self, source: str, filepath: Path | None = None) -> ConfigIR:
        return ConfigIR(name="another_config")


class TestConfigParser:
    """Test ConfigParser base class."""

    @pytest.fixture
    def parser(self):
        """Create mock parser."""
        return MockParser()

    def test_format_name(self, parser):
        """Test format name property."""
        assert parser.format_name == "mock"

    def test_file_extensions(self, parser):
        """Test file extensions property."""
        assert parser.file_extensions == [".mock", ".test"]

    def test_parse_valid_source(self, parser):
        """Test parsing valid source."""
        ir = parser.parse("valid config")
        assert isinstance(ir, ConfigIR)
        assert ir.name == "mock_config"

    def test_parse_invalid_source(self, parser):
        """Test parsing invalid source."""
        with pytest.raises(ParseError, match="Invalid syntax"):
            parser.parse("INVALID config")

    def test_parse_file_valid(self, parser):
        """Test parsing valid file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mock", delete=False) as f:
            f.write("valid config")
            filepath = Path(f.name)

        try:
            ir = parser.parse_file(filepath)
            assert isinstance(ir, ConfigIR)
            assert ir.name == "mock_config"
        finally:
            filepath.unlink()

    def test_parse_file_not_found(self, parser):
        """Test parsing non-existent file."""
        filepath = Path("/tmp/nonexistent.mock")
        with pytest.raises(ParseError, match="File not found"):
            parser.parse_file(filepath)

    def test_parse_file_invalid_content(self, parser):
        """Test parsing file with invalid content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mock", delete=False) as f:
            f.write("INVALID config")
            filepath = Path(f.name)

        try:
            with pytest.raises(ParseError, match="Invalid syntax"):
                parser.parse_file(filepath)
        finally:
            filepath.unlink()

    def test_validate_syntax_valid(self, parser):
        """Test syntax validation with valid source."""
        errors = parser.validate_syntax("valid config")
        assert len(errors) == 0

    def test_validate_syntax_invalid(self, parser):
        """Test syntax validation with invalid source."""
        errors = parser.validate_syntax("INVALID config")
        assert len(errors) == 1
        assert isinstance(errors[0], ParseError)
        assert "Invalid syntax" in str(errors[0])


class TestParserRegistry:
    """Test ParserRegistry class."""

    def setup_method(self):
        """Clear registry before each test."""
        ParserRegistry._parsers = {}
        ParserRegistry._extension_map = {}

    def test_register_parser(self):
        """Test registering a parser."""
        ParserRegistry.register(MockParser)

        assert "mock" in ParserRegistry._parsers
        assert ".mock" in ParserRegistry._extension_map
        assert ".test" in ParserRegistry._extension_map
        assert ParserRegistry._extension_map[".mock"] == "mock"

    def test_register_multiple_parsers(self):
        """Test registering multiple parsers."""
        ParserRegistry.register(MockParser)
        ParserRegistry.register(AnotherMockParser)

        assert len(ParserRegistry._parsers) == 2
        assert "mock" in ParserRegistry._parsers
        assert "another" in ParserRegistry._parsers

    def test_get_parser_by_format_name(self):
        """Test getting parser by format name."""
        ParserRegistry.register(MockParser)

        parser = ParserRegistry.get_parser(format_name="mock")
        assert isinstance(parser, MockParser)
        assert parser.format_name == "mock"

    def test_get_parser_unknown_format(self):
        """Test getting parser with unknown format."""
        with pytest.raises(ValueError, match="Unknown format: unknown"):
            ParserRegistry.get_parser(format_name="unknown")

    def test_get_parser_by_filepath(self):
        """Test getting parser by filepath extension."""
        ParserRegistry.register(MockParser)

        parser = ParserRegistry.get_parser(filepath=Path("test.mock"))
        assert isinstance(parser, MockParser)

        parser = ParserRegistry.get_parser(filepath=Path("test.test"))
        assert isinstance(parser, MockParser)

    def test_get_parser_unknown_extension(self):
        """Test getting parser with unknown extension."""
        ParserRegistry.register(MockParser)

        with pytest.raises(ValueError, match="Cannot determine parser for file extension"):
            ParserRegistry.get_parser(filepath=Path("test.unknown"))

    def test_get_parser_no_args(self):
        """Test getting parser with no arguments."""
        with pytest.raises(ValueError, match="Must specify either format_name or filepath"):
            ParserRegistry.get_parser()

    def test_list_formats(self):
        """Test listing registered formats."""
        ParserRegistry.register(MockParser)
        ParserRegistry.register(AnotherMockParser)

        formats = ParserRegistry.list_formats()
        assert len(formats) == 2
        assert "mock" in formats
        assert "another" in formats

    def test_list_extensions(self):
        """Test listing registered extensions."""
        ParserRegistry.register(MockParser)
        ParserRegistry.register(AnotherMockParser)

        extensions = ParserRegistry.list_extensions()
        assert len(extensions) == 3
        assert extensions[".mock"] == "mock"
        assert extensions[".test"] == "mock"
        assert extensions[".other"] == "another"

    def test_list_formats_empty(self):
        """Test listing formats when registry is empty."""
        formats = ParserRegistry.list_formats()
        assert formats == []

    def test_list_extensions_empty(self):
        """Test listing extensions when registry is empty."""
        extensions = ParserRegistry.list_extensions()
        assert extensions == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
