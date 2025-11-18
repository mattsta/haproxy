"""Tests for Phase 4B Part 2 global directives - SSL Advanced & Profiling."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase4BPart2GlobalDirectives:
    """Test cases for Phase 4B Part 2 global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_ssl_advanced_directives(self, parser, codegen):
        """Test SSL advanced configuration directives."""
        source = """
        config test {
            global {
                daemon: true
                ssl-load-extra-files: "bundle"
                ssl-load-extra-del-ext: "rsa"
                ssl-mode-async: true
                ssl-propquery: "provider=default"
                ssl-provider: "default"
                ssl-provider-path: "/usr/lib/ossl-modules"
                issuers-chain-path: "/etc/ssl/issuers"
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.ssl_load_extra_files == "bundle"
        assert ir.global_config.ssl_load_extra_del_ext == "rsa"
        assert ir.global_config.ssl_mode_async is True
        assert ir.global_config.ssl_propquery == "provider=default"
        assert ir.global_config.ssl_provider == "default"
        assert ir.global_config.ssl_provider_path == "/usr/lib/ossl-modules"
        assert ir.global_config.issuers_chain_path == "/etc/ssl/issuers"

        assert "ssl-load-extra-files bundle" in output
        assert "ssl-load-extra-del-ext rsa" in output
        assert "ssl-mode-async" in output
        assert "ssl-propquery provider=default" in output
        assert "ssl-provider default" in output
        assert "ssl-provider-path /usr/lib/ossl-modules" in output
        assert "issuers-chain-path /etc/ssl/issuers" in output

    def test_global_ssl_mode_async_false(self, parser, codegen):
        """Test SSL async mode disabled."""
        source = """
        config test {
            global {
                daemon: true
                ssl-mode-async: false
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.ssl_mode_async is False
        # false values don't appear in output
        assert "ssl-mode-async" not in output

    def test_global_profiling_tasks(self, parser, codegen):
        """Test profiling tasks directives."""
        source = """
        config test {
            global {
                daemon: true
                profiling.tasks.on: true
                profiling.tasks.automatic: true
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.profiling_tasks_on is True
        assert ir.global_config.profiling_tasks_automatic is True

        assert "profiling.tasks.on" in output
        assert "profiling.tasks.automatic" in output

    def test_global_profiling_memory(self, parser, codegen):
        """Test profiling memory directive."""
        source = """
        config test {
            global {
                daemon: true
                profiling.memory.on: true
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.profiling_memory_on is True
        assert "profiling.memory.on" in output

    def test_global_profiling_disabled(self, parser, codegen):
        """Test profiling with disabled options."""
        source = """
        config test {
            global {
                daemon: true
                profiling.tasks.on: false
                profiling.tasks.automatic: false
                profiling.memory.on: false
            }

            frontend web {
                bind *:80
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.profiling_tasks_on is False
        assert ir.global_config.profiling_tasks_automatic is False
        assert ir.global_config.profiling_memory_on is False

        # false values don't appear in output
        assert "profiling.tasks.on" not in output
        assert "profiling.tasks.automatic" not in output
        assert "profiling.memory.on" not in output

    def test_global_ssl_provider_configuration(self, parser, codegen):
        """Test SSL provider configuration for custom crypto engines."""
        source = """
        config test {
            global {
                daemon: true
                ssl-provider: "fips"
                ssl-provider-path: "/usr/lib64/ossl-modules"
                ssl-propquery: "fips=yes"
            }

            frontend web {
                bind *:443
                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        assert ir.global_config.ssl_provider == "fips"
        assert ir.global_config.ssl_provider_path == "/usr/lib64/ossl-modules"
        assert ir.global_config.ssl_propquery == "fips=yes"

        assert "ssl-provider fips" in output
        assert "ssl-provider-path /usr/lib64/ossl-modules" in output
        assert "ssl-propquery fips=yes" in output

    def test_global_phase4b_part2_comprehensive(self, parser, codegen):
        """Test all Phase 4B Part 2 directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 100000

                // SSL Advanced Configuration
                ssl-load-extra-files: "bundle"
                ssl-load-extra-del-ext: "ecdsa"
                ssl-mode-async: true
                ssl-propquery: "provider=default"
                ssl-provider: "default"
                ssl-provider-path: "/usr/lib/ossl-modules"
                issuers-chain-path: "/etc/ssl/issuers"

                // Profiling & Debugging
                profiling.tasks.on: true
                profiling.tasks.automatic: false
                profiling.memory.on: true
            }

            frontend https {
                bind *:443
                default_backend: web
            }

            backend web {
                servers {
                    server web1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify all SSL Advanced directives in IR
        assert ir.global_config.ssl_load_extra_files == "bundle"
        assert ir.global_config.ssl_load_extra_del_ext == "ecdsa"
        assert ir.global_config.ssl_mode_async is True
        assert ir.global_config.ssl_propquery == "provider=default"
        assert ir.global_config.ssl_provider == "default"
        assert ir.global_config.ssl_provider_path == "/usr/lib/ossl-modules"
        assert ir.global_config.issuers_chain_path == "/etc/ssl/issuers"

        # Verify all Profiling directives in IR
        assert ir.global_config.profiling_tasks_on is True
        assert ir.global_config.profiling_tasks_automatic is False
        assert ir.global_config.profiling_memory_on is True

        # Verify SSL Advanced directives in output
        assert "ssl-load-extra-files bundle" in output
        assert "ssl-load-extra-del-ext ecdsa" in output
        assert "ssl-mode-async" in output
        assert "ssl-propquery provider=default" in output
        assert "ssl-provider default" in output
        assert "ssl-provider-path /usr/lib/ossl-modules" in output
        assert "issuers-chain-path /etc/ssl/issuers" in output

        # Verify Profiling directives in output
        assert "profiling.tasks.on" in output
        # false values don't appear
        assert "profiling.tasks.automatic" not in output
        assert "profiling.memory.on" in output
