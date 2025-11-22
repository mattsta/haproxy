"""Tests for Phase 14 Remaining Global Directives (30 directives)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase14SecurityProcessManagement:
    """Test security and process management directives."""

    def test_cluster_secret(self):
        """Test cluster-secret directive."""
        config = """
        config test {
            global {
                cluster-secret: "my_secret_key_12345"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.cluster_secret == "my_secret_key_12345"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "cluster-secret my_secret_key_12345" in output

    def test_expose_deprecated_directives(self):
        """Test expose-deprecated-directives directive."""
        config = """
        config test {
            global {
                expose-deprecated-directives: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.expose_deprecated_directives is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "expose-deprecated-directives" in output

    def test_expose_experimental_directives(self):
        """Test expose-experimental-directives directive."""
        config = """
        config test {
            global {
                expose-experimental-directives: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.expose_experimental_directives is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "expose-experimental-directives" in output

    def test_insecure_fork_wanted(self):
        """Test insecure-fork-wanted directive."""
        config = """
        config test {
            global {
                insecure-fork-wanted: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.insecure_fork_wanted is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "insecure-fork-wanted" in output

    def test_insecure_setuid_wanted(self):
        """Test insecure-setuid-wanted directive."""
        config = """
        config test {
            global {
                insecure-setuid-wanted: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.insecure_setuid_wanted is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "insecure-setuid-wanted" in output

    def test_harden_reject_privileged_ports_quic(self):
        """Test harden.reject-privileged-ports.quic directive."""
        config = """
        config test {
            global {
                harden.reject-privileged-ports.quic: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.harden_reject_privileged_ports_quic is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "harden.reject-privileged-ports.quic on" in output

    def test_harden_reject_privileged_ports_tcp(self):
        """Test harden.reject-privileged-ports.tcp directive."""
        config = """
        config test {
            global {
                harden.reject-privileged-ports.tcp: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.harden_reject_privileged_ports_tcp is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "harden.reject-privileged-ports.tcp on" in output

    def test_pp2_never_send_local(self):
        """Test pp2-never-send-local directive."""
        config = """
        config test {
            global {
                pp2-never-send-local: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.pp2_never_send_local is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "pp2-never-send-local" in output

    def test_prealloc_fd(self):
        """Test prealloc-fd directive."""
        config = """
        config test {
            global {
                prealloc-fd: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.prealloc_fd is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "prealloc-fd" in output

    def test_ssl_skip_self_issued_ca(self):
        """Test ssl-skip-self-issued-ca directive."""
        config = """
        config test {
            global {
                ssl-skip-self-issued-ca: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ssl_skip_self_issued_ca is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ssl-skip-self-issued-ca" in output

    def test_grace(self):
        """Test grace directive."""
        config = """
        config test {
            global {
                grace: "10s"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.grace == "10s"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "grace 10s" in output

    def test_stats_file(self):
        """Test stats-file directive."""
        config = """
        config test {
            global {
                stats-file: "/var/lib/haproxy/stats.sock"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.stats_file == "/var/lib/haproxy/stats.sock"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "stats-file /var/lib/haproxy/stats.sock" in output


class TestPhase14CPUManagement:
    """Test CPU management directives."""

    def test_cpu_policy(self):
        """Test cpu-policy directive."""
        config = """
        config test {
            global {
                cpu-policy: "numa"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.cpu_policy == "numa"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "cpu-policy numa" in output

    def test_cpu_set(self):
        """Test cpu-set directive."""
        config = """
        config test {
            global {
                cpu-set: "0-3"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.cpu_set == "0-3"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "cpu-set 0-3" in output


class TestPhase14DNS:
    """Test DNS directives."""

    def test_dns_accept_family(self):
        """Test dns-accept-family directive."""
        config = """
        config test {
            global {
                dns-accept-family: "ipv4"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.dns_accept_family == "ipv4"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "dns-accept-family ipv4" in output


class TestPhase14HTTP1Protocol:
    """Test HTTP/1 protocol directives."""

    def test_h1_accept_payload_with_any_method(self):
        """Test h1-accept-payload-with-any-method directive."""
        config = """
        config test {
            global {
                h1-accept-payload-with-any-method: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.h1_accept_payload_with_any_method is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "h1-accept-payload-with-any-method" in output

    def test_h1_case_adjust(self):
        """Test h1-case-adjust directive."""
        config = """
        config test {
            global {
                h1-case-adjust: "content-type Content-Type"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.h1_case_adjust == "content-type Content-Type"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "h1-case-adjust content-type Content-Type" in output

    def test_h1_case_adjust_file(self):
        """Test h1-case-adjust-file directive."""
        config = """
        config test {
            global {
                h1-case-adjust-file: "/etc/haproxy/headers.map"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.h1_case_adjust_file == "/etc/haproxy/headers.map"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "h1-case-adjust-file /etc/haproxy/headers.map" in output

    def test_h1_do_not_close_on_insecure_transfer_encoding(self):
        """Test h1-do-not-close-on-insecure-transfer-encoding directive."""
        config = """
        config test {
            global {
                h1-do-not-close-on-insecure-transfer-encoding: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.h1_do_not_close_on_insecure_transfer_encoding is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "h1-do-not-close-on-insecure-transfer-encoding" in output


class TestPhase14HTTP2Protocol:
    """Test HTTP/2 protocol directives."""

    def test_h2_workaround_bogus_websocket_clients(self):
        """Test h2-workaround-bogus-websocket-clients directive."""
        config = """
        config test {
            global {
                h2-workaround-bogus-websocket-clients: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.h2_workaround_bogus_websocket_clients is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "h2-workaround-bogus-websocket-clients" in output


class TestPhase14OCSPUpdate:
    """Test OCSP update directives."""

    def test_ocsp_update_disable(self):
        """Test ocsp-update.disable directive."""
        config = """
        config test {
            global {
                ocsp-update.disable: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ocsp_update_disable is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ocsp-update.disable" in output

    def test_ocsp_update_httpproxy(self):
        """Test ocsp-update.httpproxy directive."""
        config = """
        config test {
            global {
                ocsp-update.httpproxy: "http://proxy.example.com:8080"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ocsp_update_httpproxy == "http://proxy.example.com:8080"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ocsp-update.httpproxy http://proxy.example.com:8080" in output

    def test_ocsp_update_maxdelay(self):
        """Test ocsp-update.maxdelay directive."""
        config = """
        config test {
            global {
                ocsp-update.maxdelay: 3600
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ocsp_update_maxdelay == 3600

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ocsp-update.maxdelay 3600" in output

    def test_ocsp_update_mindelay(self):
        """Test ocsp-update.mindelay directive."""
        config = """
        config test {
            global {
                ocsp-update.mindelay: 60
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ocsp_update_mindelay == 60

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ocsp-update.mindelay 60" in output

    def test_ocsp_update_mode(self):
        """Test ocsp-update.mode directive."""
        config = """
        config test {
            global {
                ocsp-update.mode: "on"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ocsp_update_mode == "on"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ocsp-update.mode on" in output


class TestPhase1451DegreesAdditional:
    """Test 51Degrees additional directives."""

    def test_51degrees_allow_unmatched(self):
        """Test 51degrees-allow-unmatched directive."""
        config = """
        config test {
            global {
                51degrees-allow-unmatched: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_allow_unmatched is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-allow-unmatched on" in output

    def test_51degrees_difference(self):
        """Test 51degrees-difference directive."""
        config = """
        config test {
            global {
                51degrees-difference: 5
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_difference == 5

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-difference 5" in output

    def test_51degrees_drift(self):
        """Test 51degrees-drift directive."""
        config = """
        config test {
            global {
                51degrees-drift: 10
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_drift == 10

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-drift 10" in output

    def test_51degrees_use_performance_graph(self):
        """Test 51degrees-use-performance-graph directive."""
        config = """
        config test {
            global {
                51degrees-use-performance-graph: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_use_performance_graph is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-use-performance-graph on" in output

    def test_51degrees_use_predictive_graph(self):
        """Test 51degrees-use-predictive-graph directive."""
        config = """
        config test {
            global {
                51degrees-use-predictive-graph: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_use_predictive_graph is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-use-predictive-graph on" in output


class TestPhase14Variables:
    """Test variables directives."""

    def test_set_var(self):
        """Test set-var directive."""
        config = """
        config test {
            global {
                set-var "proc.myvar": "myvalue"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.set_vars.get("proc.myvar") == "myvalue"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "set-var proc.myvar myvalue" in output


class TestPhase14Integration:
    """Test integration of all Phase 14 directives."""

    def test_complete_security_configuration(self):
        """Test complete security configuration."""
        config = """
        config test {
            global {
                cluster-secret: "secure_cluster_key"
                expose-experimental-directives: true
                harden.reject-privileged-ports.tcp: true
                harden.reject-privileged-ports.quic: true
                ssl-skip-self-issued-ca: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.cluster_secret == "secure_cluster_key"
        assert ir.global_config.expose_experimental_directives is True
        assert ir.global_config.harden_reject_privileged_ports_tcp is True
        assert ir.global_config.harden_reject_privileged_ports_quic is True
        assert ir.global_config.ssl_skip_self_issued_ca is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "cluster-secret secure_cluster_key" in output
        assert "expose-experimental-directives" in output
        assert "harden.reject-privileged-ports.tcp on" in output
        assert "harden.reject-privileged-ports.quic on" in output
        assert "ssl-skip-self-issued-ca" in output

    def test_complete_http_protocol_configuration(self):
        """Test complete HTTP protocol configuration."""
        config = """
        config test {
            global {
                h1-accept-payload-with-any-method: true
                h1-case-adjust-file: "/etc/haproxy/headers.map"
                h2-workaround-bogus-websocket-clients: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.h1_accept_payload_with_any_method is True
        assert ir.global_config.h1_case_adjust_file == "/etc/haproxy/headers.map"
        assert ir.global_config.h2_workaround_bogus_websocket_clients is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "h1-accept-payload-with-any-method" in output
        assert "h1-case-adjust-file /etc/haproxy/headers.map" in output
        assert "h2-workaround-bogus-websocket-clients" in output

    def test_complete_ocsp_configuration(self):
        """Test complete OCSP configuration."""
        config = """
        config test {
            global {
                ocsp-update.mode: "on"
                ocsp-update.httpproxy: "http://proxy.local:3128"
                ocsp-update.mindelay: 300
                ocsp-update.maxdelay: 7200
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ocsp_update_mode == "on"
        assert ir.global_config.ocsp_update_httpproxy == "http://proxy.local:3128"
        assert ir.global_config.ocsp_update_mindelay == 300
        assert ir.global_config.ocsp_update_maxdelay == 7200

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ocsp-update.mode on" in output
        assert "ocsp-update.httpproxy http://proxy.local:3128" in output
        assert "ocsp-update.mindelay 300" in output
        assert "ocsp-update.maxdelay 7200" in output

    def test_complete_51degrees_configuration(self):
        """Test complete 51Degrees extended configuration."""
        config = """
        config test {
            global {
                51degrees-data-file: "/etc/51degrees.dat"
                51degrees-allow-unmatched: true
                51degrees-difference: 10
                51degrees-drift: 5
                51degrees-use-performance-graph: true
                51degrees-use-predictive-graph: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fiftyone_degrees_data_file == "/etc/51degrees.dat"
        assert ir.global_config.fiftyone_degrees_allow_unmatched is True
        assert ir.global_config.fiftyone_degrees_difference == 10
        assert ir.global_config.fiftyone_degrees_drift == 5
        assert ir.global_config.fiftyone_degrees_use_performance_graph is True
        assert ir.global_config.fiftyone_degrees_use_predictive_graph is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "51degrees-data-file /etc/51degrees.dat" in output
        assert "51degrees-allow-unmatched on" in output
        assert "51degrees-difference 10" in output
        assert "51degrees-drift 5" in output
        assert "51degrees-use-performance-graph on" in output
        assert "51degrees-use-predictive-graph off" in output

    def test_all_phase14_directives_together(self):
        """Test all Phase 14 directives together in one configuration."""
        config = """
        config test {
            global {
                // Security & Process Management
                cluster-secret: "cluster_key_123"
                expose-deprecated-directives: true
                expose-experimental-directives: true
                insecure-fork-wanted: true
                insecure-setuid-wanted: true
                harden.reject-privileged-ports.quic: true
                harden.reject-privileged-ports.tcp: true
                pp2-never-send-local: true
                prealloc-fd: true
                ssl-skip-self-issued-ca: true
                grace: "30s"
                stats-file: "/var/stats.sock"

                // CPU Management
                cpu-policy: "numa"
                cpu-set: "0-7"

                // DNS
                dns-accept-family: "ipv4"

                // HTTP/1 Protocol
                h1-accept-payload-with-any-method: true
                h1-case-adjust: "host Host"
                h1-case-adjust-file: "/etc/headers.map"
                h1-do-not-close-on-insecure-transfer-encoding: true

                // HTTP/2 Protocol
                h2-workaround-bogus-websocket-clients: true

                // OCSP Update
                ocsp-update.disable: false
                ocsp-update.httpproxy: "http://proxy:8080"
                ocsp-update.maxdelay: 3600
                ocsp-update.mindelay: 60
                ocsp-update.mode: "on"

                // 51Degrees Additional
                51degrees-allow-unmatched: true
                51degrees-difference: 5
                51degrees-drift: 10
                51degrees-use-performance-graph: true
                51degrees-use-predictive-graph: true

                // Variables
                set-var "proc.myvar": "value1"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        # Verify all properties are set
        assert ir.global_config.cluster_secret == "cluster_key_123"
        assert ir.global_config.expose_deprecated_directives is True
        assert ir.global_config.expose_experimental_directives is True
        assert ir.global_config.insecure_fork_wanted is True
        assert ir.global_config.insecure_setuid_wanted is True
        assert ir.global_config.harden_reject_privileged_ports_quic is True
        assert ir.global_config.harden_reject_privileged_ports_tcp is True
        assert ir.global_config.pp2_never_send_local is True
        assert ir.global_config.prealloc_fd is True
        assert ir.global_config.ssl_skip_self_issued_ca is True
        assert ir.global_config.grace == "30s"
        assert ir.global_config.stats_file == "/var/stats.sock"
        assert ir.global_config.cpu_policy == "numa"
        assert ir.global_config.cpu_set == "0-7"
        assert ir.global_config.dns_accept_family == "ipv4"
        assert ir.global_config.h1_accept_payload_with_any_method is True
        assert ir.global_config.h1_case_adjust == "host Host"
        assert ir.global_config.h1_case_adjust_file == "/etc/headers.map"
        assert ir.global_config.h1_do_not_close_on_insecure_transfer_encoding is True
        assert ir.global_config.h2_workaround_bogus_websocket_clients is True
        assert ir.global_config.ocsp_update_disable is False
        assert ir.global_config.ocsp_update_httpproxy == "http://proxy:8080"
        assert ir.global_config.ocsp_update_maxdelay == 3600
        assert ir.global_config.ocsp_update_mindelay == 60
        assert ir.global_config.ocsp_update_mode == "on"
        assert ir.global_config.fiftyone_degrees_allow_unmatched is True
        assert ir.global_config.fiftyone_degrees_difference == 5
        assert ir.global_config.fiftyone_degrees_drift == 10
        assert ir.global_config.fiftyone_degrees_use_performance_graph is True
        assert ir.global_config.fiftyone_degrees_use_predictive_graph is True
        assert ir.global_config.set_vars.get("proc.myvar") == "value1"

        # Generate and verify output
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "cluster-secret cluster_key_123" in output
        assert "expose-deprecated-directives" in output
        assert "expose-experimental-directives" in output
        assert "grace 30s" in output
        assert "cpu-policy numa" in output
        assert "dns-accept-family ipv4" in output
        assert "h1-case-adjust host Host" in output
        assert "ocsp-update.mode on" in output
        assert "51degrees-drift 10" in output
        assert "set-var proc.myvar value1" in output
