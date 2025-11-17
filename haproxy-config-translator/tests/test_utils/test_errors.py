"""Tests for error classes."""

import pytest

from haproxy_translator.utils.errors import (
    CodeGenerationError,
    ParseError,
    SourceLocation,
    TranslatorError,
    ValidationError,
    ValidationResult,
    ValidationWarning,
)


class TestSourceLocation:
    """Test SourceLocation dataclass."""

    def test_source_location_str(self):
        """Test string representation of source location."""
        loc = SourceLocation(filepath="test.hap", line=10, column=5)
        assert str(loc) == "test.hap:10:5"

    def test_source_location_with_length(self):
        """Test source location with length."""
        loc = SourceLocation(filepath="config.hap", line=20, column=10, length=5)
        assert loc.filepath == "config.hap"
        assert loc.line == 20
        assert loc.column == 10
        assert loc.length == 5


class TestTranslatorError:
    """Test TranslatorError base class."""

    def test_error_without_location(self):
        """Test error without source location."""
        error = TranslatorError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.location is None
        assert str(error) == "Something went wrong"

    def test_error_with_location(self):
        """Test error with source location."""
        loc = SourceLocation(filepath="test.hap", line=5, column=10)
        error = TranslatorError("Syntax error", location=loc)
        assert error.message == "Syntax error"
        assert error.location == loc
        assert str(error) == "test.hap:5:10: Syntax error"

    def test_error_can_be_raised(self):
        """Test that error can be raised and caught."""
        with pytest.raises(TranslatorError, match="Test error"):
            raise TranslatorError("Test error")


class TestParseError:
    """Test ParseError class."""

    def test_parse_error_without_location(self):
        """Test parse error without location."""
        error = ParseError("Invalid syntax")
        assert error.message == "Invalid syntax"
        assert isinstance(error, TranslatorError)

    def test_parse_error_with_location(self):
        """Test parse error with location."""
        loc = SourceLocation(filepath="config.hap", line=15, column=20)
        error = ParseError("Unexpected token", location=loc)
        assert str(error) == "config.hap:15:20: Unexpected token"

    def test_parse_error_inheritance(self):
        """Test that ParseError inherits from TranslatorError."""
        error = ParseError("Test")
        assert isinstance(error, ParseError)
        assert isinstance(error, TranslatorError)
        assert isinstance(error, Exception)


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_without_location(self):
        """Test validation error without location."""
        error = ValidationError("Invalid configuration")
        assert error.message == "Invalid configuration"

    def test_validation_error_with_location(self):
        """Test validation error with location."""
        loc = SourceLocation(filepath="test.hap", line=25, column=5)
        error = ValidationError("Backend not found", location=loc)
        assert str(error) == "test.hap:25:5: Backend not found"

    def test_validation_error_can_be_raised(self):
        """Test that validation error can be raised."""
        with pytest.raises(ValidationError, match="Invalid backend"):
            raise ValidationError("Invalid backend")


class TestCodeGenerationError:
    """Test CodeGenerationError class."""

    def test_codegen_error_without_location(self):
        """Test code generation error without location."""
        error = CodeGenerationError("Failed to generate config")
        assert error.message == "Failed to generate config"

    def test_codegen_error_with_location(self):
        """Test code generation error with location."""
        loc = SourceLocation(filepath="output.cfg", line=100, column=1)
        error = CodeGenerationError("Invalid output", location=loc)
        assert str(error) == "output.cfg:100:1: Invalid output"


class TestValidationWarning:
    """Test ValidationWarning class."""

    def test_warning_without_location(self):
        """Test warning without location."""
        warning = ValidationWarning("This might cause issues")
        assert warning.message == "This might cause issues"
        assert warning.location is None
        assert str(warning) == "Warning: This might cause issues"

    def test_warning_with_location(self):
        """Test warning with location."""
        loc = SourceLocation(filepath="test.hap", line=30, column=15)
        warning = ValidationWarning("Deprecated syntax", location=loc)
        assert str(warning) == "test.hap:30:15: Warning: Deprecated syntax"


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_valid_result(self):
        """Test valid validation result."""
        result = ValidationResult(valid=True, errors=[], warnings=[])
        assert result.valid is True
        assert bool(result) is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_invalid_result_with_errors(self):
        """Test invalid result with errors."""
        errors = [
            ValidationError("Error 1"),
            ValidationError("Error 2"),
        ]
        result = ValidationResult(valid=False, errors=errors, warnings=[])
        assert result.valid is False
        assert bool(result) is False
        assert len(result.errors) == 2

    def test_result_with_warnings(self):
        """Test result with warnings."""
        warnings = [
            ValidationWarning("Warning 1"),
            ValidationWarning("Warning 2"),
        ]
        result = ValidationResult(valid=True, errors=[], warnings=warnings)
        assert result.valid is True
        assert len(result.warnings) == 2

    def test_result_str_with_errors(self):
        """Test string representation with errors."""
        errors = [
            ValidationError("First error"),
            ValidationError("Second error"),
        ]
        result = ValidationResult(valid=False, errors=errors, warnings=[])
        output = str(result)
        assert "Error: First error" in output
        assert "Error: Second error" in output

    def test_result_str_with_warnings(self):
        """Test string representation with warnings."""
        warnings = [
            ValidationWarning("First warning"),
            ValidationWarning("Second warning"),
        ]
        result = ValidationResult(valid=True, errors=[], warnings=warnings)
        output = str(result)
        assert "Warning: First warning" in output
        assert "Warning: Second warning" in output

    def test_result_str_with_both(self):
        """Test string representation with both errors and warnings."""
        loc1 = SourceLocation(filepath="test.hap", line=10, column=5)
        loc2 = SourceLocation(filepath="test.hap", line=20, column=10)

        errors = [ValidationError("Critical error", location=loc1)]
        warnings = [ValidationWarning("Minor issue", location=loc2)]
        result = ValidationResult(valid=False, errors=errors, warnings=warnings)

        output = str(result)
        assert "test.hap:10:5: Critical error" in output
        assert "test.hap:20:10: Warning: Minor issue" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
