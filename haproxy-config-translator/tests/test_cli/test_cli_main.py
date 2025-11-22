"""Tests for CLI main module."""

import tempfile
from pathlib import Path

import pytest


class TestTranslateOnce:
    """Test single translation functionality."""

    def test_translate_valid_config(self):
        """Test translating a valid configuration file."""
        from haproxy_translator.cli.main import _translate_once

        with tempfile.NamedTemporaryFile(suffix=".hap", delete=False, mode="w") as f:
            f.write('''
            config test {
                frontend web {
                    bind *:80
                    mode: http
                    default_backend: app
                }
                backend app {
                    balance: roundrobin
                    servers {
                        server s1 { address: "10.0.0.1" port: 8080 }
                    }
                }
            }
            ''')
            config_path = Path(f.name)

        try:
            # Test with default output (stdout)
            _translate_once(
                config_file=config_path,
                output=None,
                format=None,
                validate=True,
                debug=False,
                lua_dir=None,
                verbose=False,
            )
        finally:
            config_path.unlink(missing_ok=True)

    def test_translate_to_file(self):
        """Test translating to an output file."""
        from haproxy_translator.cli.main import _translate_once

        with tempfile.NamedTemporaryFile(suffix=".hap", delete=False, mode="w") as f:
            f.write('''
            config test {
                frontend web {
                    bind *:80
                    mode: http
                    default_backend: app
                }
                backend app {
                    balance: roundrobin
                    servers {
                        server s1 { address: "10.0.0.1" port: 8080 }
                    }
                }
            }
            ''')
            config_path = Path(f.name)

        # Create output file path (file doesn't exist yet)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.cfg"

            try:
                _translate_once(
                    config_file=config_path,
                    output=output_path,
                    format=None,
                    validate=False,  # Must be False to actually generate output
                    debug=False,
                    lua_dir=None,
                    verbose=False,
                )

                # Verify output was written
                assert output_path.exists()
                content = output_path.read_text()
                assert "frontend web" in content
                assert "backend app" in content
            finally:
                config_path.unlink(missing_ok=True)

    def test_translate_verbose_mode(self):
        """Test translation with verbose mode."""
        from haproxy_translator.cli.main import _translate_once

        with tempfile.NamedTemporaryFile(suffix=".hap", delete=False, mode="w") as f:
            f.write('''
            config test {
                frontend web {
                    bind *:80
                    mode: http
                    default_backend: app
                }
                backend app {
                    balance: roundrobin
                    servers {
                        server s1 { address: "10.0.0.1" port: 8080 }
                    }
                }
            }
            ''')
            config_path = Path(f.name)

        try:
            _translate_once(
                config_file=config_path,
                output=None,
                format=None,
                validate=True,
                debug=False,
                lua_dir=None,
                verbose=True,
            )
        finally:
            config_path.unlink(missing_ok=True)

    def test_translate_with_lua_dir(self):
        """Test translation with Lua directory."""
        from haproxy_translator.cli.main import _translate_once

        with tempfile.NamedTemporaryFile(suffix=".hap", delete=False, mode="w") as f:
            f.write('''
            config test {
                frontend web {
                    bind *:80
                    mode: http
                    default_backend: app
                }
                backend app {
                    balance: roundrobin
                    servers {
                        server s1 { address: "10.0.0.1" port: 8080 }
                    }
                }
            }
            ''')
            config_path = Path(f.name)

        with tempfile.TemporaryDirectory() as lua_dir:
            try:
                _translate_once(
                    config_file=config_path,
                    output=None,
                    format=None,
                    validate=True,
                    debug=False,
                    lua_dir=Path(lua_dir),
                    verbose=False,
                )
            finally:
                config_path.unlink(missing_ok=True)


class TestTranslatorErrors:
    """Test error handling in CLI."""

    def test_invalid_config_raises_error(self):
        """Test that invalid config raises TranslatorError."""
        from haproxy_translator.cli.main import _translate_once
        from haproxy_translator.utils.errors import ParseError

        with tempfile.NamedTemporaryFile(suffix=".hap", delete=False, mode="w") as f:
            f.write('''
            config test {
                frontend web {
                    this is invalid syntax
                }
            }
            ''')
            config_path = Path(f.name)

        try:
            with pytest.raises(ParseError):
                _translate_once(
                    config_file=config_path,
                    output=None,
                    format=None,
                    validate=True,
                    debug=False,
                    lua_dir=None,
                    verbose=False,
                )
        finally:
            config_path.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
