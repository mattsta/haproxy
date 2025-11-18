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

    # ========== Phase 2: Additional Coverage Tests ==========

    def test_frontend_single_option(self):
        """Test frontend with single option (line 1334)."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: "httplog"
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
        assert "httplog" in ir.frontends[0].options

    def test_frontend_maxconn(self):
        """Test frontend with maxconn (lines 1348, 1410)."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                maxconn: 2000
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
        assert ir.frontends[0].maxconn == 2000

    def test_backend_cookie_directive(self):
        """Test backend cookie directive (lines 1703, 2321)."""
        config = """
        config test {
            backend web_servers {
                cookie: "SERVERID insert indirect nocache"
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                        cookie: "srv1"
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends
        assert ir.backends[0].cookie == "SERVERID insert indirect nocache"

    def test_backend_retries_directive(self):
        """Test backend retries directive (lines 1712, 2630)."""
        config = """
        config test {
            backend web_servers {
                retries: 3
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
        assert ir.backends
        assert ir.backends[0].retries == 3

    def test_backend_single_option(self):
        """Test backend with single option (line 1739)."""
        config = """
        config test {
            backend web_servers {
                option: "httpchk"
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
        assert ir.backends
        assert "httpchk" in ir.backends[0].options

    def test_listen_section_with_acl(self):
        """Test listen section with ACL (lines 1923, 1931-1937)."""
        config = """
        config test {
            listen mysql {
                bind *:3306
                mode: tcp

                acl is_valid {
                    src "10.0.0.0/8"
                }

                servers {
                    server db1 {
                        address: "10.0.1.1"
                        port: 3306
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.listens
        assert ir.listens[0].acls

    def test_listen_section_basic(self):
        """Test basic listen section (lines 1967, 1977, 2003)."""
        config = """
        config test {
            listen web {
                bind *:80
                mode: http

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
        assert ir.listens
        assert "listen web" in output
        assert "bind *:80" in output

    # ========== Phase 3: More Edge Cases and Features ==========

    def test_backend_http_request_rules(self):
        """Test backend with http-request rules (lines 1712, 1721)."""
        config = """
        config test {
            backend web_servers {
                mode: http

                http-request {
                    set_header name: "X-Backend" value: "web"
                }

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
        assert ir.backends
        assert "http-request" in output

    def test_backend_balance_directive(self):
        """Test backend with balance algorithms (line 2630)."""
        config = """
        config test {
            backend web_servers {
                balance: leastconn
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
        assert "balance leastconn" in output

    def test_listen_with_single_option(self):
        """Test listen section with single option (line 1954)."""
        config = """
        config test {
            listen stats {
                bind *:8404
                mode: http
                option: "httplog"

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
        assert ir.listens
        assert ir.listens[0].options
        assert "httplog" in ir.listens[0].options

    def test_server_with_backup_option(self):
        """Test server with backup option (lines 2059-2062)."""
        config = """
        config test {
            backend web_servers {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                    }
                    server backup1 {
                        address: "192.168.1.10"
                        port: 8080
                        backup: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "backup" in output

    def test_defaults_with_multiple_timeouts(self):
        """Test defaults with multiple timeout types (lines 2113, 2121-2123)."""
        config = """
        config test {
            defaults {
                mode: http
                timeout: {
                    connect: 5s
                    client: 30s
                    server: 30s
                    check: 10s
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
        assert ir.defaults.timeout_check == "10s"

    def test_stick_table_configuration(self):
        """Test stick-table configuration (line 2189)."""
        config = """
        config test {
            backend web_servers {
                stick-table {
                    type: ip
                    size: 100000
                }

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
        assert "stick-table" in output
        assert "type ip" in output

    def test_server_with_weight_option(self):
        """Test server with weight option (line 2086)."""
        config = """
        config test {
            backend web_servers {
                servers {
                    server srv1 {
                        address: "127.0.0.1"
                        port: 8080
                        weight: 100
                    }
                    server srv2 {
                        address: "192.168.1.10"
                        port: 8080
                        weight: 50
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "weight 100" in output
        assert "weight 50" in output
