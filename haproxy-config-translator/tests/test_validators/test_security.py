"""Tests for security validator."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.validators.security import (
    SecurityIssue,
    SecurityLevel,
    SecurityReport,
    SecurityValidator,
)


class TestSecurityValidator:
    """Test security validation functionality."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_secure_config_passes(self, parser):
        """Test that a secure configuration passes validation."""
        source = """
        config test {
            global {
                maxconn: 10000
                user: "haproxy"
                group: "haproxy"
                chroot: "/var/lib/haproxy"
            }
            frontend web {
                bind 127.0.0.1:80
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        # Should pass (may have info-level warnings)
        critical_or_high = [
            i for i in report.issues if i.level in (SecurityLevel.CRITICAL, SecurityLevel.HIGH)
        ]
        assert len(critical_or_high) == 0

    def test_root_user_warning(self, parser):
        """Test that running as root generates a warning."""
        source = """
        config test {
            global {
                user: "root"
            }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        # Should have HIGH level issue for root user
        root_issues = [i for i in report.issues if "root" in i.message.lower()]
        assert len(root_issues) >= 1
        assert root_issues[0].level == SecurityLevel.HIGH

    def test_missing_chroot_warning(self, parser):
        """Test that missing chroot generates a warning."""
        source = """
        config test {
            global {
                user: "haproxy"
            }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        # Should have warning for missing chroot
        chroot_issues = [i for i in report.issues if "chroot" in i.message.lower()]
        assert len(chroot_issues) >= 1

    def test_stats_without_auth_critical(self, parser):
        """Test that stats without auth is flagged."""
        source = """
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
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        # Should have HIGH issue for stats without auth
        stats_issues = [
            i for i in report.issues if "stats" in i.message.lower() and "auth" in i.message.lower()
        ]
        assert len(stats_issues) >= 1

    def test_ssl_without_cert_high(self, parser):
        """Test that SSL without cert is flagged."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl { }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        # Should have issue for SSL without certificate
        ssl_issues = [
            i for i in report.issues if "ssl" in i.message.lower() and "cert" in i.message.lower()
        ]
        assert len(ssl_issues) >= 1

    def test_wildcard_bind_info(self, parser):
        """Test that wildcard bind generates info message."""
        source = """
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        # Should have INFO for wildcard bind
        bind_issues = [
            i
            for i in report.issues
            if "all interfaces" in i.message.lower() or "wildcard" in i.message.lower()
        ]
        assert len(bind_issues) >= 1


class TestSecurityReport:
    """Test SecurityReport functionality."""

    def test_empty_report_passes(self):
        """Test that empty report passes."""
        report = SecurityReport()
        assert report.passed

    def test_info_issue_still_passes(self):
        """Test that INFO issues don't fail the report."""
        report = SecurityReport()
        report.add_issue(
            SecurityIssue(
                level=SecurityLevel.INFO,
                message="Test info",
                location="test",
                recommendation="None",
            )
        )
        assert report.passed

    def test_high_issue_fails(self):
        """Test that HIGH issues fail the report."""
        report = SecurityReport()
        report.add_issue(
            SecurityIssue(
                level=SecurityLevel.HIGH,
                message="Test high",
                location="test",
                recommendation="Fix it",
            )
        )
        assert not report.passed

    def test_critical_issue_fails(self):
        """Test that CRITICAL issues fail the report."""
        report = SecurityReport()
        report.add_issue(
            SecurityIssue(
                level=SecurityLevel.CRITICAL,
                message="Test critical",
                location="test",
                recommendation="Fix immediately",
            )
        )
        assert not report.passed


class TestCipherStrengthValidation:
    """Test cipher strength validation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_weak_cipher_rc4_detected(self, parser):
        """Test that RC4 cipher is detected as weak."""
        source = """
        config test {
            global {
                ssl-default-bind-ciphers: "RC4:HIGH:!aNULL:!MD5"
            }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        # Should detect RC4 as weak
        cipher_issues = [
            i for i in report.issues if "rc4" in i.message.lower() or "cipher" in i.message.lower()
        ]
        assert len(cipher_issues) >= 1

    def test_weak_cipher_in_server_ciphers(self, parser):
        """Test weak cipher detection in ssl-default-server-ciphers."""
        source = """
        config test {
            global {
                ssl-default-server-ciphers: "DES:HIGH"
            }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        cipher_issues = [i for i in report.issues if "des" in i.message.lower()]
        assert len(cipher_issues) >= 1


class TestPathTraversalValidation:
    """Test path traversal detection."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_path_traversal_in_chroot(self, parser):
        """Test that path traversal in chroot is detected."""
        source = """
        config test {
            global {
                chroot: "/var/lib/haproxy/../../../tmp"
            }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        traversal_issues = [i for i in report.issues if "traversal" in i.message.lower()]
        assert len(traversal_issues) >= 1
        assert traversal_issues[0].level == SecurityLevel.CRITICAL


class TestListenSectionSecurity:
    """Test listen section security validation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_listen_bind_security(self, parser):
        """Test that listen section bind addresses are checked."""
        source = """
        config test {
            listen stats {
                bind *:8080
                mode: http
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 9000 }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        bind_issues = [i for i in report.issues if "all interfaces" in i.message.lower()]
        assert len(bind_issues) >= 1

    def test_listen_stats_without_auth(self, parser):
        """Test that listen stats without auth is flagged."""
        source = """
        config test {
            listen stats {
                bind *:8080
                mode: http
                stats {
                    enable: true
                    uri: "/stats"
                }
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 9000 }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        stats_issues = [
            i for i in report.issues if "stats" in i.message.lower() and "auth" in i.message.lower()
        ]
        assert len(stats_issues) >= 1


class TestWeakCredentialsValidation:
    """Test weak credentials detection."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_weak_stats_credentials(self, parser):
        """Test that weak stats credentials are detected."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                stats {
                    enable: true
                    uri: "/stats"
                    auth: "admin:admin"
                }
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        weak_creds_issues = [i for i in report.issues if "weak" in i.message.lower()]
        assert len(weak_creds_issues) >= 1
        assert weak_creds_issues[0].level == SecurityLevel.HIGH


class TestStatsAdminValidation:
    """Test stats admin mode validation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_stats_admin_without_auth(self, parser):
        """Test that stats admin without auth is critical."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                stats {
                    enable: true
                    uri: "/stats"
                    admin if TRUE
                }
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        admin_issues = [i for i in report.issues if "admin" in i.message.lower()]
        assert len(admin_issues) >= 1
        # Should have a critical issue for admin without auth
        critical_issues = [
            i for i in report.issues if i.level == SecurityLevel.CRITICAL and "admin" in i.message.lower()
        ]
        assert len(critical_issues) >= 1


class TestPrivilegedPortValidation:
    """Test privileged port detection."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_privileged_port_detected(self, parser):
        """Test that binding to privileged port is detected."""
        source = """
        config test {
            frontend web {
                bind 127.0.0.1:443
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        port_issues = [i for i in report.issues if "privileged port" in i.message.lower()]
        assert len(port_issues) >= 1
        assert port_issues[0].level == SecurityLevel.INFO


class TestResourceLimitsValidation:
    """Test resource limits validation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_high_maxconn_warning(self, parser):
        """Test that very high maxconn generates a warning."""
        source = """
        config test {
            global {
                maxconn: 500000
                chroot: "/var/lib/haproxy"
            }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        maxconn_issues = [i for i in report.issues if "maxconn" in i.message.lower()]
        assert len(maxconn_issues) >= 1
        assert maxconn_issues[0].level == SecurityLevel.LOW


class TestStatsSocketSecurity:
    """Test stats socket security validation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_stats_socket_admin_without_mode(self, parser):
        """Test that stats socket with admin level but no mode restriction is flagged."""
        source = """
        config test {
            global {
                stats_socket "/var/run/haproxy/admin.sock level admin" {
                    level: "admin"
                }
            }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        socket_issues = [i for i in report.issues if "stats socket" in i.message.lower()]
        assert len(socket_issues) >= 1


class TestSensitiveHeaderValidation:
    """Test sensitive header detection in HTTP rules."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_sensitive_header_authorization(self, parser):
        """Test that setting Authorization header is flagged."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                http-request {
                    set_header name: "Authorization" value: "Bearer secret-token"
                }
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 { address: "10.0.0.1" port: 8080 }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        header_issues = [i for i in report.issues if "sensitive header" in i.message.lower()]
        assert len(header_issues) >= 1


class TestServerSSLValidation:
    """Test server SSL configuration validation."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_server_ssl_without_verify(self, parser):
        """Test that server SSL without verify is flagged."""
        source = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }
            backend app {
                balance: roundrobin
                servers {
                    server s1 {
                        address: "10.0.0.1"
                        port: 8080
                        ssl: true
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        ssl_issues = [
            i
            for i in report.issues
            if "ssl" in i.message.lower() and "verification" in i.message.lower()
        ]
        assert len(ssl_issues) >= 1


class TestInsecureSSLOptions:
    """Test insecure SSL options detection."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    def test_force_sslv3_flagged(self, parser):
        """Test that force-sslv3 SSL option is flagged."""
        source = """
        config test {
            frontend web {
                bind *:443 ssl { crt: "/etc/ssl/cert.pem" force-sslv3: true }
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
        """
        ir = parser.parse(source)
        validator = SecurityValidator(ir)
        report = validator.validate()

        ssl_issues = [i for i in report.issues if "insecure ssl" in i.message.lower()]
        assert len(ssl_issues) >= 1


class TestHardcodedSecretsValidation:
    """Test hardcoded secrets detection in server configurations."""

    def test_hardcoded_password_in_server(self):
        """Test that hardcoded password in server is detected."""
        from haproxy_translator.ir.nodes import Backend, ConfigIR, Server

        # Create a server with a hardcoded password in options
        server = Server(
            name="s1",
            address="10.0.0.1",
            port=8080,
            options={"password": "secret123"},
        )
        backend = Backend(name="app", servers=[server])
        ir = ConfigIR(backends=[backend])

        validator = SecurityValidator(ir)
        report = validator.validate()

        secret_issues = [i for i in report.issues if "hardcoded" in i.message.lower()]
        assert len(secret_issues) >= 1
        assert secret_issues[0].level == SecurityLevel.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
