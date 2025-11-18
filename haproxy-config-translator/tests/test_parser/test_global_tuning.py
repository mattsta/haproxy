"""Test global tuning directives."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestGlobalTuning:
    """Test global performance tuning directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_nbthread(self, parser, codegen):
        """Test nbthread for multi-threading."""
        source = """
        config test {
            global {
                daemon: true
                nbthread: 4
            }
        }
        """
        ir = parser.parse(source)

        assert "nbthread" in ir.global_config.tuning
        assert ir.global_config.tuning["nbthread"] == 4

        output = codegen.generate(ir)
        assert "nbthread 4" in output

    def test_maxsslconn(self, parser, codegen):
        """Test maxsslconn for SSL connection limits."""
        source = """
        config test {
            global {
                daemon: true
                maxsslconn: 10000
            }
        }
        """
        ir = parser.parse(source)

        assert "maxsslconn" in ir.global_config.tuning
        assert ir.global_config.tuning["maxsslconn"] == 10000

        output = codegen.generate(ir)
        assert "maxsslconn 10000" in output

    def test_ulimit_n(self, parser, codegen):
        """Test ulimit-n for file descriptor limits."""
        source = """
        config test {
            global {
                daemon: true
                ulimit-n: 65536
            }
        }
        """
        ir = parser.parse(source)

        assert "ulimit_n" in ir.global_config.tuning
        assert ir.global_config.tuning["ulimit_n"] == 65536

        output = codegen.generate(ir)
        assert "ulimit-n 65536" in output

    def test_all_tuning_options(self, parser, codegen):
        """Test all tuning options together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 50000
                nbthread: 8
                maxsslconn: 20000
                ulimit-n: 100000
            }
        }
        """
        ir = parser.parse(source)

        # Verify all tuning options
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.tuning["nbthread"] == 8
        assert ir.global_config.tuning["maxsslconn"] == 20000
        assert ir.global_config.tuning["ulimit_n"] == 100000

        output = codegen.generate(ir)
        assert "maxconn 50000" in output
        assert "nbthread 8" in output
        assert "maxsslconn 20000" in output
        assert "ulimit-n 100000" in output

    def test_production_config_with_tuning(self, parser, codegen):
        """Test production configuration with performance tuning."""
        source = """
        config production {
            global {
                daemon: true
                maxconn: 50000
                nbthread: 16
                maxsslconn: 25000
                ulimit-n: 200000
                user: "haproxy"
                group: "haproxy"
            }

            frontend web {
                bind *:443 ssl {
                    cert: "/etc/ssl/cert.pem"
                }
                default_backend: api
            }

            backend api {
                balance: leastconn
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Verify global tuning
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.tuning["nbthread"] == 16
        assert ir.global_config.tuning["maxsslconn"] == 25000
        assert ir.global_config.tuning["ulimit_n"] == 200000

        # Verify code generation
        output = codegen.generate(ir)

        # Check global section has all tuning directives
        global_lines = []
        in_global = False
        for line in output.split("\n"):
            if line.startswith("global"):
                in_global = True
            elif line and not line.startswith(" ") and in_global:
                break
            elif in_global and line.strip():
                global_lines.append(line.strip())

        assert "maxconn 50000" in global_lines
        assert "nbthread 16" in global_lines
        assert "maxsslconn 25000" in global_lines
        assert "ulimit-n 200000" in global_lines
