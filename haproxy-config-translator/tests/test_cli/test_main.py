"""Tests for CLI."""

import pytest
from click.testing import CliRunner

from haproxy_translator.cli.main import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_config(tmp_path):
    """Create a simple test configuration file."""
    config_content = """
config test {
    frontend web {
        bind *:80
        default_backend: servers
    }

    backend servers {
        balance: roundrobin
        servers {
            server web1 {
                address: "10.0.1.1"
                port: 8080
                check: true
            }
        }
    }
}
"""
    config_file = tmp_path / "test.hap"
    config_file.write_text(config_content)
    return config_file


class TestCLI:
    """Test CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "HAProxy Configuration Translator" in result.output
        assert "Examples:" in result.output

    def test_cli_version(self, runner):
        """Test version flag."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "haproxy-translate" in result.output

    def test_list_formats(self, runner, sample_config):
        """Test listing available formats."""
        # Note: --list-formats requires config_file arg but ignores it
        result = runner.invoke(cli, [str(sample_config), "--list-formats"])
        assert result.exit_code == 0
        assert "Available Input Formats:" in result.output
        assert "dsl" in result.output.lower()

    def test_translate_to_stdout(self, runner, sample_config):
        """Test translating to stdout."""
        result = runner.invoke(cli, [str(sample_config)])
        assert result.exit_code == 0
        assert "frontend web" in result.output
        assert "backend servers" in result.output
        assert "bind *:80" in result.output

    def test_translate_to_file(self, runner, sample_config, tmp_path):
        """Test translating to output file."""
        output_file = tmp_path / "haproxy.cfg"
        result = runner.invoke(cli, [str(sample_config), "-o", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "frontend web" in content
        assert "backend servers" in content
        assert "bind *:80" in content

    def test_validate_only(self, runner, sample_config):
        """Test validate-only mode."""
        result = runner.invoke(cli, [str(sample_config), "--validate"])
        assert result.exit_code == 0
        assert "Configuration is valid" in result.output
        assert "frontend web" not in result.output  # No generation

    def test_verbose_mode(self, runner, sample_config, tmp_path):
        """Test verbose output."""
        output_file = tmp_path / "haproxy.cfg"
        result = runner.invoke(cli, [str(sample_config), "-o", str(output_file), "--verbose"])
        assert result.exit_code == 0
        assert "Reading config from:" in result.output
        assert "Using parser:" in result.output
        assert "Parsed successfully:" in result.output

    def test_debug_mode(self, runner, sample_config, tmp_path):
        """Test debug output."""
        output_file = tmp_path / "haproxy.cfg"
        result = runner.invoke(cli, [str(sample_config), "-o", str(output_file), "--debug"])
        assert result.exit_code == 0
        assert "IR Debug Info:" in result.output
        assert "Frontends:" in result.output
        assert "Backends:" in result.output

    def test_format_auto_detection(self, runner, sample_config):
        """Test format auto-detection from file extension."""
        result = runner.invoke(cli, [str(sample_config)])
        assert result.exit_code == 0
        # Should auto-detect .hap as DSL format

    def test_explicit_format(self, runner, sample_config):
        """Test explicit format specification."""
        result = runner.invoke(cli, [str(sample_config), "--format", "dsl"])
        assert result.exit_code == 0

    def test_invalid_format(self, runner, sample_config):
        """Test error on invalid format."""
        result = runner.invoke(cli, [str(sample_config), "--format", "invalid_format"])
        assert result.exit_code == 1
        assert "Error:" in result.output

    @pytest.mark.xfail(reason="Lua extraction not yet fully integrated in parser")
    def test_lua_extraction(self, runner, tmp_path):
        """Test Lua script extraction."""
        config_content = """
config test {
    lua {
        inline test_script {
            core.register_service("test", "http", function(applet)
                applet:set_status(200)
                applet:start_response()
                applet:send("OK")
            end)
        }
    }

    frontend web {
        bind *:80
        default_backend: servers
    }

    backend servers {
        balance: roundrobin
    }
}
"""
        config_file = tmp_path / "test.hap"
        config_file.write_text(config_content)

        output_file = tmp_path / "haproxy.cfg"
        result = runner.invoke(cli, [str(config_file), "-o", str(output_file), "--verbose"])

        assert result.exit_code == 0
        # Check that Lua directory was created
        lua_dir = tmp_path / "lua"
        if lua_dir.exists():
            assert "Lua scripts written to:" in result.output

    @pytest.mark.xfail(reason="Lua extraction not yet fully integrated in parser")
    def test_custom_lua_dir(self, runner, tmp_path):
        """Test custom Lua output directory."""
        config_content = """
config test {
    lua {
        inline test_script {
            core.Info("test")
        }
    }

    frontend web {
        bind *:80
        default_backend: servers
    }

    backend servers {
        balance: roundrobin
    }
}
"""
        config_file = tmp_path / "test.hap"
        config_file.write_text(config_content)

        output_file = tmp_path / "output" / "haproxy.cfg"
        lua_dir = tmp_path / "scripts"
        output_file.parent.mkdir(parents=True)

        result = runner.invoke(
            cli, [str(config_file), "-o", str(output_file), "--lua-dir", str(lua_dir)]
        )

        assert result.exit_code == 0

    def test_nonexistent_file(self, runner):
        """Test error on nonexistent input file."""
        result = runner.invoke(cli, ["nonexistent.hap"])
        assert result.exit_code == 2  # Click's file not found error
        assert "does not exist" in result.output.lower() or "error" in result.output.lower()

    def test_parse_error(self, runner, tmp_path):
        """Test error on invalid config."""
        invalid_config = tmp_path / "invalid.hap"
        invalid_config.write_text("this is not valid syntax {{{")

        result = runner.invoke(cli, [str(invalid_config)])
        assert result.exit_code == 1
        assert "Error:" in result.output

    def test_parse_error_with_debug(self, runner, tmp_path):
        """Test parse error with debug shows exception."""
        invalid_config = tmp_path / "invalid.hap"
        invalid_config.write_text("invalid { syntax")

        result = runner.invoke(cli, [str(invalid_config), "--debug"])
        assert result.exit_code == 1
        assert "Error:" in result.output

    @pytest.mark.xfail(reason="Full transformation pipeline integration pending")
    def test_variable_interpolation(self, runner, tmp_path):
        """Test configuration with variables."""
        config_content = """
config test {
    let port = 8080

    frontend web {
        bind *:80
        default_backend: servers
    }

    backend servers {
        balance: roundrobin
        servers {
            server web1 {
                address: "10.0.1.1"
                port: ${port}
            }
        }
    }
}
"""
        config_file = tmp_path / "test.hap"
        config_file.write_text(config_content)

        output_file = tmp_path / "haproxy.cfg"
        result = runner.invoke(cli, [str(config_file), "-o", str(output_file), "--debug"])

        assert result.exit_code == 0
        assert "Variables:" in result.output

        content = output_file.read_text()
        assert "10.0.1.1:8080" in content

    @pytest.mark.xfail(reason="Full transformation pipeline integration pending")
    def test_template_expansion(self, runner, tmp_path):
        """Test configuration with templates."""
        config_content = """
config test {
    template defaults {
        check: true
        rise: 3
        fall: 2
    }

    frontend web {
        bind *:80
        default_backend: servers
    }

    backend servers {
        balance: roundrobin
        servers {
            server web1 {
                address: "10.0.1.1"
                port: 8080
                @defaults
            }
        }
    }
}
"""
        config_file = tmp_path / "test.hap"
        config_file.write_text(config_content)

        output_file = tmp_path / "haproxy.cfg"
        result = runner.invoke(cli, [str(config_file), "-o", str(output_file), "--debug"])

        assert result.exit_code == 0
        assert "Templates:" in result.output

        content = output_file.read_text()
        assert "check" in content
        assert "rise 3" in content

    @pytest.mark.xfail(reason="Directory creation needs explicit mkdir in HAProxyCodeGenerator")
    def test_output_directory_creation(self, runner, sample_config, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_file = tmp_path / "nested" / "dir" / "haproxy.cfg"
        result = runner.invoke(cli, [str(sample_config), "-o", str(output_file)])

        # Should create directories and file
        assert result.exit_code == 0
        assert output_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
