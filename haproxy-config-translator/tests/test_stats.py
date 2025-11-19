"""Tests for stats directives (Phase 4D)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestStatsBasic:
    """Test basic stats configuration."""

    def test_stats_enable(self):
        """Test stats enable directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/stats"
                }

                default_backend: app
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

        assert ir.frontends[0].stats_config is not None
        assert ir.frontends[0].stats_config.enable is True
        assert ir.frontends[0].stats_config.uri == "/stats"
        assert "stats enable" in output
        assert "stats uri /stats" in output

    def test_stats_with_realm(self):
        """Test stats with authentication realm."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/admin/stats"
                    realm: "HAProxy Statistics"
                }

                default_backend: app
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

        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert stats.realm == "HAProxy Statistics"
        assert "stats realm HAProxy Statistics" in output

    def test_stats_with_auth(self):
        """Test stats with authentication."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/stats"
                    auth: "admin:secret123"
                }

                default_backend: app
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

        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert len(stats.auth) == 1
        assert stats.auth[0] == "admin:secret123"
        assert "stats auth admin:secret123" in output

    def test_stats_with_multiple_auth(self):
        """Test stats with multiple authentication credentials."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/stats"
                    auth: "admin:secret123"
                    auth: "viewer:readonly"
                }

                default_backend: app
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

        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert len(stats.auth) == 2
        assert "admin:secret123" in stats.auth
        assert "viewer:readonly" in stats.auth
        assert "stats auth admin:secret123" in output
        assert "stats auth viewer:readonly" in output


class TestStatsAdvanced:
    """Test advanced stats configuration."""

    def test_stats_hide_version(self):
        """Test stats hide-version directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/stats"
                    hide-version: true
                }

                default_backend: app
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

        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert stats.hide_version is True
        assert "stats hide-version" in output

    def test_stats_refresh(self):
        """Test stats refresh directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/stats"
                    refresh: 30
                }

                default_backend: app
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

        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert stats.refresh == "30"
        assert "stats refresh 30" in output

    def test_stats_show_legends(self):
        """Test stats show-legends directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/stats"
                    show-legends: true
                }

                default_backend: app
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

        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert stats.show_legends is True
        assert "stats show-legends" in output

    def test_stats_show_desc(self):
        """Test stats show-desc directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/stats"
                    show-desc: "Production Load Balancer"
                }

                default_backend: app
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

        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert stats.show_desc == "Production Load Balancer"
        assert "stats show-desc Production Load Balancer" in output


class TestStatsComplete:
    """Test complete stats configuration."""

    def test_stats_complete_configuration(self):
        """Test complete stats setup with all options."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                stats {
                    enable: true
                    uri: "/haproxy?stats"
                    realm: "HAProxy Admin"
                    auth: "admin:SuperSecret123"
                    auth: "viewer:ReadOnly456"
                    hide-version: true
                    refresh: 30
                    show-legends: true
                    show-desc: "Production Web Frontend"
                }

                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server app2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify IR
        stats = ir.frontends[0].stats_config
        assert stats is not None
        assert stats.enable is True
        assert stats.uri == "/haproxy?stats"
        assert stats.realm == "HAProxy Admin"
        assert len(stats.auth) == 2
        assert "admin:SuperSecret123" in stats.auth
        assert "viewer:ReadOnly456" in stats.auth
        assert stats.hide_version is True
        assert stats.refresh == "30"
        assert stats.show_legends is True
        assert stats.show_desc == "Production Web Frontend"

        # Verify output
        assert "stats enable" in output
        assert "stats uri /haproxy?stats" in output
        assert "stats realm HAProxy Admin" in output
        assert "stats auth admin:SuperSecret123" in output
        assert "stats auth viewer:ReadOnly456" in output
        assert "stats hide-version" in output
        assert "stats refresh 30" in output
        assert "stats show-legends" in output
        assert "stats show-desc Production Web Frontend" in output

    def test_stats_with_monitoring(self):
        """Test stats combined with monitoring features."""
        config = """
        config production {
            frontend api {
                bind *:443
                mode: http

                monitor_uri: "/healthz"
                monitor-net "10.0.0.0/8"

                stats {
                    enable: true
                    uri: "/admin/stats"
                    realm: "API Gateway Stats"
                    auth: "admin:password123"
                    hide-version: true
                }

                default_backend: api_backend
            }

            backend api_backend {
                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        # Verify monitoring
        frontend = ir.frontends[0]
        assert frontend.monitor_uri == "/healthz"
        assert len(frontend.monitor_net) == 1

        # Verify stats
        assert frontend.stats_config is not None
        assert frontend.stats_config.enable is True
        assert frontend.stats_config.uri == "/admin/stats"

        # Verify output
        assert "monitor-uri /healthz" in output
        assert "monitor-net 10.0.0.0/8" in output
        assert "stats enable" in output
        assert "stats uri /admin/stats" in output
        assert "stats hide-version" in output

    def test_stats_with_logging(self):
        """Test stats combined with logging features."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                log: "127.0.0.1:514 local0 info"
                log-tag: "web-frontend"

                stats {
                    enable: true
                    uri: "/stats"
                    auth: "admin:secret"
                    refresh: 10
                }

                default_backend: app
            }

            backend app {
                servers {
                    server app1 {
                        address: "10.0.1.1"
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

        # Verify logging
        frontend = ir.frontends[0]
        assert len(frontend.log) == 1
        assert frontend.log_tag == "web-frontend"

        # Verify stats
        assert frontend.stats_config is not None
        assert frontend.stats_config.enable is True

        # Verify output
        assert "log 127.0.0.1:514 local0 info" in output
        assert "log-tag web-frontend" in output
        assert "stats enable" in output
        assert "stats uri /stats" in output
        assert "stats refresh 10" in output
