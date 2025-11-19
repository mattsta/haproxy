"""Tests for HAProxy code generator."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator
from haproxy_translator.ir.nodes import (
    ACL,
    Backend,
    BalanceAlgorithm,
    Bind,
    CompressionConfig,
    ConfigIR,
    DefaultsConfig,
    Frontend,
    GlobalConfig,
    HealthCheck,
    HttpRequestRule,
    HttpResponseRule,
    Listen,
    LogFacility,
    LogLevel,
    LogTarget,
    LuaScript,
    Mode,
    Server,
    ServerTemplate,
    StatsConfig,
    StatsSocket,
    UseBackendRule,
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
                    acls=[ACL(name="is_api", criterion="path_beg", values=["/api"])],
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

    def test_server_with_sni_and_alpn(self, codegen):
        """Test generation of server with SNI and ALPN."""
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
                            sni="example.com",
                            alpn=["h2", "http/1.1"],
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "server web1 10.0.1.1:443 ssl verify none sni example.com alpn h2,http/1.1" in output

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

    def test_global_with_all_options(self, codegen):
        """Test global section with all options."""
        ir = ConfigIR(
            name="test",
            global_config=GlobalConfig(
                daemon=True,
                maxconn=10000,
                user="haproxy",
                group="haproxy",
                chroot="/var/lib/haproxy",
                pidfile="/var/run/haproxy.pid",
                log_targets=[
                    LogTarget(
                        address="/dev/log",
                        facility=LogFacility.LOCAL0,
                        level=LogLevel.INFO,
                        minlevel=LogLevel.WARNING,
                    )
                ],
                ssl_default_bind_ciphers="ECDHE-RSA-AES128-GCM-SHA256",
                ssl_default_bind_options=["no-sslv3", "no-tlsv10"],
                lua_scripts=[
                    LuaScript(
                        name="auth",
                        source_type="file",
                        content="/etc/haproxy/lua/auth.lua",
                    )
                ],
                stats=StatsConfig(enable=True),
                stats_sockets=[
                    StatsSocket(
                        path="/var/run/haproxy.sock",
                        level="admin",
                        mode="660",
                    )
                ],
                tuning={"tune.ssl.default-dh-param": "2048", "maxconnrate": "100"},
            ),
        )

        output = codegen.generate(ir)

        assert "chroot /var/lib/haproxy" in output
        assert "pidfile /var/run/haproxy.pid" in output
        assert "log /dev/log local0 info warning" in output
        assert "ssl-default-bind-ciphers ECDHE-RSA-AES128-GCM-SHA256" in output
        assert "ssl-default-bind-options no-sslv3" in output
        assert "ssl-default-bind-options no-tlsv10" in output
        assert "lua-load /etc/haproxy/lua/auth.lua" in output
        assert "stats socket /var/run/haproxy.sock level admin mode 660" in output
        assert "tune.ssl.default-dh-param 2048" in output
        assert "maxconnrate 100" in output

    def test_defaults_with_all_options(self, codegen):
        """Test defaults section with all options."""
        ir = ConfigIR(
            name="test",
            defaults=DefaultsConfig(
                mode=Mode.HTTP,
                log="global",
                retries=3,
                timeout_connect="5s",
                timeout_client="50s",
                timeout_server="50s",
                timeout_check="2s",
                timeout_queue="5s",
                options=["httplog", "dontlognull"],
                errorfiles={
                    400: "/etc/haproxy/errors/400.http",
                    500: "/etc/haproxy/errors/500.http",
                },
                http_check=HealthCheck(
                    method="GET",
                    uri="/health",
                    expect_status=200,
                ),
            ),
        )

        output = codegen.generate(ir)

        assert "timeout check 2s" in output
        assert "timeout queue 5s" in output
        assert "errorfile 400 /etc/haproxy/errors/400.http" in output
        assert "errorfile 500 /etc/haproxy/errors/500.http" in output
        assert "http-check send meth GET uri /health" in output
        assert "http-check expect status 200" in output

    def test_frontend_with_all_options(self, codegen):
        """Test frontend with all options."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(
                    name="web",
                    binds=[Bind(address="*:80")],
                    maxconn=5000,
                    timeout_client="60s",
                    acls=[ACL(name="is_api", criterion="path_beg", flags=["-i"], values=["/api"])],
                    http_request_rules=[
                        HttpRequestRule(
                            action="set-header",
                            parameters={"header": "X-Forwarded-Proto", "value": "https"},
                        )
                    ],
                    http_response_rules=[
                        HttpResponseRule(
                            action="set-header",
                            parameters={"name": "X-Frame-Options", "value": "DENY"},
                        )
                    ],
                    use_backend_rules=[
                        UseBackendRule(backend="api_servers", condition="is_api"),
                    ],
                    default_backend="web_servers",
                    options=["httplog", "forwardfor"],
                )
            ],
            backends=[
                Backend(name="api_servers", balance=BalanceAlgorithm.ROUNDROBIN),
                Backend(name="web_servers", balance=BalanceAlgorithm.ROUNDROBIN),
            ],
        )

        output = codegen.generate(ir)

        assert "maxconn 5000" in output
        assert "timeout client 60s" in output
        assert "acl is_api path_beg -i /api" in output
        assert "http-request set-header X-Forwarded-Proto value https" in output
        assert "http-response set-header" in output
        assert "use_backend api_servers if is_api" in output
        assert "option httplog" in output
        assert "option forwardfor" in output

    def test_backend_with_all_options(self, codegen):
        """Test backend with all options."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="servers",
                    balance=BalanceAlgorithm.ROUNDROBIN,
                    retries=5,
                    timeout_connect="3s",
                    timeout_server="30s",
                    timeout_check="2s",
                    cookie="SERVERID insert indirect nocache",
                    health_check=HealthCheck(
                        method="POST",
                        uri="/api/health",
                        headers={"Authorization": "Bearer token123"},
                        expect_status=None,
                        expect_string="OK",
                    ),
                    http_request_rules=[
                        HttpRequestRule(
                            action="add-header",
                            parameters={"name": "X-Backend", "value": "servers"},
                        )
                    ],
                    http_response_rules=[
                        HttpResponseRule(
                            action="del-header",
                            parameters={"name": "Server"},
                            condition="is_prod",
                        )
                    ],
                    compression=CompressionConfig(
                        algo="gzip",
                        types=["text/html", "text/plain", "application/json"],
                    ),
                    servers=[
                        Server(
                            name="web1",
                            address="10.0.1.1",
                            port=8080,
                            disabled=True,
                            send_proxy=True,
                            options={"resolvers": "dns", "init-addr": "last,libc,none"},
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "retries 5" in output
        assert "timeout connect 3s" in output
        assert "timeout server 30s" in output
        assert "timeout check 2s" in output
        assert "cookie SERVERID insert indirect nocache" in output
        assert "http-check send meth POST uri /api/health hdr Authorization" in output
        assert "http-check expect string OK" in output
        assert "http-request add-header" in output
        assert "http-response del-header name Server if is_prod" in output
        assert "compression algo gzip" in output
        assert "compression type text/html text/plain application/json" in output
        assert "disabled" in output
        assert "send-proxy" in output
        assert "resolvers dns" in output
        assert "init-addr" in output

    def test_listen_section(self, codegen):
        """Test listen section generation."""
        ir = ConfigIR(
            name="test",
            listens=[
                Listen(
                    name="stats",
                    binds=[Bind(address="*:8404")],
                    mode=Mode.HTTP,
                    balance=BalanceAlgorithm.ROUNDROBIN,
                    acls=[ACL(name="is_admin", criterion="src", values=["10.0.0.0/24"])],
                    options=["httplog"],
                    servers=[
                        Server(name="s1", address="127.0.0.1", port=8080),
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "listen stats" in output
        assert "bind *:8404" in output
        assert "mode http" in output
        assert "balance roundrobin" in output
        assert "acl is_admin src 10.0.0.0/24" in output
        assert "option httplog" in output
        assert "server s1 127.0.0.1:8080" in output

    def test_bind_with_ssl_options(self, codegen):
        """Test bind with SSL and all options."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(
                    name="https",
                    binds=[
                        Bind(
                            address="*:443",
                            ssl=True,
                            ssl_cert="/etc/ssl/certs/site.pem",
                            alpn=["h2", "http/1.1"],
                            options={"accept-proxy": True, "maxconn": "1000"},
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "bind *:443 ssl crt /etc/ssl/certs/site.pem alpn h2,http/1.1" in output
        assert "accept-proxy" in output
        assert "maxconn 1000" in output

    def test_server_template_with_base_server(self, codegen):
        """Test server-template with base server properties."""
        ir = ConfigIR(
            name="test",
            backends=[
                Backend(
                    name="scaled",
                    balance=BalanceAlgorithm.ROUNDROBIN,
                    server_templates=[
                        ServerTemplate(
                            prefix="web",
                            count=10,
                            fqdn_pattern="web-{id}.internal.example.com",
                            port=8080,
                            base_server=Server(
                                name="base",
                                address="",
                                port=8080,
                                check=True,
                                check_interval="5s",
                                rise=3,
                                fall=2,
                                weight=50,
                                maxconn=200,
                                ssl=True,
                                ssl_verify="required",
                            ),
                        )
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "server-template web 10 web-{id}.internal.example.com:8080" in output
        assert "check inter 5s rise 3 fall 2" in output
        assert "weight 50" in output
        assert "maxconn 200" in output
        assert "ssl verify required" in output

    def test_http_request_rule_with_various_parameters(self, codegen):
        """Test HTTP request rules with different parameter types."""
        ir = ConfigIR(
            name="test",
            frontends=[
                Frontend(
                    name="web",
                    binds=[Bind(address="*:80")],
                    http_request_rules=[
                        HttpRequestRule(
                            action="deny",
                            parameters={"deny_status": "403"},
                            condition="is_blocked",
                        ),
                        HttpRequestRule(
                            action="set-var",
                            parameters={
                                "name": "req.custom_var",
                                "value": "some value with spaces",
                            },
                        ),
                    ],
                )
            ],
        )

        output = codegen.generate(ir)

        assert "http-request deny deny status 403 if is_blocked" in output
        assert 'http-request set-var req.custom_var value "some value with spaces"' in output

    def test_output_to_file(self, codegen):
        """Test writing output to file."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "haproxy.cfg"
            ir = ConfigIR(name="test", version="2.0")

            result = codegen.generate(ir, output_path=output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert content == result
            assert "# Generated HAProxy configuration: test" in content

    def test_get_lua_files(self, codegen):
        """Test getting Lua files list."""
        ir = ConfigIR(
            name="test",
            global_config=GlobalConfig(
                lua_scripts=[
                    LuaScript(
                        name="script1",
                        source_type="file",
                        content="/etc/haproxy/lua/script1.lua",
                    ),
                    LuaScript(
                        name="script2",
                        source_type="file",
                        content="/etc/haproxy/lua/script2.lua",
                    ),
                ]
            ),
        )

        codegen.generate(ir)
        lua_files = codegen.get_lua_files()

        assert len(lua_files) == 2
        assert "/etc/haproxy/lua/script1.lua" in lua_files
        assert "/etc/haproxy/lua/script2.lua" in lua_files


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
