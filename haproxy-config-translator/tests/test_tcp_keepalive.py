"""Tests for TCP keepalive directives (clitcpka-*, srvtcpka-*)."""

from haproxy_translator.parsers import DSLParser


class TestDefaultsTcpKeepalive:
    """Test TCP keepalive in defaults section."""

    def test_defaults_clitcpka(self):
        """Test client TCP keepalive in defaults."""
        config = """
        config test {
            defaults {
                clitcpka-cnt: 5
                clitcpka-idle: 10s
                clitcpka-intvl: 3s
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.clitcpka_cnt == 5
        assert ir.defaults.clitcpka_idle == "10s"
        assert ir.defaults.clitcpka_intvl == "3s"

    def test_defaults_srvtcpka(self):
        """Test server TCP keepalive in defaults."""
        config = """
        config test {
            defaults {
                srvtcpka-cnt: 7
                srvtcpka-idle: 20s
                srvtcpka-intvl: 5s
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.srvtcpka_cnt == 7
        assert ir.defaults.srvtcpka_idle == "20s"
        assert ir.defaults.srvtcpka_intvl == "5s"

    def test_defaults_both_tcp_keepalive(self):
        """Test both client and server TCP keepalive in defaults."""
        config = """
        config test {
            defaults {
                clitcpka-cnt: 5
                clitcpka-idle: 10s
                clitcpka-intvl: 3s
                srvtcpka-cnt: 7
                srvtcpka-idle: 20s
                srvtcpka-intvl: 5s
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.clitcpka_cnt == 5
        assert ir.defaults.srvtcpka_cnt == 7


class TestFrontendClitcpka:
    """Test client TCP keepalive in frontend section."""

    def test_frontend_clitcpka(self):
        """Test client TCP keepalive in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                clitcpka-cnt: 5
                clitcpka-idle: 10s
                clitcpka-intvl: 3s
                default_backend: app
            }

            backend app {
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert ir.frontends[0].clitcpka_cnt == 5
        assert ir.frontends[0].clitcpka_idle == "10s"
        assert ir.frontends[0].clitcpka_intvl == "3s"


class TestBackendSrvtcpka:
    """Test server TCP keepalive in backend section."""

    def test_backend_srvtcpka(self):
        """Test server TCP keepalive in backend."""
        config = """
        config test {
            backend app {
                srvtcpka-cnt: 7
                srvtcpka-idle: 20s
                srvtcpka-intvl: 5s
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].srvtcpka_cnt == 7
        assert ir.backends[0].srvtcpka_idle == "20s"
        assert ir.backends[0].srvtcpka_intvl == "5s"


class TestIntegration:
    """Integration tests for TCP keepalive directives."""

    def test_full_config_with_tcp_keepalive(self):
        """Test complete configuration with TCP keepalive in all sections."""
        config = """
        config test {
            defaults {
                mode: http
                clitcpka-cnt: 3
                clitcpka-idle: 5s
                srvtcpka-cnt: 4
                srvtcpka-idle: 10s
            }

            frontend web {
                bind *:80
                clitcpka-cnt: 5
                clitcpka-idle: 10s
                clitcpka-intvl: 3s
                default_backend: app
            }

            backend app {
                srvtcpka-cnt: 7
                srvtcpka-idle: 20s
                srvtcpka-intvl: 5s
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify defaults
        assert ir.defaults.clitcpka_cnt == 3
        assert ir.defaults.srvtcpka_cnt == 4

        # Verify frontend
        assert ir.frontends[0].clitcpka_cnt == 5
        assert ir.frontends[0].clitcpka_idle == "10s"

        # Verify backend
        assert ir.backends[0].srvtcpka_cnt == 7
        assert ir.backends[0].srvtcpka_idle == "20s"
