"""Phase 13 Batch 3: Lua global directives tests."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers.dsl_parser import DSLParser


class TestPhase13Lua:
    """Test Phase 13 Batch 3: Lua global directives."""

    def test_lua_load_simple(self):
        """Test basic lua-load directive."""
        config = """
        config test {
            global {
                daemon: false
                lua-load "/etc/haproxy/scripts/main.lua"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.global_config.lua_load_files) == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "lua-load /etc/haproxy/scripts/main.lua" in output

    def test_lua_load_with_args(self):
        """Test lua-load with command-line arguments."""
        config = """
        config test {
            global {
                daemon: false
                lua-load "/etc/haproxy/scripts/config.lua" "arg1" "arg2" "arg3"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.global_config.lua_load_files) == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "lua-load /etc/haproxy/scripts/config.lua arg1 arg2 arg3" in output

    def test_lua_load_per_thread_simple(self):
        """Test basic lua-load-per-thread directive."""
        config = """
        config test {
            global {
                daemon: false
                nbthread: 4
                lua-load-per-thread "/etc/haproxy/scripts/worker.lua"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 4
        assert len(ir.global_config.lua_load_per_thread_files) == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "lua-load-per-thread /etc/haproxy/scripts/worker.lua" in output

    def test_lua_prepend_path_default(self):
        """Test lua-prepend-path with default type."""
        config = """
        config test {
            global {
                daemon: false
                lua-prepend-path "/usr/local/share/lua/5.3/?.lua"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.global_config.lua_prepend_paths) == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "lua-prepend-path /usr/local/share/lua/5.3/?.lua" in output

    def test_lua_prepend_path_cpath(self):
        """Test lua-prepend-path with cpath type."""
        config = """
        config test {
            global {
                daemon: false
                lua-prepend-path "/usr/local/lib/lua/5.3/?.so" "cpath"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.global_config.lua_prepend_paths) == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "lua-prepend-path /usr/local/lib/lua/5.3/?.so cpath" in output

    def test_lua_complete_setup(self):
        """Test complete Lua setup."""
        config = """
        config test {
            global {
                daemon: false
                nbthread: 4
                lua-prepend-path "/opt/haproxy/lua/?.lua"
                lua-prepend-path "/opt/haproxy/lua/lib/?.so" "cpath"
                lua-load "/opt/haproxy/lua/lib/utils.lua"
                lua-load-per-thread "/opt/haproxy/lua/worker.lua" "worker_id"
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 4
        assert len(ir.global_config.lua_prepend_paths) == 2
        assert len(ir.global_config.lua_load_files) == 1
        assert len(ir.global_config.lua_load_per_thread_files) == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "lua-prepend-path /opt/haproxy/lua/?.lua" in output
        assert "lua-prepend-path /opt/haproxy/lua/lib/?.so cpath" in output
        assert "lua-load /opt/haproxy/lua/lib/utils.lua" in output
        assert "lua-load-per-thread /opt/haproxy/lua/worker.lua worker_id" in output

    def test_lua_with_tuning(self):
        """Test Lua directives with tuning."""
        config = """
        config test {
            global {
                daemon: true
                nbthread: 16
                lua-prepend-path "/usr/local/share/haproxy/lua/?.lua"
                lua-load "/usr/local/share/haproxy/lua/lib/auth.lua" "production"
                tune.lua.maxmem: 104857600
                tune.lua.session-timeout: "10s"
                tune.lua.forced-yield: 10000
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.global_config.nbthread == 16
        assert len(ir.global_config.lua_prepend_paths) == 1
        assert len(ir.global_config.lua_load_files) == 1

        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)
        assert "lua-prepend-path /usr/local/share/haproxy/lua/?.lua" in output
        assert "lua-load /usr/local/share/haproxy/lua/lib/auth.lua production" in output
        assert "tune.lua.maxmem 104857600" in output
        assert "tune.lua.session-timeout 10s" in output
        assert "tune.lua.forced-yield 10000" in output
