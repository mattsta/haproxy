"""Tests for hash-preserve-affinity directive (Phase 5B)."""

from haproxy_translator.parsers import DSLParser


class TestHashPreserveAffinity:
    """Test hash-preserve-affinity directive."""

    def test_hash_preserve_affinity_always(self):
        """Test hash-preserve-affinity with always mode."""
        config = """
        config test {
            backend app {
                balance: uri
                hash-type: consistent
                hash-preserve-affinity: always
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert ir.backends[0].hash_preserve_affinity == "always"

    def test_hash_preserve_affinity_maxconn(self):
        """Test hash-preserve-affinity with maxconn mode."""
        config = """
        config test {
            backend app {
                balance: uri
                hash-preserve-affinity: maxconn
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].hash_preserve_affinity == "maxconn"

    def test_hash_preserve_affinity_maxqueue(self):
        """Test hash-preserve-affinity with maxqueue mode."""
        config = """
        config test {
            backend app {
                balance: uri
                hash-preserve-affinity: maxqueue
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert ir.backends[0].hash_preserve_affinity == "maxqueue"

    def test_hash_preserve_with_hash_type_and_balance_factor(self):
        """Test hash-preserve-affinity combined with other hash directives."""
        config = """
        config test {
            backend app {
                balance: uri
                hash-type: consistent
                hash-balance-factor: 150
                hash-preserve-affinity: always
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                    server app2 { address: "10.0.1.2" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        backend = ir.backends[0]

        # All hash directives should be present
        assert backend.hash_type == "consistent"
        assert backend.hash_balance_factor == 150
        assert backend.hash_preserve_affinity == "always"
