"""Tests for Phase 10 batch 3 - Server State Management directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase10ServerState:
    """Test Phase 10 batch 3 server state management directives."""

    def test_server_state_base(self):
        """Test server-state-base directive - directory for server state files."""
        config = """
        config test {
            global {
                server-state-base: "/var/lib/haproxy/state"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.server_state_base == "/var/lib/haproxy/state"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "server-state-base /var/lib/haproxy/state" in output

    def test_server_state_base_relative(self):
        """Test server-state-base with relative path."""
        config = """
        config test {
            global {
                server-state-base: "/etc/haproxy/states"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.server_state_base == "/etc/haproxy/states"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "server-state-base /etc/haproxy/states" in output

    def test_server_state_file(self):
        """Test server-state-file directive - server state file name."""
        config = """
        config test {
            global {
                server-state-file: "global.state"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.server_state_file == "global.state"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "server-state-file global.state" in output

    def test_server_state_file_custom(self):
        """Test server-state-file with custom file name."""
        config = """
        config test {
            global {
                server-state-file: "haproxy-servers.state"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.server_state_file == "haproxy-servers.state"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "server-state-file haproxy-servers.state" in output

    def test_load_server_state_from_file_global(self):
        """Test load-server-state-from-file directive - restore state at startup."""
        config = """
        config test {
            global {
                load-server-state-from-file: "global"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.load_server_state_from_file == "global"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "load-server-state-from-file global" in output

    def test_load_server_state_from_file_local(self):
        """Test load-server-state-from-file with local setting."""
        config = """
        config test {
            global {
                load-server-state-from-file: "local"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.load_server_state_from_file == "local"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "load-server-state-from-file local" in output

    def test_load_server_state_from_file_none(self):
        """Test load-server-state-from-file with none setting."""
        config = """
        config test {
            global {
                load-server-state-from-file: "none"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.load_server_state_from_file == "none"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "load-server-state-from-file none" in output

    def test_all_server_state_directives(self):
        """Test all Phase 10 batch 3 server state directives together."""
        config = """
        config test {
            global {
                server-state-base: "/var/lib/haproxy"
                server-state-file: "server-state"
                load-server-state-from-file: "global"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.server_state_base == "/var/lib/haproxy"
        assert ir.global_config.server_state_file == "server-state"
        assert ir.global_config.load_server_state_from_file == "global"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "server-state-base /var/lib/haproxy" in output
        assert "server-state-file server-state" in output
        assert "load-server-state-from-file global" in output

    def test_server_state_with_paths(self):
        """Test server state directives with other path directives."""
        config = """
        config test {
            global {
                ca-base: "/etc/ssl/certs"
                crt-base: "/etc/ssl/private"
                server-state-base: "/var/lib/haproxy/state"
                server-state-file: "servers.state"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.ca_base == "/etc/ssl/certs"
        assert ir.global_config.crt_base == "/etc/ssl/private"
        assert ir.global_config.server_state_base == "/var/lib/haproxy/state"
        assert ir.global_config.server_state_file == "servers.state"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ca-base /etc/ssl/certs" in output
        assert "crt-base /etc/ssl/private" in output
        assert "server-state-base /var/lib/haproxy/state" in output
        assert "server-state-file servers.state" in output

    def test_server_state_in_production_config(self):
        """Test server state directives in a production configuration."""
        config = """
        config production {
            global {
                daemon: true
                maxconn: 100000
                server-state-base: "/var/lib/haproxy"
                server-state-file: "global.state"
                load-server-state-from-file: "global"
                user: "haproxy"
                group: "haproxy"
            }

            defaults {
                mode: http
            }

            frontend web {
                mode: http
            }

            backend servers {
                mode: http
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.daemon is True
        assert ir.global_config.maxconn == 100000
        assert ir.global_config.server_state_base == "/var/lib/haproxy"
        assert ir.global_config.server_state_file == "global.state"
        assert ir.global_config.load_server_state_from_file == "global"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "daemon" in output
        assert "maxconn 100000" in output
        assert "server-state-base /var/lib/haproxy" in output
        assert "server-state-file global.state" in output
        assert "load-server-state-from-file global" in output

    def test_server_state_with_threading(self):
        """Test server state with threading directives."""
        config = """
        config test {
            global {
                nbthread: 8
                thread-groups: 2
                server-state-base: "/var/lib/haproxy"
                load-server-state-from-file: "global"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 8
        assert ir.global_config.thread_groups == 2
        assert ir.global_config.server_state_base == "/var/lib/haproxy"
        assert ir.global_config.load_server_state_from_file == "global"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 8" in output
        assert "thread-groups 2" in output
        assert "server-state-base /var/lib/haproxy" in output
        assert "load-server-state-from-file global" in output

    def test_server_state_with_resource_limits(self):
        """Test server state with resource limit directives."""
        config = """
        config test {
            global {
                fd-hard-limit: 200000
                server-state-base: "/var/lib/haproxy"
                server-state-file: "state.db"
                strict-limits: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fd_hard_limit == 200000
        assert ir.global_config.server_state_base == "/var/lib/haproxy"
        assert ir.global_config.server_state_file == "state.db"
        assert ir.global_config.strict_limits is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "fd-hard-limit 200000" in output
        assert "server-state-base /var/lib/haproxy" in output
        assert "server-state-file state.db" in output
        assert "strict-limits on" in output

    def test_server_state_seamless_reload(self):
        """Test server state for seamless reload scenario."""
        config = """
        config test {
            global {
                daemon: true
                master-worker: true
                server-state-base: "/var/run/haproxy"
                server-state-file: "runtime.state"
                load-server-state-from-file: "global"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.daemon is True
        assert ir.global_config.master_worker is True
        assert ir.global_config.server_state_base == "/var/run/haproxy"
        assert ir.global_config.server_state_file == "runtime.state"
        assert ir.global_config.load_server_state_from_file == "global"

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "daemon" in output
        assert "master-worker" in output
        assert "server-state-base /var/run/haproxy" in output
        assert "server-state-file runtime.state" in output
        assert "load-server-state-from-file global" in output
