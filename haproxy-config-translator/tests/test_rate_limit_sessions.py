"""Tests for rate-limit sessions directive (Phase 5B)."""

from haproxy_translator.parsers import DSLParser


class TestDefaultsRateLimitSessions:
    """Test rate-limit sessions in defaults section."""

    def test_defaults_rate_limit_sessions(self):
        """Test rate-limit sessions in defaults."""
        config = """
        config test {
            defaults {
                rate-limit sessions: 100
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.defaults.rate_limit_sessions == 100


class TestFrontendRateLimitSessions:
    """Test rate-limit sessions in frontend section."""

    def test_frontend_rate_limit_sessions(self):
        """Test rate-limit sessions in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                rate-limit sessions: 50
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
        assert ir.frontends[0].rate_limit_sessions == 50


class TestIntegration:
    """Integration tests for rate-limit sessions."""

    def test_rate_limit_in_defaults_and_frontend(self):
        """Test rate-limit sessions in both defaults and frontend."""
        config = """
        config test {
            defaults {
                mode: http
                rate-limit sessions: 1000
            }

            frontend web {
                bind *:80
                rate-limit sessions: 100
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

        # Defaults should have rate limit
        assert ir.defaults.rate_limit_sessions == 1000

        # Frontend should override with its own
        assert ir.frontends[0].rate_limit_sessions == 100
