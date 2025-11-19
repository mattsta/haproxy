"""Tests for declare capture directive (capture slot declarations)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestDeclareCaptureParsing:
    """Test declare capture directive parsing."""

    def test_frontend_declare_capture_request(self):
        """Test frontend declare capture with request type."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture request len 64
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends) == 1
        assert len(ir.frontends[0].declare_captures) == 1
        capture = ir.frontends[0].declare_captures[0]
        assert capture.capture_type == "request"
        assert capture.length == 64

    def test_frontend_declare_capture_response(self):
        """Test frontend declare capture with response type."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture response len 128
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].declare_captures) == 1
        capture = ir.frontends[0].declare_captures[0]
        assert capture.capture_type == "response"
        assert capture.length == 128

    def test_backend_declare_capture(self):
        """Test backend declare capture directive."""
        config = """
        config test {
            backend app {
                mode: http
                declare capture request len 32
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.backends) == 1
        assert len(ir.backends[0].declare_captures) == 1
        capture = ir.backends[0].declare_captures[0]
        assert capture.capture_type == "request"
        assert capture.length == 32

    def test_listen_declare_capture(self):
        """Test listen declare capture directive."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                balance: roundrobin
                declare capture request len 256
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.listens) == 1
        assert len(ir.listens[0].declare_captures) == 1
        capture = ir.listens[0].declare_captures[0]
        assert capture.capture_type == "request"
        assert capture.length == 256

    def test_multiple_declare_captures(self):
        """Test multiple declare capture directives in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture request len 64
                declare capture response len 128
                declare capture request len 32
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        assert len(ir.frontends[0].declare_captures) == 3
        assert ir.frontends[0].declare_captures[0].capture_type == "request"
        assert ir.frontends[0].declare_captures[0].length == 64
        assert ir.frontends[0].declare_captures[1].capture_type == "response"
        assert ir.frontends[0].declare_captures[1].length == 128
        assert ir.frontends[0].declare_captures[2].capture_type == "request"
        assert ir.frontends[0].declare_captures[2].length == 32


class TestDeclareCaptureCodegen:
    """Test declare capture code generation."""

    def test_frontend_declare_capture_request_codegen(self):
        """Test frontend declare capture request code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture request len 64
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "declare capture request len 64" in output

    def test_frontend_declare_capture_response_codegen(self):
        """Test frontend declare capture response code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture response len 128
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "declare capture response len 128" in output

    def test_backend_declare_capture_codegen(self):
        """Test backend declare capture code generation."""
        config = """
        config test {
            backend app {
                mode: http
                declare capture request len 32
                servers {
                    server s1 { address: "10.0.1.1" port: 8080 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "backend app" in output
        assert "declare capture request len 32" in output

    def test_listen_declare_capture_codegen(self):
        """Test listen declare capture code generation."""
        config = """
        config test {
            listen stats {
                bind *:9000
                mode: http
                declare capture request len 256
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "listen stats" in output
        assert "declare capture request len 256" in output

    def test_multiple_declare_captures_codegen(self):
        """Test multiple declare capture directives code generation."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture request len 64
                declare capture response len 128
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "declare capture request len 64" in output
        assert "declare capture response len 128" in output


class TestDeclareCaptureIntegration:
    """Integration tests for declare capture directive."""

    def test_declare_capture_with_other_directives(self):
        """Test declare capture alongside other frontend directives."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                option: "httplog"
                declare capture request len 64
                declare capture response len 128
                default_backend: app
            }

            backend app {
                mode: http
                declare capture request len 32
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 check: true }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "declare capture request len 64" in output
        assert "declare capture response len 128" in output
        assert "backend app" in output
        assert "declare capture request len 32" in output

    def test_declare_capture_various_lengths(self):
        """Test declare capture with various length values."""
        lengths = [8, 16, 32, 64, 128, 256, 512, 1024]

        for length in lengths:
            config = f"""
            config test {{
                frontend web {{
                    bind *:80
                    mode: http
                    declare capture request len {length}
                }}
            }}
            """
            parser = DSLParser()
            ir = parser.parse(config)
            assert ir.frontends[0].declare_captures[0].length == length

    def test_multiple_proxies_with_declare_capture(self):
        """Test multiple proxies with declare capture configuration."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture request len 64
                declare capture response len 64
                default_backend: app
            }

            backend app {
                mode: http
                declare capture request len 32
                servers {
                    server app1 { address: "10.0.1.1" port: 8080 }
                }
            }

            listen stats {
                bind *:9000
                mode: http
                declare capture request len 128
                servers {
                    server s1 { address: "127.0.0.1" port: 9001 }
                }
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "frontend web" in output
        assert len(ir.frontends[0].declare_captures) == 2
        assert len(ir.backends[0].declare_captures) == 1
        assert len(ir.listens[0].declare_captures) == 1

    def test_declare_capture_request_and_response(self):
        """Test declare capture with both request and response types."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                declare capture request len 100
                declare capture response len 200
                declare capture request len 50
            }
        }
        """
        parser = DSLParser()
        ir = parser.parse(config)
        codegen = HAProxyCodeGenerator()
        output = codegen.generate(ir)

        assert "declare capture request len 100" in output
        assert "declare capture response len 200" in output
        assert "declare capture request len 50" in output

        # Verify parsing
        captures = ir.frontends[0].declare_captures
        assert len(captures) == 3
        assert captures[0].capture_type == "request"
        assert captures[0].length == 100
        assert captures[1].capture_type == "response"
        assert captures[1].length == 200
        assert captures[2].capture_type == "request"
        assert captures[2].length == 50
