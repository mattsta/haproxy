"""Tests for loop unrolling transformer."""

import pytest

from haproxy_translator.parsers import DSLParser
from haproxy_translator.transformers.loop_unroller import LoopUnroller
from haproxy_translator.utils.errors import ParseError


class TestLoopUnrolling:
    """Test loop unrolling functionality."""

    @pytest.fixture
    def parser(self):
        """Create a DSL parser."""
        return DSLParser()

    def test_basic_range_loop(self, parser):
        """Test basic for loop with range."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    for i in [1..3] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Should have 3 servers
        backend = ir.backends[0]
        assert len(backend.servers) == 3
        assert backend.servers[0].name == "web1"
        assert backend.servers[0].address == "10.0.1.1"
        assert backend.servers[1].name == "web2"
        assert backend.servers[1].address == "10.0.1.2"
        assert backend.servers[2].name == "web3"
        assert backend.servers[2].address == "10.0.1.3"

    def test_loop_with_arithmetic(self, parser):
        """Test loop with arithmetic expressions."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    for i in [1..3] {
                        server "web${i}" {
                            address: "10.0.1.${10 + i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Check arithmetic in addresses
        backend = ir.backends[0]
        assert backend.servers[0].address == "10.0.1.11"
        assert backend.servers[1].address == "10.0.1.12"
        assert backend.servers[2].address == "10.0.1.13"

    def test_loop_with_template_spread(self, parser):
        """Test loop with template spread."""
        source = """
        config test {
            template defaults {
                check: true
                inter: 3s
                rise: 5
            }

            backend servers {
                balance: roundrobin
                servers {
                    for i in [1..2] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                            @defaults
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # All servers should have template spreads metadata
        backend = ir.backends[0]
        assert len(backend.servers) == 2
        for server in backend.servers:
            assert "template_spreads" in server.metadata
            assert server.metadata["template_spreads"] == ["defaults"]

    def test_loop_with_mixed_servers(self, parser):
        """Test loop alongside regular server definitions."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server static1 {
                        address: "10.0.0.1"
                        port: 8080
                    }

                    for i in [1..2] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }

                    server static2 {
                        address: "10.0.0.2"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Should have 4 servers total
        # Note: Current implementation appends loop-expanded servers after static servers
        backend = ir.backends[0]
        assert len(backend.servers) == 4
        server_names = {s.name for s in backend.servers}
        assert server_names == {"static1", "static2", "web1", "web2"}
        # Verify static servers are present
        static_servers = [s for s in backend.servers if s.name.startswith("static")]
        assert len(static_servers) == 2
        # Verify loop-generated servers are present
        web_servers = [s for s in backend.servers if s.name.startswith("web")]
        assert len(web_servers) == 2

    def test_loop_range_inclusive(self, parser):
        """Test that range is inclusive on both ends."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    for i in [5..7] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Should generate 3 servers: 5, 6, 7
        backend = ir.backends[0]
        assert len(backend.servers) == 3
        assert backend.servers[0].name == "web5"
        assert backend.servers[1].name == "web6"
        assert backend.servers[2].name == "web7"

    def test_multiple_loops_in_backend(self, parser):
        """Test multiple for loops in the same backend."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    for i in [1..2] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }

                    for i in [1..2] {
                        server "api${i}" {
                            address: "10.0.2.${i}"
                            port: 8081
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Should have 4 servers total
        backend = ir.backends[0]
        assert len(backend.servers) == 4
        assert backend.servers[0].name == "web1"
        assert backend.servers[1].name == "web2"
        assert backend.servers[2].name == "api1"
        assert backend.servers[3].name == "api2"

    def test_loop_with_single_iteration(self, parser):
        """Test loop with single iteration (range of 1)."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    for i in [1..1] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Should have exactly 1 server
        backend = ir.backends[0]
        assert len(backend.servers) == 1
        assert backend.servers[0].name == "web1"

    def test_loop_preserves_server_properties(self, parser):
        """Test that loop preserves all server properties."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    for i in [1..2] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                            check: true
                            inter: 3s
                            rise: 5
                            fall: 2
                            weight: 100
                            maxconn: 500
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Check all properties are preserved
        backend = ir.backends[0]
        for server in backend.servers:
            assert server.port == 8080
            assert server.check is True
            assert server.check_interval == "3s"
            assert server.rise == 5
            assert server.fall == 2
            assert server.weight == 100
            assert server.maxconn == 500

    def test_loop_removes_metadata_after_unroll(self, parser):
        """Test that loop metadata is removed after unrolling."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    for i in [1..2] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)

        # Before unroll - should have loop metadata
        assert "server_loops" in ir.backends[0].metadata

        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # After unroll - metadata should be removed
        assert "server_loops" not in ir.backends[0].metadata

    def test_multiple_backends_with_loops(self, parser):
        """Test loop unrolling across multiple backends."""
        source = """
        config test {
            backend backend1 {
                balance: roundrobin
                servers {
                    for i in [1..2] {
                        server "web${i}" {
                            address: "10.0.1.${i}"
                            port: 8080
                        }
                    }
                }
            }

            backend backend2 {
                balance: leastconn
                servers {
                    for i in [1..3] {
                        server "api${i}" {
                            address: "10.0.2.${i}"
                            port: 8081
                        }
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Check both backends
        assert len(ir.backends) == 2
        assert len(ir.backends[0].servers) == 2
        assert len(ir.backends[1].servers) == 3

    def test_backend_without_loops_unchanged(self, parser):
        """Test that backends without loops are unchanged."""
        source = """
        config test {
            backend servers {
                balance: roundrobin
                servers {
                    server web1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                }
            }
        }
        """
        ir = parser.parse(source)
        original_server = ir.backends[0].servers[0]

        unroller = LoopUnroller(ir)
        ir = unroller.unroll()

        # Server should be unchanged
        assert len(ir.backends[0].servers) == 1
        assert ir.backends[0].servers[0].name == original_server.name
        assert ir.backends[0].servers[0].address == original_server.address


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
