"""Tests for Phase 1 critical global directives."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase1GlobalDirectives:
    """Test cases for Phase 1 critical global directives."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    def test_global_rate_limiting(self, parser, codegen):
        """Test rate limiting directives: maxconnrate, maxsslrate, maxsessrate."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 4000
                maxconnrate: 500
                maxsslrate: 100
                maxsessrate: 1000
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.maxconnrate == 500
        assert ir.global_config.maxsslrate == 100
        assert ir.global_config.maxsessrate == 1000

        # Verify code generation
        assert "maxconnrate 500" in output
        assert "maxsslrate 100" in output
        assert "maxsessrate 1000" in output

    def test_global_process_control(self, parser, codegen):
        """Test process control directive: nbproc."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 4000
                nbproc: 4
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.nbproc == 4

        # Verify code generation
        assert "nbproc 4" in output

    def test_global_ssl_base_paths(self, parser, codegen):
        """Test SSL base path directives: ca-base, crt-base."""
        source = """
        config test {
            global {
                daemon: true
                ca-base: "/etc/ssl/certs"
                crt-base: "/etc/ssl/private"
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.ca_base == "/etc/ssl/certs"
        assert ir.global_config.crt_base == "/etc/ssl/private"

        # Verify code generation
        assert "ca-base /etc/ssl/certs" in output
        assert "crt-base /etc/ssl/private" in output

    def test_global_logging_config(self, parser, codegen):
        """Test logging configuration directives: log-tag, log-send-hostname."""
        source = """
        config test {
            global {
                daemon: true
                log-tag: "myapp"
                log-send-hostname: "webserver01"
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.log_tag == "myapp"
        assert ir.global_config.log_send_hostname == "webserver01"

        # Verify code generation
        assert "log-tag myapp" in output
        assert "log-send-hostname webserver01" in output

    def test_global_ssl_server_config(self, parser, codegen):
        """Test SSL server directives: ssl-dh-param-file, ssl-default-server-ciphers, ssl-server-verify."""
        source = """
        config test {
            global {
                daemon: true
                ssl-dh-param-file: "/etc/ssl/dhparam.pem"
                ssl-default-server-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
                ssl-server-verify: "required"
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
                        ssl: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.ssl_dh_param_file == "/etc/ssl/dhparam.pem"
        assert (
            ir.global_config.ssl_default_server_ciphers
            == "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
        )
        assert ir.global_config.ssl_server_verify == "required"

        # Verify code generation
        assert "ssl-dh-param-file /etc/ssl/dhparam.pem" in output
        assert (
            "ssl-default-server-ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
            in output
        )
        assert "ssl-server-verify required" in output

    def test_global_environment_variables(self, parser, codegen):
        """Test environment variable directives: setenv, presetenv."""
        source = """
        config test {
            global {
                daemon: true
                setenv "API_KEY" "secret123"
                setenv "ENVIRONMENT" "production"
                presetenv "HOME_DIR" "/var/lib/haproxy"
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

        # Verify IR
        assert ir.global_config is not None
        assert ir.global_config.env_vars["API_KEY"] == "secret123"
        assert ir.global_config.env_vars["ENVIRONMENT"] == "production"
        assert ir.global_config.env_vars["HOME_DIR"] == "/var/lib/haproxy"

        # Verify code generation
        assert "setenv API_KEY secret123" in output
        assert "setenv ENVIRONMENT production" in output
        assert "setenv HOME_DIR /var/lib/haproxy" in output

    def test_global_reset_unset_env(self, parser, codegen):
        """Test environment variable directives: resetenv, unsetenv."""
        source = """
        config test {
            global {
                daemon: true
                resetenv "PATH"
                unsetenv "TEMP_VAR"
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

        # Verify IR
        assert ir.global_config is not None
        assert "PATH" in ir.global_config.reset_env_vars
        assert "TEMP_VAR" in ir.global_config.unset_env_vars

        # Verify code generation
        assert "resetenv PATH" in output
        assert "unsetenv TEMP_VAR" in output

    def test_global_phase1_comprehensive(self, parser, codegen):
        """Test all Phase 1 global directives together."""
        source = """
        config test {
            global {
                daemon: true
                maxconn: 10000
                nbproc: 8
                maxconnrate: 1000
                maxsslrate: 200
                maxsessrate: 2000
                ca-base: "/etc/ssl/certs"
                crt-base: "/etc/ssl/private"
                log-tag: "haproxy"
                log-send-hostname: "lb01"
                ssl-dh-param-file: "/etc/ssl/dhparam.pem"
                ssl-default-server-ciphers: "ECDHE-RSA-AES128-GCM-SHA256"
                ssl-server-verify: "required"
                setenv "APP_ENV" "prod"
                resetenv "PATH"
                unsetenv "DEBUG"
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
                        ssl: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        output = codegen.generate(ir)

        # Verify all directives are in output
        assert "maxconn 10000" in output
        assert "nbproc 8" in output
        assert "maxconnrate 1000" in output
        assert "maxsslrate 200" in output
        assert "maxsessrate 2000" in output
        assert "ca-base /etc/ssl/certs" in output
        assert "crt-base /etc/ssl/private" in output
        assert "log-tag haproxy" in output
        assert "log-send-hostname lb01" in output
        assert "ssl-dh-param-file /etc/ssl/dhparam.pem" in output
        assert "ssl-default-server-ciphers ECDHE-RSA-AES128-GCM-SHA256" in output
        assert "ssl-server-verify required" in output
        assert "setenv APP_ENV prod" in output
        assert "resetenv PATH" in output
        assert "unsetenv DEBUG" in output
