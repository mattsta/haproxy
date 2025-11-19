"""Tests for critical missing features: stats socket, peers, resolvers, mailers."""

import pytest
from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestCriticalFeatures:
    """Test critical missing features implemented for 100% feature parity."""

    # ===== Stats Socket (Runtime API) =====

    def test_stats_socket_basic(self):
        """Test basic stats socket configuration."""
        config = """
        config test {
            global {
                stats_socket "/var/run/haproxy.sock" {
                    level: "admin"
                    mode: "660"
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
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.global_config is not None
        assert len(ir.global_config.stats_sockets) == 1
        assert ir.global_config.stats_sockets[0].path == "/var/run/haproxy.sock"
        assert ir.global_config.stats_sockets[0].level == "admin"
        assert ir.global_config.stats_sockets[0].mode == "660"

        assert "stats socket /var/run/haproxy.sock level admin mode 660" in output

    def test_stats_socket_with_all_options(self):
        """Test stats socket with all options."""
        config = """
        config test {
            global {
                stats_socket "/var/run/haproxy.sock" {
                    level: "admin"
                    mode: "660"
                    user: "haproxy"
                    group: "haproxy"
                    process: "all"
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
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.global_config is not None
        assert len(ir.global_config.stats_sockets) == 1
        socket = ir.global_config.stats_sockets[0]
        assert socket.path == "/var/run/haproxy.sock"
        assert socket.level == "admin"
        assert socket.mode == "660"
        assert socket.user == "haproxy"
        assert socket.group == "haproxy"
        assert socket.process == "all"

        assert "stats socket /var/run/haproxy.sock" in output
        assert "level admin" in output
        assert "mode 660" in output
        assert "user haproxy" in output
        assert "group haproxy" in output
        assert "process all" in output

    def test_multiple_stats_sockets(self):
        """Test multiple stats socket configurations."""
        config = """
        config test {
            global {
                stats_socket "/var/run/haproxy.sock" {
                    level: "admin"
                }

                stats_socket "127.0.0.1:9999" {
                    level: "operator"
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
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert ir.global_config is not None
        assert len(ir.global_config.stats_sockets) == 2
        assert ir.global_config.stats_sockets[0].path == "/var/run/haproxy.sock"
        assert ir.global_config.stats_sockets[1].path == "127.0.0.1:9999"

        assert "stats socket /var/run/haproxy.sock level admin" in output
        assert "stats socket 127.0.0.1:9999 level operator" in output

    # ===== Peers Section =====

    def test_peers_section_basic(self):
        """Test basic peers section for stick table replication."""
        config = """
        config test {
            peers mypeers {
                peer haproxy1 "10.0.0.1" 1024
                peer haproxy2 "10.0.0.2" 1024
                peer haproxy3 "10.0.0.3" 1024
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

        assert len(ir.peers) == 1
        assert ir.peers[0].name == "mypeers"
        assert len(ir.peers[0].peers) == 3
        assert ir.peers[0].peers[0].name == "haproxy1"
        assert ir.peers[0].peers[0].address == "10.0.0.1"
        assert ir.peers[0].peers[0].port == 1024

        assert "peers mypeers" in output
        assert "peer haproxy1 10.0.0.1:1024" in output
        assert "peer haproxy2 10.0.0.2:1024" in output
        assert "peer haproxy3 10.0.0.3:1024" in output

    def test_peers_section_disabled(self):
        """Test peers section with disabled flag."""
        config = """
        config test {
            peers mypeers {
                disabled: true
                peer haproxy1 "10.0.0.1" 1024
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

        assert len(ir.peers) == 1
        assert ir.peers[0].disabled is True

        assert "peers mypeers" in output
        assert "disabled" in output

    # ===== Resolvers Section =====

    def test_resolvers_section_basic(self):
        """Test basic resolvers section for DNS resolution."""
        config = """
        config test {
            resolvers mydns {
                nameserver dns1 "8.8.8.8" 53
                nameserver dns2 "8.8.4.4" 53
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

        assert len(ir.resolvers) == 1
        assert ir.resolvers[0].name == "mydns"
        assert len(ir.resolvers[0].nameservers) == 2
        assert ir.resolvers[0].nameservers[0].name == "dns1"
        assert ir.resolvers[0].nameservers[0].address == "8.8.8.8"
        assert ir.resolvers[0].nameservers[0].port == 53

        assert "resolvers mydns" in output
        assert "nameserver dns1 8.8.8.8:53" in output
        assert "nameserver dns2 8.8.4.4:53" in output

    def test_resolvers_section_with_options(self):
        """Test resolvers section with timeout and hold options."""
        config = """
        config test {
            resolvers mydns {
                nameserver dns1 "8.8.8.8" 53

                accepted_payload_size: 8192
                hold_nx: 30s
                hold_valid: 10s
                hold_timeout: 30s
                resolve_retries: 3
                timeout_resolve: 1s
                timeout_retry: 1s
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

        assert len(ir.resolvers) == 1
        resolvers = ir.resolvers[0]
        assert resolvers.accepted_payload_size == 8192
        assert resolvers.hold_nx == "30s"
        assert resolvers.hold_valid == "10s"
        assert resolvers.hold_timeout == "30s"
        assert resolvers.resolve_retries == 3
        assert resolvers.timeout_resolve == "1s"
        assert resolvers.timeout_retry == "1s"

        assert "resolvers mydns" in output
        assert "accepted_payload_size 8192" in output
        assert "hold nx 30s" in output
        assert "hold valid 10s" in output
        assert "hold timeout 30s" in output
        assert "resolve_retries 3" in output
        assert "timeout resolve 1s" in output
        assert "timeout retry 1s" in output

    # ===== Mailers Section =====

    def test_mailers_section_basic(self):
        """Test basic mailers section for email alerts."""
        config = """
        config test {
            mailers mymailers {
                mailer smtp1 "smtp1.example.com" 587
                mailer smtp2 "smtp2.example.com" 587
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

        assert len(ir.mailers) == 1
        assert ir.mailers[0].name == "mymailers"
        assert len(ir.mailers[0].mailers) == 2
        assert ir.mailers[0].mailers[0].name == "smtp1"
        assert ir.mailers[0].mailers[0].address == "smtp1.example.com"
        assert ir.mailers[0].mailers[0].port == 587

        assert "mailers mymailers" in output
        assert "mailer smtp1 smtp1.example.com:587" in output
        assert "mailer smtp2 smtp2.example.com:587" in output

    def test_mailers_section_with_timeout(self):
        """Test mailers section with timeout_mail."""
        config = """
        config test {
            mailers mymailers {
                timeout_mail: 10s
                mailer smtp1 "smtp.example.com" 25
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

        assert len(ir.mailers) == 1
        assert ir.mailers[0].timeout_mail == "10s"

        assert "mailers mymailers" in output
        assert "timeout mail 10s" in output
        assert "mailer smtp1 smtp.example.com:25" in output

    # ===== Integration Tests =====

    def test_all_critical_features_together(self):
        """Test all critical features in one configuration."""
        config = """
        config production {
            global {
                daemon: true

                stats_socket "/var/run/haproxy.sock" {
                    level: "admin"
                    mode: "660"
                }
            }

            peers mycluster {
                peer lb1 "10.0.0.1" 1024
                peer lb2 "10.0.0.2" 1024
            }

            resolvers mydns {
                nameserver dns1 "8.8.8.8" 53
                nameserver dns2 "8.8.4.4" 53
                timeout_resolve: 1s
            }

            mailers alerts {
                timeout_mail: 10s
                mailer smtp "smtp.example.com" 587
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

        # Verify all sections are present
        assert "stats socket /var/run/haproxy.sock level admin mode 660" in output
        assert "peers mycluster" in output
        assert "peer lb1 10.0.0.1:1024" in output
        assert "resolvers mydns" in output
        assert "nameserver dns1 8.8.8.8:53" in output
        assert "mailers alerts" in output
        assert "mailer smtp smtp.example.com:587" in output

        # Verify IR structure
        assert len(ir.global_config.stats_sockets) == 1
        assert len(ir.peers) == 1
        assert len(ir.resolvers) == 1
        assert len(ir.mailers) == 1
