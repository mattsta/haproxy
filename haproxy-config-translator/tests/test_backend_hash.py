"""Tests for backend hash directives (hash-type, hash-balance-factor)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestHashType:
    """Test hash-type directive."""

    def test_backend_hash_type_map_based(self):
        """Test backend hash-type with 'map-based' algorithm."""
        config = """
        config test {
            backend app {
                mode: http
                balance: uri
                hash-type: map-based
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].hash_type == "map-based"

    def test_backend_hash_type_consistent(self):
        """Test backend hash-type with 'consistent' algorithm."""
        config = """
        config test {
            backend app {
                mode: http
                balance: uri
                hash-type: consistent
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].hash_type == "consistent"

    def test_backend_hash_type_codegen(self):
        """Test backend hash-type code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: uri
                hash-type: consistent
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "hash-type consistent" in output
        assert "backend app" in output
        assert "balance uri" in output

    def test_backend_without_hash_type(self):
        """Test backend without hash-type (should be None)."""
        config = """
        config test {
            backend app {
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].hash_type is None


class TestHashBalanceFactor:
    """Test hash-balance-factor directive."""

    def test_backend_hash_balance_factor(self):
        """Test backend hash-balance-factor directive."""
        config = """
        config test {
            backend app {
                mode: http
                balance: uri
                hash-type: consistent
                hash-balance-factor: 150
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].hash_balance_factor == 150

    def test_backend_hash_balance_factor_codegen(self):
        """Test backend hash-balance-factor code generation."""
        config = """
        config test {
            backend app {
                mode: http
                balance: uri
                hash-type: consistent
                hash-balance-factor: 200
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "hash-balance-factor 200" in output
        assert "hash-type consistent" in output
        assert "backend app" in output

    def test_backend_without_hash_balance_factor(self):
        """Test backend without hash-balance-factor (should be None)."""
        config = """
        config test {
            backend app {
                mode: http
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].hash_balance_factor is None

    def test_hash_balance_factor_range(self):
        """Test hash-balance-factor with different values in valid range."""
        values = [100, 150, 200, 500, 1000, 10000, 65535]

        for value in values:
            config = f"""
            config test {{
                backend app {{
                    mode: http
                    balance: uri
                    hash-type: consistent
                    hash-balance-factor: {value}
                    servers {{
                        server s1 {{ address: "10.0.1.1" port: 8080 }}
                    }}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.backends[0].hash_balance_factor == value


class TestHashIntegration:
    """Integration tests for hash directives."""

    def test_hash_type_and_balance_factor_together(self):
        """Test hash-type and hash-balance-factor used together."""
        config = """
        config test {
            backend app {
                mode: http
                balance: uri
                hash-type: consistent
                hash-balance-factor: 150
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].hash_type == "consistent"
        assert ir.backends[0].hash_balance_factor == 150

    def test_hash_with_uri_balance_algorithm(self):
        """Test hash directives with URI balance algorithm."""
        config = """
        config test {
            backend api {
                mode: http
                balance: uri
                hash-type: consistent
                hash-balance-factor: 200
                servers {
                    server api1 { address: "192.168.1.10" port: 8080 }
                    server api2 { address: "192.168.1.11" port: 8080 }
                    server api3 { address: "192.168.1.12" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend api" in output
        assert "mode http" in output
        assert "balance uri" in output
        assert "hash-type consistent" in output
        assert "hash-balance-factor 200" in output

    def test_multiple_backends_different_hash_configs(self):
        """Test multiple backends with different hash configurations."""
        config = """
        config test {
            backend web {
                mode: http
                balance: uri
                hash-type: map-based
                servers {
                    server web1 { address: "10.0.1.1" port: 80 }
                }
            }

            backend api {
                mode: http
                balance: uri
                hash-type: consistent
                hash-balance-factor: 150
                servers {
                    server api1 { address: "10.0.2.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert len(ir.backends) == 2
        assert ir.backends[0].hash_type == "map-based"
        assert ir.backends[0].hash_balance_factor is None
        assert ir.backends[1].hash_type == "consistent"
        assert ir.backends[1].hash_balance_factor == 150

    def test_hash_with_source_balance(self):
        """Test hash directives with source balance algorithm."""
        config = """
        config test {
            backend app {
                mode: http
                balance: source
                hash-type: consistent
                hash-balance-factor: 100
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)

        assert ir.backends[0].balance.value == "source"
        assert ir.backends[0].hash_type == "consistent"
        assert ir.backends[0].hash_balance_factor == 100

    def test_hash_complete_codegen(self):
        """Test complete configuration with hash directives."""
        config = """
        config test {
            backend cdn {
                mode: http
                balance: uri
                hash-type: consistent
                hash-balance-factor: 150
                option: "httpchk"
                http-reuse: safe
                servers {
                    server cdn1 { address: "192.168.1.10" port: 8080 check: true }
                    server cdn2 { address: "192.168.1.11" port: 8080 check: true }
                    server cdn3 { address: "192.168.1.12" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend cdn" in output
        assert "balance uri" in output
        assert "hash-type consistent" in output
        assert "hash-balance-factor 150" in output
        assert "option httpchk" in output
        assert "http-reuse safe" in output
        assert "server cdn1 192.168.1.10:8080 check" in output
        assert "server cdn2 192.168.1.11:8080 check" in output
        assert "server cdn3 192.168.1.12:8080 check" in output

    def test_map_based_hash_type(self):
        """Test map-based hash type configuration."""
        config = """
        config test {
            backend app {
                mode: http
                balance: source
                hash-type: map-based
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "balance source" in output
        assert "hash-type map-based" in output
