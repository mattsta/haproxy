"""Tests for Phase 10 batch 2 - Resource Limits directives."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestPhase10ResourceLimits:
    """Test Phase 10 batch 2 resource limit directives."""

    def test_fd_hard_limit(self):
        """Test fd-hard-limit directive - maximum file descriptors."""
        config = """
        config test {
            global {
                fd-hard-limit: 65536
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fd_hard_limit == 65536

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "fd-hard-limit 65536" in output

    def test_fd_hard_limit_large(self):
        """Test fd-hard-limit with large value."""
        config = """
        config test {
            global {
                fd-hard-limit: 1048576
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fd_hard_limit == 1048576

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "fd-hard-limit 1048576" in output

    def test_maxzlibmem(self):
        """Test maxzlibmem directive - memory limit for zlib compression."""
        config = """
        config test {
            global {
                maxzlibmem: 8192
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxzlibmem == 8192

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxzlibmem 8192" in output

    def test_maxzlibmem_large(self):
        """Test maxzlibmem with large memory value."""
        config = """
        config test {
            global {
                maxzlibmem: 65536
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxzlibmem == 65536

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxzlibmem 65536" in output

    def test_strict_limits_on(self):
        """Test strict-limits directive set to true."""
        config = """
        config test {
            global {
                strict-limits: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.strict_limits is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "strict-limits on" in output

    def test_strict_limits_off(self):
        """Test strict-limits directive set to false."""
        config = """
        config test {
            global {
                strict-limits: false
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.strict_limits is False

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "strict-limits off" in output

    def test_all_resource_limits(self):
        """Test all Phase 10 batch 2 resource limits together."""
        config = """
        config test {
            global {
                fd-hard-limit: 131072
                maxzlibmem: 16384
                strict-limits: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fd_hard_limit == 131072
        assert ir.global_config.maxzlibmem == 16384
        assert ir.global_config.strict_limits is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "fd-hard-limit 131072" in output
        assert "maxzlibmem 16384" in output
        assert "strict-limits on" in output

    def test_resource_limits_with_ulimit(self):
        """Test resource limits with ulimit-n for comparison."""
        config = """
        config test {
            global {
                ulimit-n: 200000
                fd-hard-limit: 200000
                strict-limits: true
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.tuning.get("ulimit_n") == 200000
        assert ir.global_config.fd_hard_limit == 200000
        assert ir.global_config.strict_limits is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "ulimit-n 200000" in output
        assert "fd-hard-limit 200000" in output
        assert "strict-limits on" in output

    def test_resource_limits_with_maxconn(self):
        """Test resource limits with connection limits."""
        config = """
        config test {
            global {
                maxconn: 50000
                fd-hard-limit: 100000
                maxzlibmem: 32768
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxconn == 50000
        assert ir.global_config.fd_hard_limit == 100000
        assert ir.global_config.maxzlibmem == 32768

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxconn 50000" in output
        assert "fd-hard-limit 100000" in output
        assert "maxzlibmem 32768" in output

    def test_resource_limits_in_production_config(self):
        """Test resource limits in a production configuration."""
        config = """
        config production {
            global {
                daemon: true
                maxconn: 100000
                nbthread: 8
                fd-hard-limit: 200000
                maxzlibmem: 65536
                strict-limits: true
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
        assert ir.global_config.nbthread == 8
        assert ir.global_config.fd_hard_limit == 200000
        assert ir.global_config.maxzlibmem == 65536
        assert ir.global_config.strict_limits is True

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "daemon" in output
        assert "maxconn 100000" in output
        assert "nbthread 8" in output
        assert "fd-hard-limit 200000" in output
        assert "maxzlibmem 65536" in output
        assert "strict-limits on" in output

    def test_fd_hard_limit_minimal(self):
        """Test fd-hard-limit with minimal value."""
        config = """
        config test {
            global {
                fd-hard-limit: 1024
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.fd_hard_limit == 1024

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "fd-hard-limit 1024" in output

    def test_maxzlibmem_minimal(self):
        """Test maxzlibmem with minimal value."""
        config = """
        config test {
            global {
                maxzlibmem: 1024
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.maxzlibmem == 1024

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "maxzlibmem 1024" in output

    def test_strict_limits_with_threading(self):
        """Test strict-limits with threading directives."""
        config = """
        config test {
            global {
                nbthread: 16
                thread-groups: 4
                strict-limits: true
                fd-hard-limit: 262144
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 16
        assert ir.global_config.thread_groups == 4
        assert ir.global_config.strict_limits is True
        assert ir.global_config.fd_hard_limit == 262144

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "nbthread 16" in output
        assert "thread-groups 4" in output
        assert "strict-limits on" in output
        assert "fd-hard-limit 262144" in output
