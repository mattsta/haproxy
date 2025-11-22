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
            i for i in report.issues
            if i.level in (SecurityLevel.CRITICAL, SecurityLevel.HIGH)
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
        root_issues = [
            i for i in report.issues
            if "root" in i.message.lower()
        ]
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
        chroot_issues = [
            i for i in report.issues
            if "chroot" in i.message.lower()
        ]
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
            i for i in report.issues
            if "stats" in i.message.lower() and "auth" in i.message.lower()
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
            i for i in report.issues
            if "ssl" in i.message.lower() and "cert" in i.message.lower()
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
            i for i in report.issues
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
            i for i in report.issues
            if "rc4" in i.message.lower() or "cipher" in i.message.lower()
        ]
        assert len(cipher_issues) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
