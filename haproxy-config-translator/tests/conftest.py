"""Pytest fixtures for haproxy-config-translator tests."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


@pytest.fixture
def parser():
    """Return a DSL parser instance."""
    return DSLParser()


@pytest.fixture
def codegen():
    """Return a code generator instance."""
    return HAProxyCodeGenerator()
