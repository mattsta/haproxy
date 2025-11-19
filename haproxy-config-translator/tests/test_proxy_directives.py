"""Tests for proxy-level directives: redirect, errorfile, http-reuse, source."""

import pytest
from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestProxyDirectives:
    """Test proxy-level directives for frontend and backend."""

    # ===== Redirect Rules =====

    def test_redirect_location_basic(self):
        """Test basic redirect location."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                redirect location "https://example.com"
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

        assert len(ir.frontends) == 1
        assert len(ir.frontends[0].redirect_rules) == 1
        assert ir.frontends[0].redirect_rules[0].type == "location"
        assert ir.frontends[0].redirect_rules[0].target == "https://example.com"

        assert "redirect location https://example.com" in output

    def test_redirect_with_code(self):
        """Test redirect with HTTP status code."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                redirect location "https://example.com" code 301
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

        assert ir.frontends[0].redirect_rules[0].code == 301
        assert "redirect location https://example.com code 301" in output

    def test_redirect_prefix(self):
        """Test redirect prefix for path rewriting."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                redirect prefix "/new-path" code 302
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

        assert ir.frontends[0].redirect_rules[0].type == "prefix"
        assert ir.frontends[0].redirect_rules[0].target == "/new-path"
        assert "redirect prefix /new-path code 302" in output

    def test_redirect_scheme(self):
        """Test redirect scheme for HTTPS enforcement."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                redirect scheme "https" code 301
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

        assert ir.frontends[0].redirect_rules[0].type == "scheme"
        assert ir.frontends[0].redirect_rules[0].target == "https"
        assert "redirect scheme https code 301" in output

    def test_redirect_with_drop_query(self):
        """Test redirect with drop-query option."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                redirect location "https://example.com" drop-query
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

        assert "drop-query" in ir.frontends[0].redirect_rules[0].options
        assert "redirect location https://example.com drop-query" in output

    def test_redirect_in_backend(self):
        """Test redirect rule in backend section."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }

            backend app {
                redirect location "https://secure.example.com" code 302

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

        assert len(ir.backends[0].redirect_rules) == 1
        assert ir.backends[0].redirect_rules[0].target == "https://secure.example.com"
        assert "backend app" in output
        assert "redirect location https://secure.example.com code 302" in output

    # ===== Error Files =====

    def test_errorfile_basic(self):
        """Test basic errorfile directive."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                errorfile 404 "/etc/haproxy/errors/404.html"
                errorfile 500 "/etc/haproxy/errors/500.html"
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

        assert len(ir.frontends[0].error_files) == 2
        assert ir.frontends[0].error_files[0].code == 404
        assert ir.frontends[0].error_files[0].file == "/etc/haproxy/errors/404.html"
        assert ir.frontends[0].error_files[1].code == 500

        assert "errorfile 404 /etc/haproxy/errors/404.html" in output
        assert "errorfile 500 /etc/haproxy/errors/500.html" in output

    def test_errorfile_in_backend(self):
        """Test errorfile directive in backend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }

            backend app {
                errorfile 503 "/etc/haproxy/errors/503.html"

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

        assert len(ir.backends[0].error_files) == 1
        assert ir.backends[0].error_files[0].code == 503
        assert "backend app" in output
        assert "errorfile 503 /etc/haproxy/errors/503.html" in output

    # ===== HTTP Reuse =====

    def test_http_reuse_never(self):
        """Test http-reuse never mode."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }

            backend app {
                http-reuse: never

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

        assert ir.backends[0].http_reuse == "never"
        assert "http-reuse never" in output

    def test_http_reuse_safe(self):
        """Test http-reuse safe mode."""
        config = """
        config test {
            backend app {
                http-reuse: safe

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

        assert ir.backends[0].http_reuse == "safe"
        assert "http-reuse safe" in output

    def test_http_reuse_aggressive(self):
        """Test http-reuse aggressive mode."""
        config = """
        config test {
            backend app {
                http-reuse: aggressive

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

        assert ir.backends[0].http_reuse == "aggressive"
        assert "http-reuse aggressive" in output

    def test_http_reuse_always(self):
        """Test http-reuse always mode."""
        config = """
        config test {
            backend app {
                http-reuse: always

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

        assert ir.backends[0].http_reuse == "always"
        assert "http-reuse always" in output

    # ===== Source Directive =====

    def test_source_basic(self):
        """Test source directive for backend."""
        config = """
        config test {
            backend app {
                source: "10.0.0.1:0"

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

        assert ir.backends[0].source == "10.0.0.1:0"
        assert "source 10.0.0.1:0" in output

    def test_source_with_port_range(self):
        """Test source with port range."""
        config = """
        config test {
            backend app {
                source: "192.168.1.1:1024-65535"

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

        assert ir.backends[0].source == "192.168.1.1:1024-65535"
        assert "source 192.168.1.1:1024-65535" in output

    # ===== Integration Tests =====

    def test_all_proxy_directives_together(self):
        """Test all new proxy directives in one configuration."""
        config = """
        config production {
            frontend web {
                bind *:80
                bind *:443
                mode: http

                // Error pages
                errorfile 400 "/etc/haproxy/errors/400.html"
                errorfile 404 "/etc/haproxy/errors/404.html"
                errorfile 500 "/etc/haproxy/errors/500.html"

                // HTTPS redirect
                redirect scheme "https" code 301

                default_backend: app
            }

            backend app {
                mode: http

                // Connection pooling
                http-reuse: safe

                // Source IP binding
                source: "10.0.0.1:0"

                // Backend error page
                errorfile 503 "/etc/haproxy/errors/503.html"

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

        # Verify IR
        assert len(ir.frontends[0].error_files) == 3
        assert len(ir.frontends[0].redirect_rules) == 1
        assert len(ir.backends[0].error_files) == 1
        assert ir.backends[0].http_reuse == "safe"
        assert ir.backends[0].source == "10.0.0.1:0"

        # Verify generated config
        assert "errorfile 400 /etc/haproxy/errors/400.html" in output
        assert "errorfile 404 /etc/haproxy/errors/404.html" in output
        assert "redirect scheme https code 301" in output
        assert "http-reuse safe" in output
        assert "source 10.0.0.1:0" in output
        assert "errorfile 503 /etc/haproxy/errors/503.html" in output
