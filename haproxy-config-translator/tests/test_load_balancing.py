"""Tests for advanced load balancing features (Phase 4A)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHashType:
    """Test hash-type directive for hash-based load balancing."""

    def test_hash_type_map_based(self):
        """Test hash-type with map-based method."""
        config = """
        config test {
            backend app {
                balance: source
                hash-type: map-based

                servers {
                    server srv1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                    server srv2 {
                        address: "10.0.1.2"
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

        assert ir.backends[0].hash_type == "map-based"
        assert "hash-type map-based" in output

    def test_hash_type_consistent(self):
        """Test hash-type with consistent method."""
        config = """
        config test {
            backend app {
                balance: source
                hash-type: consistent

                servers {
                    server srv1 {
                        address: "10.0.1.1"
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

        assert ir.backends[0].hash_type == "consistent"
        assert "hash-type consistent" in output

    def test_hash_type_with_function(self):
        """Test hash-type with method and function."""
        config = """
        config test {
            backend app {
                balance: uri
                hash-type: map-based sdbm

                servers {
                    server srv1 {
                        address: "10.0.1.1"
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

        assert ir.backends[0].hash_type == "map-based sdbm"
        assert "hash-type map-based sdbm" in output

    def test_hash_type_with_function_and_modifier(self):
        """Test hash-type with method, function, and modifier."""
        config = """
        config test {
            backend app {
                balance: uri
                hash-type: consistent djb2 avalanche

                servers {
                    server srv1 {
                        address: "10.0.1.1"
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

        assert ir.backends[0].hash_type == "consistent djb2 avalanche"
        assert "hash-type consistent djb2 avalanche" in output

    def test_hash_type_all_functions(self):
        """Test all supported hash functions."""
        functions = ["sdbm", "djb2", "wt6", "crc32"]

        for func in functions:
            config = f"""
            config test {{
                backend app {{
                    balance: uri
                    hash-type: map-based {func}

                    servers {{
                        server srv1 {{
                            address: "10.0.1.1"
                            port: 8080
                        }}
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            codegen = HAProxyCodeGenerator()
            output = codegen.generate(ir)

            assert ir.backends[0].hash_type == f"map-based {func}"
            assert f"hash-type map-based {func}" in output


class TestHashBalanceFactor:
    """Test hash-balance-factor directive."""

    def test_hash_balance_factor_basic(self):
        """Test basic hash-balance-factor."""
        config = """
        config test {
            backend app {
                balance: uri
                hash-balance-factor: 150

                servers {
                    server srv1 {
                        address: "10.0.1.1"
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

        assert ir.backends[0].hash_balance_factor == 150
        assert "hash-balance-factor 150" in output

    def test_hash_balance_factor_large_value(self):
        """Test hash-balance-factor with large value."""
        config = """
        config test {
            backend app {
                balance: source
                hash-balance-factor: 65535

                servers {
                    server srv1 {
                        address: "10.0.1.1"
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

        assert ir.backends[0].hash_balance_factor == 65535
        assert "hash-balance-factor 65535" in output


class TestLoadBalancingIntegration:
    """Test hash-type and hash-balance-factor together."""

    def test_hash_type_and_balance_factor_together(self):
        """Test using both hash-type and hash-balance-factor."""
        config = """
        config production {
            backend api {
                balance: uri
                hash-type: consistent djb2 avalanche
                hash-balance-factor: 200

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                    }
                    server api3 {
                        address: "10.0.1.3"
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

        # Verify IR
        assert ir.backends[0].hash_type == "consistent djb2 avalanche"
        assert ir.backends[0].hash_balance_factor == 200

        # Verify output
        assert "hash-type consistent djb2 avalanche" in output
        assert "hash-balance-factor 200" in output

    def test_production_config_with_hash_balancing(self):
        """Test production-like configuration with advanced hash balancing."""
        config = """
        config production {
            frontend web {
                bind *:80
                mode: http

                acl {
                    url_api path_beg "/api"
                }

                route {
                    to api_backend if url_api
                    default: static_backend
                }
            }

            backend api_backend {
                mode: http
                balance: uri
                hash-type: consistent djb2 avalanche
                hash-balance-factor: 150

                option: ["httplog", "forwardfor"]

                servers {
                    server api1 {
                        address: "10.0.1.1"
                        port: 8080
                        check: true
                    }
                    server api2 {
                        address: "10.0.1.2"
                        port: 8080
                        check: true
                    }
                    server api3 {
                        address: "10.0.1.3"
                        port: 8080
                        check: true
                    }
                }
            }

            backend static_backend {
                mode: http
                balance: source
                hash-type: map-based sdbm

                servers {
                    server static1 {
                        address: "10.0.2.1"
                        port: 8080
                    }
                    server static2 {
                        address: "10.0.2.2"
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

        # Verify IR for api_backend
        assert ir.backends[0].name == "api_backend"
        assert ir.backends[0].hash_type == "consistent djb2 avalanche"
        assert ir.backends[0].hash_balance_factor == 150

        # Verify IR for static_backend
        assert ir.backends[1].name == "static_backend"
        assert ir.backends[1].hash_type == "map-based sdbm"

        # Verify output
        assert "backend api_backend" in output
        assert "hash-type consistent djb2 avalanche" in output
        assert "hash-balance-factor 150" in output
        assert "backend static_backend" in output
        assert "hash-type map-based sdbm" in output
