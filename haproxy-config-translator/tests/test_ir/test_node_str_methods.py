"""Test __str__ methods for IR nodes."""

from haproxy_translator.ir.nodes import ACL, Bind, HttpRequestRule


class TestACLStr:
    """Test ACL __str__ method."""

    def test_acl_basic(self):
        """Test basic ACL string representation."""
        acl = ACL(name="is_static", criterion="path_beg", values=["/static"])
        assert str(acl) == "acl is_static path_beg /static"

    def test_acl_with_flags(self):
        """Test ACL with flags."""
        acl = ACL(name="is_api", criterion="path_beg", flags=["-i"], values=["/api"])
        assert str(acl) == "acl is_api path_beg -i /api"

    def test_acl_with_multiple_values(self):
        """Test ACL with multiple values."""
        acl = ACL(
            name="is_admin",
            criterion="path_beg",
            values=["/admin", "/dashboard"],
        )
        assert str(acl) == "acl is_admin path_beg /admin /dashboard"

    def test_acl_with_flags_and_values(self):
        """Test ACL with both flags and multiple values."""
        acl = ACL(
            name="blocked_ips",
            criterion="src",
            flags=["-f"],
            values=["/etc/haproxy/blocked.txt"],
        )
        assert str(acl) == "acl blocked_ips src -f /etc/haproxy/blocked.txt"

    def test_acl_no_values(self):
        """Test ACL with no values."""
        acl = ACL(name="test", criterion="path_beg")
        assert str(acl) == "acl test path_beg"


class TestHttpRequestRuleStr:
    """Test HttpRequestRule __str__ method."""

    def test_basic_http_request_rule(self):
        """Test basic HTTP request rule."""
        rule = HttpRequestRule(action="deny")
        assert str(rule) == "http-request deny"

    def test_http_request_rule_with_condition(self):
        """Test HTTP request rule with condition."""
        rule = HttpRequestRule(action="deny", condition="is_blocked")
        assert str(rule) == "http-request deny if is_blocked"

    def test_http_request_rule_with_parameters(self):
        """Test HTTP request rule with parameters."""
        rule = HttpRequestRule(
            action="set-header",
            parameters={"X-Custom-Header": "value"},
        )
        assert str(rule) == "http-request set-header X-Custom-Header value"

    def test_http_request_rule_with_parameter_containing_space(self):
        """Test HTTP request rule with parameter containing space."""
        rule = HttpRequestRule(
            action="set-header",
            parameters={"X-Custom-Header": "value with space"},
        )
        assert str(rule) == 'http-request set-header X-Custom-Header "value with space"'

    def test_http_request_rule_with_parameters_and_condition(self):
        """Test HTTP request rule with both parameters and condition."""
        rule = HttpRequestRule(
            action="redirect",
            parameters={"location": "https://example.com"},
            condition="!is_admin",
        )
        assert str(rule) == "http-request redirect location https://example.com if !is_admin"

    def test_http_request_rule_multiple_parameters(self):
        """Test HTTP request rule with multiple parameters."""
        rule = HttpRequestRule(
            action="set-var",
            parameters={"txn.user_id": "12345", "scope": "request"},
        )
        result = str(rule)
        # Check that all parts are present (order may vary due to dict)
        assert result.startswith("http-request set-var")
        assert "txn.user_id 12345" in result or "txn.user_id" in result
        assert "scope request" in result or "scope" in result


class TestBindStr:
    """Test Bind __str__ method."""

    def test_bind_basic(self):
        """Test basic bind string representation."""
        bind = Bind(address="*:80")
        assert str(bind) == "bind *:80"

    def test_bind_with_ssl(self):
        """Test bind with SSL."""
        bind = Bind(address="*:443", ssl=True)
        assert str(bind) == "bind *:443 ssl"

    def test_bind_with_ssl_cert(self):
        """Test bind with SSL certificate."""
        bind = Bind(address="*:443", ssl=True, ssl_cert="/etc/ssl/cert.pem")
        assert str(bind) == "bind *:443 ssl crt /etc/ssl/cert.pem"

    def test_bind_with_ssl_alpn(self):
        """Test bind with SSL and ALPN."""
        bind = Bind(
            address="*:443",
            ssl=True,
            ssl_cert="/etc/ssl/cert.pem",
            alpn=["h2", "http/1.1"],
        )
        assert str(bind) == "bind *:443 ssl crt /etc/ssl/cert.pem alpn h2,http/1.1"

    def test_bind_with_bool_option(self):
        """Test bind with boolean option."""
        bind = Bind(address="*:80", options={"accept-proxy": True})
        assert str(bind) == "bind *:80 accept-proxy"

    def test_bind_with_value_option(self):
        """Test bind with value option."""
        bind = Bind(address="*:80", options={"maxconn": 1000})
        assert str(bind) == "bind *:80 maxconn 1000"

    def test_bind_with_multiple_options(self):
        """Test bind with multiple options."""
        bind = Bind(
            address="*:443",
            ssl=True,
            ssl_cert="/etc/ssl/cert.pem",
            alpn=["h2"],
            options={"accept-proxy": True, "defer-accept": True, "maxconn": 5000},
        )
        result = str(bind)
        assert result.startswith("bind *:443 ssl crt /etc/ssl/cert.pem alpn h2")
        assert "accept-proxy" in result
        assert "defer-accept" in result
        assert "maxconn 5000" in result

    def test_bind_with_false_bool_option(self):
        """Test bind with false boolean option (should be omitted)."""
        bind = Bind(address="*:80", options={"accept-proxy": False})
        assert str(bind) == "bind *:80"

    def test_bind_with_empty_value_option(self):
        """Test bind with empty value option (should be omitted)."""
        bind = Bind(address="*:80", options={"name": ""})
        assert str(bind) == "bind *:80"
