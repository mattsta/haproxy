"""Comprehensive tests to achieve 100% code coverage."""

import pytest
from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestCoverage100Percent:
    """Tests specifically designed to hit all uncovered code paths."""

    # ========== Template Expander Coverage ==========

    def test_template_spread_single_not_list(self):
        """Test template_spreads as single value (line 40)."""
        config = """
        config test {
            template web_server {
                check: true
                maxconn: 100
            }

            backend app {
                servers {
                    server srv1 {
                        address: "192.168.1.10"
                        port: 9000
                        @web_server
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "server srv1 192.168.1.10:9000" in output
        assert "check" in output
        assert "maxconn 100" in output

    def test_server_port_not_default_8080(self):
        """Test server with port != 8080 (line 70)."""
        config = """
        config test {
            template web_server {
                check: true
            }

            backend app {
                servers {
                    server srv1 {
                        address: "192.168.1.10"
                        port: 9000
                        @web_server
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "9000" in output

    # ========== Transformer Coverage - Global Directives ==========

    def test_global_chroot_directive(self):
        """Test chroot global directive (line 250)."""
        config = """
        config test {
            global {
                chroot: "/var/lib/haproxy"
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "chroot /var/lib/haproxy" in output

    def test_global_pidfile_directive(self):
        """Test pidfile global directive (line 252)."""
        config = """
        config test {
            global {
                pidfile: "/var/run/haproxy.pid"
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "pidfile /var/run/haproxy.pid" in output

    # ========== Transformer Coverage - More Global Directives ==========

    def test_global_directive_combinations(self):
        """Test multiple uncovered global directives."""
        config = """
        config test {
            global {
                chroot: "/var/lib/haproxy"
                pidfile: "/var/run/haproxy.pid"
                user: "haproxy"
                group: "haproxy"
                daemon: true
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "chroot /var/lib/haproxy" in output
        assert "pidfile /var/run/haproxy.pid" in output
        assert "user haproxy" in output
        assert "group haproxy" in output
        assert "daemon" in output

    # ========== Phase 1: High-Impact Tests ==========

    def test_global_stats_configuration(self):
        """Test global stats with enable, uri, auth (lines 477-478, 615, 1082-1096, 1099, 1102, 1105)."""
        config = """
        config test {
            global {
                stats {
                    enable: true
                    uri: "/haproxy-stats"
                    auth: "admin:password"
                }
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config
        assert ir.global_config.stats is not None
        assert ir.global_config.stats.enable is True
        assert ir.global_config.stats.uri == "/haproxy-stats"
        assert ir.global_config.stats.auth == "admin:password"

    def test_frontend_tcp_request_response_rules(self):
        """Test TCP request/response rules in frontend (lines 1300, 1304, 1039, 1056)."""
        config = """
        config test {
            frontend tcp_front {
                bind *:3306
                mode: tcp

                tcp-request {
                    content accept
                }

                tcp-response {
                    content accept
                }

                default_backend: db_servers
            }

            backend db_servers {
                mode: tcp
                servers {
                    server db1 {
                        address: "10.0.1.10"
                        port: 3306
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "tcp-request content accept" in output
        assert "tcp-response content accept" in output

    def test_frontend_http_response_rules(self):
        """Test HTTP response rules in frontend (lines 1292, 1296)."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                http-response {
                    set_header name: "X-Frame-Options" value: "DENY"
                }

                default_backend: web_servers
            }

            backend web_servers {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.frontends
        assert ir.frontends[0].http_response_rules

    def test_defaults_with_log_and_single_option(self):
        """Test defaults with log and single option (lines 1162, 1167, 1227)."""
        config = """
        config test {
            defaults {
                mode: http
                log: "global"
                option: "httplog"
                timeout: {
                    connect: 5s
                    client: 50s
                    server: 50s
                }
            }

            backend app {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults
        assert ir.defaults.log == "global"
        assert "httplog" in ir.defaults.options

    def test_frontend_use_backend_rules(self):
        """Test use_backend rules in frontend (lines 1312, 1314)."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                acl is_api {
                    path_beg "/api"
                }

                use_backend api_servers if is_api

                default_backend: web_servers
            }

            backend api_servers {
                servers {
                    server api1 {
                        address: "10.0.1.20"
                        port: 8080
                    }
                }
            }

            backend web_servers {
                servers {
                    server web1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.frontends
        assert ir.frontends[0].use_backend_rules
