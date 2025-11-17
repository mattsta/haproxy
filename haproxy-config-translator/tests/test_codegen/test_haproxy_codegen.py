"""Tests for HAProxy code generator."""

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.ir.nodes import (
    ACL,
    Backend,
    BalanceAlgorithm,
    Bind,
    ConfigIR,
    DefaultsConfig,
    Frontend,
    GlobalConfig,
    HealthCheck,
    HttpRequestRule,
    Mode,
    Server,
    ServerTemplate,
)


class TestHAProxyCodeGenerator:
    """Test HAProxy code generator."""

    @pytest.fixture
    def codegen(self):
        """Create code generator."""
        return HAProxyCodeGenerator()

    def test_minimal_config(self, codegen):
        """Test generation of minimal configuration."""
        ir = ConfigIR(
            name="minimal",
            version="2.0",
        )

        output = codegen.generate(ir)

        assert "# Generated HAProxy configuration: minimal" in output
        assert "# Version: 2.0" in output

    def test_global_section(self, codegen):
        """Test generation of global section."""
        ir = ConfigIR(
            name="test",
            global_config=GlobalConfig(
                daemon=True,
                maxconn=10000,
                user="haproxy",
                group="haproxy",
            ),
        )

        output = codegen.generate(ir)

        assert "global" in output
        assert "daemon" in output
        assert "maxconn 10000" in output
        assert "user haproxy" in output
        assert "group haproxy" in output

    def test_defaults_section(self, codegen):
        """Test generation of defaults section."""
        ir = ConfigIR(
            name="test",
            defaults=DefaultsConfig(
                mode=Mode.HTTP,
                retries=3,
                timeout_connect="5s",
                timeout_client="50s",
                timeout_server="50s",
                log="global",
                options=["httplog", "dontlognull"],
            ),
        )

        output = codegen.generate(ir)

        assert "defaults" in output
        assert "mode http" in output
        assert "retries 3" in output
        assert "timeout connect 5s" in output
        assert "timeout client 50s" in output
        assert "timeout server 50s" in output
        assert "log global" in output
        assert "option httplog" in output
        assert "option dontlognull" in output

    def test_frontend_basic(self, codegen):
        """Test generation of basic frontend."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(
                    name="web",
                    binds=[Bind(address="*:80")],
                    mode=Mode.HTTP,
                    default_backend="servers",
                )
            ],
        )

        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "bind *:80" in output
        assert "mode http" in output
        assert "default_backend servers" in output

    def test_frontend_with_acl(self, codegen):
        """Test generation of frontend with ACL."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(
                    name="web",
                    binds=[Bind(address="*:80")],
                    acls=[
                        ACL(name="is_api", criterion="path_beg", values=["/api"])
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "acl is_api path_beg /api" in output

    def test_frontend_with_http_request_rules(self, codegen):
        """Test generation of frontend with HTTP request rules."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(
                    name="web",
                    binds=[Bind(address="*:80")],
                    http_request_rules=[
                        HttpRequestRule(
                            action="deny",
                            parameters={"status": "403"},
                            condition="is_blocked",
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "http-request deny" in output

    def test_backend_basic(self, codegen):
        """Test generation of basic backend."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    balance=BalanceAlgorithm.ROUNDROBIN,
                    mode=Mode.HTTP,
                )
            ],
        )

        output = codegen.generate(ir)

        assert "backend servers" in output
        assert "balance roundrobin" in output
        assert "mode http" in output

    def test_backend_with_servers(self, codegen):
        """Test generation of backend with servers."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    balance=BalanceAlgorithm.ROUNDROBIN,
                    servers=[
                        Server(
                            name="web1",
                            address="10.0.1.1",
                            port=8080,
                            check=True,
                            check_interval="3s",
                            rise=5,
                            fall=2,
                        ),
                        Server(
                            name="web2",
                            address="10.0.1.2",
                            port=8080,
                            check=True,
                        ),
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "backend servers" in output
        assert "server web1 10.0.1.1:8080 check inter 3s rise 5 fall 2" in output
        assert "server web2 10.0.1.2:8080 check" in output

    def test_backend_with_health_check(self, codegen):
        """Test generation of backend with health check."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    balance=BalanceAlgorithm.ROUNDROBIN,
                    health_check=HealthCheck(
                        method="GET",
                        uri="/health",
                        expect_status=200,
                    ),
                )
            ],
        )

        output = codegen.generate(ir)

        assert "backend servers" in output
        # HAProxy 2.0+ uses http-check syntax
        assert "http-check send meth GET uri /health" in output
        assert "http-check expect status 200" in output

    def test_backend_with_options(self, codegen):
        """Test generation of backend with options."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    balance=BalanceAlgorithm.ROUNDROBIN,
                    options=["httpchk", "forwardfor", "http-server-close"],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "backend servers" in output
        assert "option httpchk" in output
        assert "option forwardfor" in output
        assert "option http-server-close" in output

    def test_server_with_ssl(self, codegen):
        """Test generation of server with SSL."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    servers=[
                        Server(
                            name="web1",
                            address="10.0.1.1",
                            port=443,
                            ssl=True,
                            ssl_verify="none",
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "server web1 10.0.1.1:443 ssl verify none" in output

    def test_server_with_backup(self, codegen):
        """Test generation of backup server."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    servers=[
                        Server(
                            name="web1",
                            address="10.0.1.1",
                            port=8080,
                        ),
                        Server(
                            name="backup1",
                            address="10.0.2.1",
                            port=8080,
                            backup=True,
                        ),
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "server web1 10.0.1.1:8080" in output
        assert "server backup1 10.0.2.1:8080 backup" in output

    def test_server_with_weight(self, codegen):
        """Test generation of server with weight."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    servers=[
                        Server(
                            name="web1",
                            address="10.0.1.1",
                            port=8080,
                            weight=100,
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "server web1 10.0.1.1:8080 weight 100" in output

    def test_server_with_maxconn(self, codegen):
        """Test generation of server with maxconn."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    servers=[
                        Server(
                            name="web1",
                            address="10.0.1.1",
                            port=8080,
                            maxconn=500,
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "server web1 10.0.1.1:8080 maxconn 500" in output

    def test_server_template(self, codegen):
        """Test generation of server-template."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    server_templates=[
                        ServerTemplate(
                            prefix="web",
                            count=5,
                            fqdn_pattern="web-{id}.internal.example.com",
                            port=8080,
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "backend servers" in output
        assert "server-template web" in output
        assert "web-{id}.internal.example.com:8080" in output

    def test_multiple_frontends_and_backends(self, codegen):
        """Test generation with multiple frontends and backends."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(name="web", binds=[Bind(address="*:80")]),
                Frontend(name="api", binds=[Bind(address="*:8080")]),
            ],
            backends=[
                Backend(name="web_servers", balance=BalanceAlgorithm.ROUNDROBIN),
                Backend(name="api_servers", balance=BalanceAlgorithm.LEASTCONN),
            ],
        )

        output = codegen.generate(ir)

        assert "frontend web" in output
        assert "frontend api" in output
        assert "backend web_servers" in output
        assert "backend api_servers" in output

    def test_tcp_mode(self, codegen):
        """Test generation in TCP mode."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(
                    name="tcp_front",
                    binds=[Bind(address="*:3306")],
                    mode=Mode.TCP,
                )
            ],
            backends=[
                Backend(
                    name="mysql",
                    mode=Mode.TCP,
                    balance=BalanceAlgorithm.LEASTCONN,
                )
            ],
        )

        output = codegen.generate(ir)

        assert "frontend tcp_front" in output
        assert "mode tcp" in output
        assert "backend mysql" in output

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
