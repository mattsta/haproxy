"""Tests for HTTP/TCP content filtering (filter directive)."""

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.parsers import DSLParser


class TestCompressionFilter:
    """Test compression filter."""

    def test_compression_filter_frontend(self):
        """Test compression filter in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                filters: [
                    { type: "compression" }
                ]

                default_backend: app
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

        assert len(ir.frontends[0].filters) == 1
        assert ir.frontends[0].filters[0].filter_type == "compression"
        assert "filter compression" in output


class TestSpoeFilter:
    """Test SPOE (Stream Processing Offload Engine) filter."""

    def test_spoe_filter_backend(self):
        """Test SPOE filter in backend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }

            backend app {
                filters: [
                    { type: "spoe", engine: "my_agent", config: "/etc/haproxy/spoe.conf" }
                ]

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

        assert len(ir.backends[0].filters) == 1
        assert ir.backends[0].filters[0].filter_type == "spoe"
        assert ir.backends[0].filters[0].engine == "my_agent"
        assert ir.backends[0].filters[0].config == "/etc/haproxy/spoe.conf"
        assert "filter spoe engine my_agent config /etc/haproxy/spoe.conf" in output


class TestCacheFilter:
    """Test cache filter."""

    def test_cache_filter_frontend(self):
        """Test cache filter in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                filters: [
                    { type: "cache", name: "my_cache" }
                ]

                default_backend: app
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

        assert len(ir.frontends[0].filters) == 1
        assert ir.frontends[0].filters[0].filter_type == "cache"
        assert ir.frontends[0].filters[0].name == "my_cache"
        assert "filter cache my_cache" in output


class TestTraceFilter:
    """Test trace filter."""

    def test_trace_filter_frontend(self):
        """Test trace filter in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                filters: [
                    { type: "trace", name: "REQUEST_TRACE" }
                ]

                default_backend: app
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

        assert len(ir.frontends[0].filters) == 1
        assert ir.frontends[0].filters[0].filter_type == "trace"
        assert ir.frontends[0].filters[0].name == "REQUEST_TRACE"
        assert "filter trace name REQUEST_TRACE" in output


class TestBandwidthLimitFilter:
    """Test bandwidth limit filters."""

    def test_bwlim_in_filter(self):
        """Test bwlim-in filter."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                filters: [
                    {
                        type: "bwlim-in",
                        name: "bw_in",
                        default_limit: "1m",
                        default_period: "10s",
                        key: "src",
                        table: "stick_table"
                    }
                ]

                default_backend: app
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

        assert len(ir.frontends[0].filters) == 1
        filter_obj = ir.frontends[0].filters[0]
        assert filter_obj.filter_type == "bwlim-in"
        assert filter_obj.name == "bw_in"
        assert filter_obj.default_limit == "1m"
        assert filter_obj.default_period == "10s"
        assert filter_obj.key == "src"
        assert filter_obj.table == "stick_table"
        assert "filter bwlim-in bw_in default-limit 1m default-period 10s key src table stick_table" in output

    def test_bwlim_out_filter(self):
        """Test bwlim-out filter."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http
                default_backend: app
            }

            backend app {
                filters: [
                    {
                        type: "bwlim-out",
                        name: "bw_out",
                        limit: "500k",
                        period: "1s"
                    }
                ]

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

        assert len(ir.backends[0].filters) == 1
        filter_obj = ir.backends[0].filters[0]
        assert filter_obj.filter_type == "bwlim-out"
        assert filter_obj.name == "bw_out"
        assert filter_obj.limit == "500k"
        assert filter_obj.period == "1s"
        assert "filter bwlim-out bw_out limit 500k period 1s" in output


class TestMultipleFilters:
    """Test multiple filters in single config."""

    def test_multiple_filters_frontend(self):
        """Test multiple filters in frontend."""
        config = """
        config test {
            frontend web {
                bind *:80
                mode: http

                filters: [
                    { type: "compression" },
                    { type: "cache", name: "my_cache" },
                    { type: "trace", name: "REQUEST_TRACE" }
                ]

                default_backend: app
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

        assert len(ir.frontends[0].filters) == 3
        assert ir.frontends[0].filters[0].filter_type == "compression"
        assert ir.frontends[0].filters[1].filter_type == "cache"
        assert ir.frontends[0].filters[2].filter_type == "trace"
        assert "filter compression" in output
        assert "filter cache my_cache" in output
        assert "filter trace name REQUEST_TRACE" in output


class TestFiltersInListen:
    """Test filters in listen section."""

    def test_filters_in_listen(self):
        """Test filters in listen section."""
        config = """
        config test {
            listen web {
                bind *:80
                mode: http

                filters: [
                    { type: "compression" },
                    { type: "cache", name: "my_cache" }
                ]

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

        assert len(ir.listens[0].filters) == 2
        assert ir.listens[0].filters[0].filter_type == "compression"
        assert ir.listens[0].filters[1].filter_type == "cache"
        assert "filter compression" in output
        assert "filter cache my_cache" in output


class TestProductionExample:
    """Test production-like example with multiple filter types."""

    def test_production_filters(self):
        """Test production configuration with multiple filter types."""
        config = """
        config production {
            frontend api {
                bind *:443
                mode: http

                filters: [
                    { type: "compression" },
                    { type: "cache", name: "api_cache" },
                    { type: "trace", name: "API_TRACE" },
                    {
                        type: "bwlim-in",
                        name: "rate_limiter",
                        default_limit: "10m",
                        default_period: "60s",
                        key: "src"
                    }
                ]

                default_backend: api_servers
            }

            backend api_servers {
                filters: [
                    { type: "spoe", engine: "analytics", config: "/etc/haproxy/spoe-analytics.conf" },
                    { type: "bwlim-out", limit: "1m", period: "1s" }
                ]

                servers {
                    server api1 {
                        address: "10.0.1.10"
                        port: 8080
                    }
                    server api2 {
                        address: "10.0.1.11"
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

        # Frontend filters
        assert len(ir.frontends[0].filters) == 4
        assert ir.frontends[0].filters[0].filter_type == "compression"
        assert ir.frontends[0].filters[1].filter_type == "cache"
        assert ir.frontends[0].filters[1].name == "api_cache"
        assert ir.frontends[0].filters[2].filter_type == "trace"
        assert ir.frontends[0].filters[2].name == "API_TRACE"
        assert ir.frontends[0].filters[3].filter_type == "bwlim-in"
        assert ir.frontends[0].filters[3].default_limit == "10m"

        # Backend filters
        assert len(ir.backends[0].filters) == 2
        assert ir.backends[0].filters[0].filter_type == "spoe"
        assert ir.backends[0].filters[0].engine == "analytics"
        assert ir.backends[0].filters[1].filter_type == "bwlim-out"

        # Check output
        assert "filter compression" in output
        assert "filter cache api_cache" in output
        assert "filter trace name API_TRACE" in output
        assert "filter bwlim-in rate_limiter default-limit 10m default-period 60s key src" in output
        assert "filter spoe engine analytics config /etc/haproxy/spoe-analytics.conf" in output
        assert "filter bwlim-out limit 1m period 1s" in output
