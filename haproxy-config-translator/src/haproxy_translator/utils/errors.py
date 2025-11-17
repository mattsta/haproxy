"""Error classes for HAProxy translator."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceLocation:
    """Source code location for error reporting."""

    filepath: str
    line: int
    column: int
    length: int = 1

    def __str__(self) -> str:
        return f"{self.filepath}:{self.line}:{self.column}"


class TranslatorError(Exception):
    """Base exception for translator errors."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        self.message = message
        self.location = location
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.location:
            return f"{self.location}: {self.message}"
        return self.message


class ParseError(TranslatorError):
    """Error during parsing."""

    pass


class ValidationError(TranslatorError):
    """Error during validation."""

    pass


class ValidationWarning:
    """Warning during validation (non-fatal)."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        self.message = message
        self.location = location

    def __str__(self) -> str:
        if self.location:
            return f"{self.location}: Warning: {self.message}"
        return f"Warning: {self.message}"


class CodeGenerationError(TranslatorError):
    """Error during code generation."""

    pass


@dataclass
class ValidationResult:
    """Result of validation."""

    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]

    def __bool__(self) -> bool:
        return self.valid

    def __str__(self) -> str:
        lines = []
        for error in self.errors:
            lines.append(f"Error: {error}")
        for warning in self.warnings:
            lines.append(str(warning))
        return "\n".join(lines)
