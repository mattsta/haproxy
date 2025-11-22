# Test Coverage Report - Path to 100%

## Executive Summary

- **Current Coverage**: 95% (176 lines missing)
- **Primary Target**: dsl_transformer.py (126 uncovered lines)
- **Secondary Targets**: 4 other files (7 total uncovered lines)

---

## Part 1: dsl_transformer.py Coverage Gaps (126 lines)

### Group 1: Import Statements (Lines 86-87)

**What it does**: Handles string-based import statements like `import:common_settings`

**Test Config Needed**:

```
config test {
    import: "base_config"

    backend app {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

**Status**: Likely working but never tested. Needs import resolution implementation.

---

### Group 2: Global Stats Configuration (Lines 477-478, 615, 1082-1096, 1099, 1102, 1105)

**What it does**: Parses StatsConfig objects in global section with enable, uri, and auth options

**Test Configs Needed**:

**Test 2A - Basic Stats**:

```
config test {
    global {
        stats {
            enable: true
            uri: "/haproxy-stats"
        }
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
```

**Test 2B - Stats with Auth**:

```
config test {
    global {
        stats {
            enable: true
            uri: "/admin/stats"
            auth: "admin:password123"
        }
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
```

**Test 2C - Stats disabled**:

```
config test {
    global {
        stats {
            enable: false
        }
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
```

---

### Group 3: Inline Lua with Parameters (Lines 1126-1130)

**What it does**: Parses lua-load-inline with optional parameters

**Test Config Needed**:

````
config test {
    global {
        lua {
            lua-load-inline my_script param1 value1 param2 value2 ```
            function validate_token(txn)
                local token = txn.sf:req_hdr("Authorization")
                if token == nil then
                    return false
                end
                return true
            end
            ```
        }
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
````

---

### Group 4: Defaults Section Features (Lines 1162, 1167, 1227)

**What it does**:

- Line 1162, 1227: `log` directive in defaults
- Line 1167: Single option (not list) in defaults

**Test Config Needed**:

```
config test {
    defaults {
        mode: http
        log: "global"
        option: "httplog"
        timeout {
            connect: "5s"
            client: "50s"
            server: "50s"
        }
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
```

---

### Group 5: Frontend HTTP Response Rules (Lines 1292, 1296)

**What it does**: Handles HttpResponseRule objects in frontend (single and in lists)

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        http-response {
            set-header X-Frame-Options value: "DENY"
        }

        http-response {
            set-header X-Content-Type-Options value: "nosniff"
        }

        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 6: Frontend TCP Rules (Lines 1300, 1304)

**What it does**: Handles TcpRequestRule and TcpResponseRule in frontend

**Test Config Needed**:

```
config test {
    frontend tcp_front {
        bind: "0.0.0.0:3306"
        mode: tcp

        tcp-request {
            content accept
        }

        tcp-response {
            content accept
        }

        default_backend: db_servers
    }

    backend db_servers {
        mode: tcp
        servers {
            server db1 {
                address: "10.0.1.10"
                port: 3306
            }
        }
    }
}
```

---

### Group 7: Frontend Use Backend Rules (Lines 1312, 1314)

**What it does**: Handles UseBackendRule objects in frontend (single and in lists)

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        acl is_api path_beg /api
        acl is_admin path_beg /admin

        use-backend api_servers if is_api
        use-backend admin_servers if is_admin

        default_backend: web_servers
    }

    backend api_servers {
        servers {
            server api1 { address: "10.0.1.1" port: 8080 }
        }
    }

    backend admin_servers {
        servers {
            server admin1 { address: "10.0.2.1" port: 8080 }
        }
    }

    backend web_servers {
        servers {
            server web1 { address: "10.0.3.1" port: 8080 }
        }
    }
}
```

---

### Group 8: Frontend Single Option (Line 1334)

**What it does**: Handles option as single string (not list) in frontend

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http
        option: "httplog"
        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 9: Frontend Maxconn (Lines 1348, 1410)

**What it does**: Handles maxconn directive in frontend

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http
        maxconn: 2000
        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 10: HTTP Action Expression Fallbacks (Lines 1479-1480, 1497-1498, 1515-1523, 1537)

**What it does**:

- Lines 1479-1480, 1497-1498: Fallback for old action format (non-tuple)
- Lines 1515-1523: Handles positional string values in action parameters
- Line 1537: Cast for http_rule_value

**Status**: These are fallback/legacy code paths. May be unreachable with current grammar.

**Test Config to Try** (old format):

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        http-request {
            set-header X-Custom-Header value: "custom-value" extra: "extra-value"
        }

        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 11: Use ACL Directive (Lines 1546-1548)

**What it does**: Creates placeholder ACL objects from use-acl directive

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        use-acl: ["acl_mobile", "acl_desktop"]

        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

**Note**: This may require grammar support for use-acl directive.

---

### Group 12: Single Use Backend (Lines 1562-1564)

**What it does**: Handles single use_backend directive (outside routing block)

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        acl is_api path_beg /api
        use-backend api_servers if is_api

        default_backend: web_servers
    }

    backend api_servers {
        servers {
            server api1 { address: "10.0.1.1" port: 8080 }
        }
    }

    backend web_servers {
        servers {
            server web1 { address: "10.0.2.1" port: 8080 }
        }
    }
}
```

---

### Group 13: Backend Servers/Rules in Lists (Lines 1598, 1600, 1617, 1619, 1625, 1631)

**What it does**: Handles servers and HTTP/TCP rules when they come as lists in backend

**Test Config Needed**:

```
config test {
    backend api {
        mode: http
        balance: roundrobin

        http-request {
            set-header X-Backend value: "api"
        }

        http-request {
            set-header X-Version value: "1.0"
        }

        http-response {
            set-header X-Powered-By value: "HAProxy"
        }

        servers {
            server api1 { address: "10.0.1.1" port: 8080 check: true }
            server api2 { address: "10.0.1.2" port: 8080 check: true }
            server api3 { address: "10.0.1.3" port: 8080 check: true }
        }
    }
}
```

---

### Group 14: Backend Single Option (Lines 1642, 1644)

**What it does**: Handles option as single string (not list) in backend

**Test Config Needed**:

```
config test {
    backend app {
        mode: http
        balance: roundrobin
        option: "httpchk"

        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
                check: true
            }
        }
    }
}
```

---

### Group 15: Backend Retries (Lines 1656, 1739)

**What it does**: Handles retries directive in backend

**Test Config Needed**:

```
config test {
    backend app {
        mode: http
        balance: roundrobin
        retries: 5

        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 16: Backend Cookie (Line 1703)

**What it does**: Handles cookie directive in backend

**Test Config Needed**:

```
config test {
    backend app {
        mode: http
        balance: roundrobin
        cookie: "SERVERID insert indirect nocache"

        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
                cookie: "srv1"
            }
        }
    }
}
```

---

### Group 17: Backend HTTP Rule Casts (Lines 1712, 1718, 1721)

**What it does**: Type casting for backend http-request and http-response directives

**Test Config Needed**:

```
config test {
    backend app {
        mode: http

        http-request {
            set-header X-Backend value: "app"
        }

        http-response {
            set-header Cache-Control value: "no-cache"
        }

        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 18: Listen Section Features (Lines 1923, 1931-1937, 1939, 1941, 1943, 1954, 1967, 1977, 2003)

**What it does**:

- Lines 1923, 1931-1937, 1939, 1941, 1943: Mixed ACL/Server/ForLoop lists in listen
- Line 1954: Single option (not list) in listen
- Line 1967: server_loops metadata in listen
- Lines 1977, 2003: health_check in listen

**Test Configs Needed**:

**Test 18A - Listen with ACLs**:

```
config test {
    listen stats
        bind: "0.0.0.0:8404"
        mode: http
        option: "httplog"

        acl is_local src 127.0.0.0/8
        acl is_admin path_beg /admin

        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    end
}
```

**Test 18B - Listen with Health Check**:

```
config test {
    listen mysql
        bind: "0.0.0.0:3306"
        mode: tcp
        balance: leastconn

        health-check {
            method: "GET"
            uri: "/health"
            expect: status 200
        }

        servers {
            server db1 {
                address: "10.0.1.1"
                port: 3306
                check: true
            }
        }
    end
}
```

**Test 18C - Listen with For Loop**:

```
config test {
    let server_count = 3

    listen web_cluster
        bind: "0.0.0.0:80"
        mode: http
        balance: roundrobin

        servers {
            for i in range(1, ${server_count}) {
                server web${i} {
                    address: "10.0.1.${i}"
                    port: 8080
                    check: true
                }
            }
        }
    end
}
```

---

### Group 19: Health Check Headers (Lines 2059-2062, 2086, 2113)

**What it does**: Parses custom headers in health-check blocks

**Test Config Needed**:

```
config test {
    backend api {
        balance: roundrobin

        health-check {
            method: "POST"
            uri: "/api/health"
            expect: status 200
            header: "Content-Type" "application/json"
            header: "X-API-Key" "secret123"
            header: "Accept" "application/json"
        }

        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
                check: true
            }
        }
    }
}
```

---

### Group 20: Servers Block Nested Lists (Lines 2121-2123)

**What it does**: Handles nested list structures in servers block

**Test Config Needed**:

```
config test {
    backend app {
        servers {
            for i in range(1, 3) {
                server app${i} {
                    address: "10.0.1.${i}"
                    port: 8080
                    check: true
                }
            }

            server backup {
                address: "10.0.2.1"
                port: 8080
                backup: true
            }
        }
    }
}
```

---

### Group 21: Server Send Proxy (Lines 2189, 2321)

**What it does**: Handles send_proxy option on servers

**Test Config Needed**:

```
config test {
    backend app {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
                send-proxy: true
            }
        }
    }
}
```

---

### Group 22: Server Template Block (Lines 2447-2473)

**What it does**: Parses server-template directive with range

**Test Config Needed**:

```
config test {
    backend app {
        server-template web 1-10 {
            port: 8080
            check: true
            inter: "2s"
            rise: 3
            fall: 2
            weight: 50
        }
    }
}
```

---

### Group 23: ACL Empty Criterion Fallback (Lines 2522-2523)

**What it does**: Fallback when ACL criterion parsing returns empty

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        # ACL without criterion (edge case)
        acl test_acl

        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

**Note**: This is likely an error case - may not be valid syntax.

---

### Group 24: Import Statement (Line 2558)

**What it does**: Parses import statement and returns formatted string

**Test Config Needed**: (Same as Group 1)

```
config test {
    import: "common_config"

    backend app {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 25: Expression Fallback (Line 2579)

**What it does**: Returns None when expression has no items

**Status**: This is an edge case fallback. May be unreachable with valid syntax.

---

### Group 26: Float Number Parsing (Line 2630)

**What it does**: Parses floating point numbers

**Test Config Needed**:

```
config test {
    let timeout_value = 5.5

    defaults {
        timeout {
            connect: "5.5s"
            client: "30.25s"
            server: "30.25s"
        }
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
```

---

### Group 27: Boolean False Path (Line 2637)

**What it does**: Returns False when boolean items list is empty

**Status**: Edge case - when boolean parsing fails. Likely unreachable.

---

### Group 28: Empty Collections (Lines 2653, 2656, 2665-2667, 2670, 2673)

**What it does**:

- Lines 2653, 2656: Empty identifier_array and identifier_list
- Lines 2665-2667: Empty object
- Lines 2670, 2673: Empty object_pair_list and object_pair

**Status**: Edge cases for empty data structures. May need specific syntax:

**Test Config to Try**:

```
config test {
    template empty_template {
    }

    backend app {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
                metadata: {}
            }
        }
    }
}
```

---

### Group 29: Stick Table Type Fallback (Line 2718)

**What it does**: Returns "ip" as default stick-table type when items empty

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        stick-table {
            size: 100000
            expire: "30m"
        }

        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 30: Function Args Empty (Line 2746)

**What it does**: Returns empty string when function has no arguments

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        acl no_args_test method()

        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

**Note**: May not be valid syntax - functions usually require arguments.

---

### Group 31: Stick Rule Fallbacks (Lines 2772, 2778)

**What it does**: Fallback paths for stick rule parsing

**Test Config Needed**:

```
config test {
    frontend web {
        bind: "0.0.0.0:80"
        mode: http

        stick-table {
            type: ip
            size: 100000
            expire: "30m"
        }

        stick on src if { src 10.0.0.0/8 }

        default_backend: web_servers
    }

    backend web_servers {
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8080
            }
        }
    }
}
```

---

### Group 32: TCP Request Type Fallback (Line 2811)

**What it does**: Returns "connection" as default tcp-request type

**Test Config Needed**:

```
config test {
    frontend tcp_front {
        bind: "0.0.0.0:443"
        mode: tcp

        tcp-request {
            accept
        }

        default_backend: ssl_servers
    }

    backend ssl_servers {
        mode: tcp
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8443
            }
        }
    }
}
```

---

### Group 33: TCP Rule Parameters (Lines 2879, 2883)

**What it does**: Transforms tcp rule parameters and values

**Test Config Needed**:

```
config test {
    frontend tcp_front {
        bind: "0.0.0.0:443"
        mode: tcp

        tcp-request {
            content accept delay: "5s"
        }

        default_backend: ssl_servers
    }

    backend ssl_servers {
        mode: tcp
        servers {
            server srv1 {
                address: "127.0.0.1"
                port: 8443
            }
        }
    }
}
```

---

## Part 2: Other File Coverage Gaps (7 lines)

### codegen/haproxy.py (Lines 1039, 1056)

**What it does**: Handles TCP request/response rules with named parameters (not params list)

**Test Config Needed**:

```
config test {
    frontend tcp_front {
        bind: "0.0.0.0:3306"
        mode: tcp

        tcp-request {
            content accept timeout: "10s"
        }

        tcp-response {
            content accept timeout: "10s"
        }

        default_backend: db_servers
    }

    backend db_servers {
        mode: tcp
        servers {
            server db1 {
                address: "10.0.1.10"
                port: 3306
            }
        }
    }
}
```

---

### dsl_parser.py (Lines 30-33)

**What it does**: Python 3.7-3.8 fallback for loading grammar file

**How to Test**:

1. Mock `resources.files()` to raise AttributeError
2. Verify fallback to `resources.open_text()` is called

**Python Test Code**:

```python
def test_python37_fallback(monkeypatch):
    """Test Python 3.7-3.8 resource loading fallback."""
    # Mock resources.files to raise AttributeError
    import importlib.resources as resources

    def mock_files(*args):
        raise AttributeError("files() not available")

    monkeypatch.setattr(resources, "files", mock_files)

    # Create parser - should use fallback
    parser = DSLParser()
    assert parser.parser is not None
```

---

### template_expander.py (Line 40)

**What it does**: Converts single template_spread value to list

**Test Config Needed**: Already covered in existing tests

```
config test {
    template web_server {
        check: true
        maxconn: 100
    }

    backend app {
        servers {
            server srv1 {
                address: "192.168.1.10"
                port: 9000
                @web_server
            }
        }
    }
}
```

**Note**: This is already in test_coverage_100_percent.py as `test_template_spread_single_not_list`

---

### variable_resolver.py (Line 105)

**What it does**: Recursively resolves variables in dictionary values

**Test Config Needed**:

```
config test {
    let base_port = 8080
    let base_host = "192.168.1"

    template server_config {
        port: ${base_port}
        check: true
        maxconn: 100
        metadata: {
            host: "${base_host}.10"
            port: ${base_port}
        }
    }

    backend app {
        servers {
            server srv1 {
                address: "${base_host}.10"
                @server_config
            }
        }
    }
}
```

---

## Part 3: Likely Unreachable Code (Dead Code Candidates)

These lines may be unreachable with the current grammar/implementation:

1. **Lines 1479-1480, 1497-1498**: Action expression fallback for old format
   - **Why unreachable**: Current grammar always produces tuple format
   - **Recommendation**: Add comment or remove if confirmed unused

2. **Line 1537**: http_rule_value cast
   - **Why unreachable**: Always returns items[0] which is already a string
   - **Recommendation**: Review if cast is necessary

3. **Lines 1546-1548**: use_acl_directive
   - **Why unreachable**: No `use-acl` directive in current grammar
   - **Recommendation**: Remove or implement grammar support

4. **Lines 2522-2523**: ACL empty criterion fallback
   - **Why unreachable**: Grammar requires criterion for ACL
   - **Recommendation**: Keep as safety fallback

5. **Line 2579**: expression with no items returning None
   - **Why unreachable**: Grammar always produces items
   - **Recommendation**: Keep as safety fallback

6. **Line 2637**: boolean returning False on empty items
   - **Why unreachable**: Grammar token always present
   - **Recommendation**: Keep as safety fallback

7. **Lines 2665-2667, 2670, 2673**: Empty object/list returns
   - **Why unreachable**: May be reachable with specific syntax
   - **Recommendation**: Keep as safety fallbacks

8. **Line 2718**: Stick table type fallback to "ip"
   - **Why unreachable**: Grammar should always provide type
   - **Recommendation**: Keep as safety fallback

9. **Line 2746**: Function args returning empty string
   - **Why unreachable**: Functions typically require arguments
   - **Recommendation**: Keep as safety fallback

10. **Lines 2772, 2778**: Stick rule type fallbacks
    - **Why unreachable**: Grammar should provide rule_type tuple
    - **Recommendation**: Keep as safety fallbacks

---

## Part 4: Recommended Testing Strategy

### Phase 1: High-Value Tests (Will cover 80+ lines)

1. **Stats Configuration** (Group 2) - 15 lines
2. **Listen Section** (Group 18) - 20 lines
3. **Frontend HTTP/TCP Rules** (Groups 5, 6, 7) - 15 lines
4. **Backend Lists** (Group 13) - 10 lines
5. **Health Check Headers** (Group 19) - 5 lines
6. **Server Template** (Group 22) - 27 lines

### Phase 2: Medium-Value Tests (Will cover 30+ lines)

7. **Inline Lua with Params** (Group 3) - 5 lines
8. **Defaults Features** (Group 4) - 3 lines
9. **Frontend/Backend Options** (Groups 8, 14) - 4 lines
10. **Frontend/Backend Maxconn** (Group 9) - 2 lines
11. **Backend Cookie/Retries** (Groups 15, 16) - 3 lines
12. **Send Proxy** (Group 21) - 2 lines
13. **TCP Parameters** (Group 33) - 2 lines
14. **Variable Dict Resolution** (variable_resolver.py) - 1 line
15. **TCP Codegen** (codegen/haproxy.py) - 2 lines

### Phase 3: Edge Cases (Will cover remaining lines)

16. **Float Numbers** (Group 26)
17. **Stick Rules** (Groups 29, 31)
18. **TCP Type Fallback** (Group 32)
19. **Import Statement** (Groups 1, 24)
20. **Empty Collections** (Group 28)
21. **Python 3.7 Fallback** (dsl_parser.py)

### Phase 4: Document/Remove Dead Code

22. Review unreachable code and either:
    - Add `# pragma: no cover` comments
    - Remove if confirmed unused
    - Add integration tests if edge cases exist

---

## Part 5: Example Test File Structure

```python
"""Tests to achieve final 100% code coverage."""

import pytest
from haproxy_translator.parsers import DSLParser
from haproxy_translator.codegen.haproxy import HAProxyCodeGenerator


class TestFinalCoverage:
    """Tests targeting remaining uncovered lines."""

    @pytest.fixture
    def parser(self):
        return DSLParser()

    @pytest.fixture
    def codegen(self):
        return HAProxyCodeGenerator()

    # ===== Stats Configuration =====

    def test_global_stats_basic(self, parser, codegen):
        """Cover lines 477-478, 615, 1082-1096."""
        config = '''
        config test {
            global {
                stats {
                    enable: true
                    uri: "/haproxy-stats"
                }
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
        '''
        ir = parser.parse(config)
        assert ir.global_config.stats is not None
        assert ir.global_config.stats.enable is True
        assert ir.global_config.stats.uri == "/haproxy-stats"

        output = codegen.generate(ir)
        assert "stats enable" in output
        assert "stats uri /haproxy-stats" in output

    def test_global_stats_with_auth(self, parser, codegen):
        """Cover lines 1099, 1102, 1105."""
        config = '''
        config test {
            global {
                stats {
                    enable: true
                    uri: "/admin"
                    auth: "admin:secret"
                }
            }

            backend app {
                servers {
                    server srv1 { address: "127.0.0.1" port: 8080 }
                }
            }
        }
        '''
        ir = parser.parse(config)
        assert ir.global_config.stats.auth == "admin:secret"

        output = codegen.generate(ir)
        assert "stats auth admin:secret" in output

    # ... Continue with other test groups
```

---

## Part 6: Summary of Actions

| Priority | Group                | Lines | Effort | Impact |
| -------- | -------------------- | ----- | ------ | ------ |
| P0       | Stats Config         | 15    | Low    | High   |
| P0       | Listen Section       | 20    | Medium | High   |
| P0       | Frontend Rules       | 15    | Low    | High   |
| P0       | Server Template      | 27    | Medium | High   |
| P1       | Backend Lists        | 10    | Low    | Medium |
| P1       | Health Check Headers | 5     | Low    | Medium |
| P1       | Lua Parameters       | 5     | Low    | Medium |
| P1       | TCP Codegen          | 2     | Low    | Medium |
| P2       | Various Options      | 15    | Low    | Medium |
| P2       | Variable Dict        | 1     | Low    | Low    |
| P3       | Edge Cases           | 20    | Medium | Low    |
| P4       | Dead Code Review     | ??    | Medium | Low    |

**Total Estimated Effort**: 2-3 hours to implement all tests

**Expected Coverage Gain**: Should reach 98-99%, with remaining 1-2% being confirmed dead code

---

## Conclusion

The path to 100% coverage is clear:

1. **Add ~30 new test configs** targeting specific uncovered features
2. **Review ~20 lines** of likely unreachable code for documentation or removal
3. **Focus on high-value tests first** (stats, listen, rules) to quickly boost coverage
4. **Use existing test patterns** from test_coverage_100_percent.py as templates

Most uncovered code is legitimate functionality that simply hasn't been tested yet. The remaining gaps can be closed with targeted, well-structured test cases using the DSL syntax patterns shown above.
