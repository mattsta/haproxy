# HAProxy Config Translator - Migration Guide

This guide shows how to convert existing HAProxy configurations to the modern DSL syntax.

## Table of Contents

1. [Basic Structure](#basic-structure)
2. [Global Section](#global-section)
3. [Defaults Section](#defaults-section)
4. [Frontend Section](#frontend-section)
5. [Backend Section](#backend-section)
6. [Listen Section](#listen-section)
7. [ACLs and Conditions](#acls-and-conditions)
8. [HTTP Rules](#http-rules)
9. [TCP Rules](#tcp-rules)
10. [Stick Tables](#stick-tables)
11. [SSL/TLS Configuration](#ssltls-configuration)
12. [Health Checks](#health-checks)
13. [Advanced Features](#advanced-features)

---

## Basic Structure

### HAProxy Native Syntax
```haproxy
global
    daemon
    maxconn 4096
    log 127.0.0.1 local0

defaults
    mode http
    timeout connect 5s
    timeout client 30s
    timeout server 30s

frontend web
    bind *:80
    default_backend servers

backend servers
    balance roundrobin
    server web1 192.168.1.10:8080 check
```

### Modern DSL Syntax
```javascript
global {
    daemon: true
    maxconn: 4096
    log: "127.0.0.1 local0"
}

defaults {
    mode: "http"
    timeouts: {
        connect: "5s"
        client: "30s"
        server: "30s"
    }
}

frontend web {
    bind: "*:80"
    default_backend: "servers"
}

backend servers {
    balance: "roundrobin"
    servers: [
        { name: "web1", address: "192.168.1.10", port: 8080, check: true }
    ]
}
```

---

## Global Section

### Process Management

```haproxy
# HAProxy Native
global
    daemon
    user haproxy
    group haproxy
    chroot /var/lib/haproxy
    pidfile /var/run/haproxy.pid
    maxconn 4096
    nbthread 4
```

```javascript
// Modern DSL
global {
    daemon: true
    user: "haproxy"
    group: "haproxy"
    chroot: "/var/lib/haproxy"
    pidfile: "/var/run/haproxy.pid"
    maxconn: 4096
    nbthread: 4
}
```

### Logging

```haproxy
# HAProxy Native
global
    log 127.0.0.1 local0
    log 127.0.0.1 local1 notice
    log-send-hostname
    log-tag haproxy
```

```javascript
// Modern DSL
global {
    log: "127.0.0.1 local0"
    // Multiple logs via array
    logs: ["127.0.0.1 local0", "127.0.0.1 local1 notice"]
    log-send-hostname: true
    log-tag: "haproxy"
}
```

### SSL/TLS Defaults

```haproxy
# HAProxy Native
global
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    ssl-default-server-ciphers ECDHE-ECDSA-AES128-GCM-SHA256
    ssl-dh-param-file /etc/haproxy/dhparam.pem
```

```javascript
// Modern DSL
global {
    ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
    ssl-default-bind-ciphersuites: "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"
    ssl-default-bind-options: "ssl-min-ver TLSv1.2 no-tls-tickets"
    ssl-default-server-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256"
    ssl-dh-param-file: "/etc/haproxy/dhparam.pem"
}
```

### Performance Tuning

```haproxy
# HAProxy Native
global
    tune.bufsize 16384
    tune.maxrewrite 1024
    tune.ssl.cachesize 20000
    tune.ssl.lifetime 300
    tune.http.maxhdr 101
    tune.comp.maxlevel 5
```

```javascript
// Modern DSL
global {
    tune.bufsize: 16384
    tune.maxrewrite: 1024
    tune.ssl.cachesize: 20000
    tune.ssl.lifetime: 300
    tune.http.maxhdr: 101
    tune.comp.maxlevel: 5
}
```

---

## Defaults Section

### Timeouts

```haproxy
# HAProxy Native
defaults
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    timeout check 5s
    timeout http-request 10s
    timeout http-keep-alive 10s
    timeout queue 30s
    timeout tunnel 1h
```

```javascript
// Modern DSL
defaults {
    timeouts: {
        connect: "5s"
        client: "30s"
        server: "30s"
        check: "5s"
        http_request: "10s"
        http_keep_alive: "10s"
        queue: "30s"
        tunnel: "1h"
    }
}
```

### Options

```haproxy
# HAProxy Native
defaults
    option httplog
    option dontlognull
    option http-server-close
    option forwardfor except 127.0.0.0/8
    option redispatch
    no option httpclose
```

```javascript
// Modern DSL
defaults {
    options: [
        "httplog",
        "dontlognull",
        "http-server-close",
        "forwardfor except 127.0.0.0/8",
        "redispatch"
    ]
    // Use "no option X" for disabled options
    // options: ["no httpclose"]
}
```

### Retries and Error Handling

```haproxy
# HAProxy Native
defaults
    retries 3
    retry-on conn-failure empty-response response-timeout
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 500 /etc/haproxy/errors/500.http
```

```javascript
// Modern DSL
defaults {
    retries: 3
    retry_on: "conn-failure empty-response response-timeout"
    errorfiles: {
        400: "/etc/haproxy/errors/400.http"
        403: "/etc/haproxy/errors/403.http"
        500: "/etc/haproxy/errors/500.http"
    }
}
```

---

## Frontend Section

### Basic Frontend

```haproxy
# HAProxy Native
frontend http-in
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/site.pem
    mode http
    maxconn 10000
    default_backend webservers
```

```javascript
// Modern DSL
frontend http_in {
    bind: "*:80"
    binds: [
        { address: "*:443", ssl: { cert: "/etc/ssl/certs/site.pem" } }
    ]
    mode: "http"
    maxconn: 10000
    default_backend: "webservers"
}
```

### Multiple Binds with Options

```haproxy
# HAProxy Native
frontend https
    bind *:443 ssl crt /etc/ssl/certs/site.pem alpn h2,http/1.1
    bind *:8443 ssl crt /etc/ssl/certs/admin.pem verify required ca-file /etc/ssl/ca.pem
    bind /var/run/haproxy.sock mode 600 user haproxy
```

```javascript
// Modern DSL
frontend https {
    binds: [
        {
            address: "*:443",
            ssl: {
                cert: "/etc/ssl/certs/site.pem",
                alpn: "h2,http/1.1"
            }
        },
        {
            address: "*:8443",
            ssl: {
                cert: "/etc/ssl/certs/admin.pem",
                verify: "required",
                ca_file: "/etc/ssl/ca.pem"
            }
        },
        {
            address: "/var/run/haproxy.sock",
            mode: "600",
            user: "haproxy"
        }
    ]
}
```

### Request Routing

```haproxy
# HAProxy Native
frontend web
    bind *:80
    acl is_api path_beg /api/
    acl is_static path_beg /static/
    acl host_admin hdr(host) -i admin.example.com

    use_backend api_servers if is_api
    use_backend static_servers if is_static
    use_backend admin_servers if host_admin
    default_backend webservers
```

```javascript
// Modern DSL
frontend web {
    bind: "*:80"

    acls: [
        { name: "is_api", criterion: "path_beg /api/" },
        { name: "is_static", criterion: "path_beg /static/" },
        { name: "host_admin", criterion: "hdr(host) -i admin.example.com" }
    ]

    use_backends: [
        { backend: "api_servers", condition: "if is_api" },
        { backend: "static_servers", condition: "if is_static" },
        { backend: "admin_servers", condition: "if host_admin" }
    ]

    default_backend: "webservers"
}
```

---

## Backend Section

### Basic Backend

```haproxy
# HAProxy Native
backend webservers
    mode http
    balance roundrobin
    option httpchk GET /health
    server web1 192.168.1.10:8080 check weight 10
    server web2 192.168.1.11:8080 check weight 10
    server web3 192.168.1.12:8080 check weight 5 backup
```

```javascript
// Modern DSL
backend webservers {
    mode: "http"
    balance: "roundrobin"
    options: ["httpchk GET /health"]

    servers: [
        { name: "web1", address: "192.168.1.10", port: 8080,
          check: true, weight: 10 },
        { name: "web2", address: "192.168.1.11", port: 8080,
          check: true, weight: 10 },
        { name: "web3", address: "192.168.1.12", port: 8080,
          check: true, weight: 5, backup: true }
    ]
}
```

### Advanced Server Options

```haproxy
# HAProxy Native
backend api
    server api1 10.0.1.1:8080 check inter 3s fall 3 rise 2 maxconn 100 ssl verify none sni req.hdr(host)
    server api2 10.0.1.2:8080 check inter 3s fall 3 rise 2 maxconn 100 ssl verify none sni req.hdr(host)
```

```javascript
// Modern DSL
backend api {
    servers: [
        {
            name: "api1",
            address: "10.0.1.1",
            port: 8080,
            check: true,
            inter: "3s",
            fall: 3,
            rise: 2,
            maxconn: 100,
            ssl: true,
            verify: "none",
            sni: "req.hdr(host)"
        },
        {
            name: "api2",
            address: "10.0.1.2",
            port: 8080,
            check: true,
            inter: "3s",
            fall: 3,
            rise: 2,
            maxconn: 100,
            ssl: true,
            verify: "none",
            sni: "req.hdr(host)"
        }
    ]
}
```

### Server Templates

```haproxy
# HAProxy Native
backend dynamic
    server-template srv 1-10 10.0.1.1:8080 check resolvers mydns
```

```javascript
// Modern DSL
backend dynamic {
    server_templates: [
        {
            prefix: "srv",
            range: "1-10",
            address: "10.0.1.1",
            port: 8080,
            check: true,
            resolvers: "mydns"
        }
    ]
}
```

---

## Listen Section

```haproxy
# HAProxy Native
listen stats
    bind *:8404
    mode http
    stats enable
    stats uri /stats
    stats refresh 10s
    stats auth admin:password
    stats admin if LOCALHOST
```

```javascript
// Modern DSL
listen stats {
    bind: "*:8404"
    mode: "http"

    stats: {
        enable: true
        uri: "/stats"
        refresh: "10s"
        auth: "admin:password"
        admin: "if LOCALHOST"
    }
}
```

---

## ACLs and Conditions

### Named ACLs

```haproxy
# HAProxy Native
frontend web
    acl is_api path_beg -i /api/
    acl is_websocket hdr(Upgrade) -i websocket
    acl host_example hdr(host) -i example.com www.example.com
    acl method_post method POST
    acl src_internal src 192.168.0.0/16 10.0.0.0/8
```

```javascript
// Modern DSL
frontend web {
    acls: [
        { name: "is_api", criterion: "path_beg -i /api/" },
        { name: "is_websocket", criterion: "hdr(Upgrade) -i websocket" },
        { name: "host_example", criterion: "hdr(host) -i example.com www.example.com" },
        { name: "method_post", criterion: "method POST" },
        { name: "src_internal", criterion: "src 192.168.0.0/16 10.0.0.0/8" }
    ]
}
```

### Inline ACLs in Conditions

```haproxy
# HAProxy Native
frontend web
    use_backend api if { path_beg /api/ }
    use_backend static if { path_end .jpg .png .css .js }
```

```javascript
// Modern DSL
frontend web {
    use_backends: [
        { backend: "api", condition: "if { path_beg /api/ }" },
        { backend: "static", condition: "if { path_end .jpg .png .css .js }" }
    ]
}
```

---

## HTTP Rules

### HTTP Request Rules

```haproxy
# HAProxy Native
frontend web
    http-request deny if { path_beg /admin } !src_internal
    http-request set-header X-Forwarded-Proto https if { ssl_fc }
    http-request add-header X-Request-ID %[uuid()]
    http-request redirect scheme https unless { ssl_fc }
    http-request set-var(txn.path) path
```

```javascript
// Modern DSL
frontend web {
    http-request {
        deny if { path_beg /admin } !src_internal
        set-header "X-Forwarded-Proto" "https" if { ssl_fc }
        add-header "X-Request-ID" "%[uuid()]"
        redirect scheme "https" unless { ssl_fc }
        set-var(txn.path) path
    }
}
```

### HTTP Response Rules

```haproxy
# HAProxy Native
backend api
    http-response set-header X-Frame-Options DENY
    http-response set-header X-Content-Type-Options nosniff
    http-response del-header Server
    http-response add-header Strict-Transport-Security "max-age=31536000; includeSubDomains"
```

```javascript
// Modern DSL
backend api {
    http-response {
        set-header "X-Frame-Options" "DENY"
        set-header "X-Content-Type-Options" "nosniff"
        del-header "Server"
        add-header "Strict-Transport-Security" "max-age=31536000; includeSubDomains"
    }
}
```

---

## TCP Rules

```haproxy
# HAProxy Native
frontend tcp-in
    mode tcp
    tcp-request connection reject if { src -f /etc/haproxy/blacklist.lst }
    tcp-request content accept if { req.ssl_hello_type 1 }
    tcp-request inspect-delay 5s
```

```javascript
// Modern DSL
frontend tcp_in {
    mode: "tcp"

    tcp-request {
        connection reject if { src -f /etc/haproxy/blacklist.lst }
        content accept if { req.ssl_hello_type 1 }
        inspect-delay "5s"
    }
}
```

---

## Stick Tables

```haproxy
# HAProxy Native
backend api
    stick-table type ip size 100k expire 30m store conn_cur,conn_rate(10s),http_req_rate(10s)
    stick on src
    stick match src
    stick store-request src
```

```javascript
// Modern DSL
backend api {
    stick_table: {
        type: "ip"
        size: "100k"
        expire: "30m"
        store: "conn_cur,conn_rate(10s),http_req_rate(10s)"
    }

    stick_rules: [
        { type: "on", pattern: "src" },
        { type: "match", pattern: "src" },
        { type: "store-request", pattern: "src" }
    ]
}
```

---

## SSL/TLS Configuration

### SSL Termination

```haproxy
# HAProxy Native
frontend https
    bind *:443 ssl crt /etc/ssl/certs/combined.pem crt-list /etc/ssl/crt-list.txt ca-file /etc/ssl/ca.pem verify optional crl-file /etc/ssl/crl.pem alpn h2,http/1.1
```

```javascript
// Modern DSL
frontend https {
    binds: [
        {
            address: "*:443",
            ssl: {
                cert: "/etc/ssl/certs/combined.pem",
                crt_list: "/etc/ssl/crt-list.txt",
                ca_file: "/etc/ssl/ca.pem",
                verify: "optional",
                crl_file: "/etc/ssl/crl.pem",
                alpn: "h2,http/1.1"
            }
        }
    ]
}
```

### Backend SSL

```haproxy
# HAProxy Native
backend secure-api
    server api1 10.0.1.1:443 ssl verify required ca-file /etc/ssl/ca.pem sni str(api.internal) check-ssl check-sni api.internal
```

```javascript
// Modern DSL
backend secure_api {
    servers: [
        {
            name: "api1",
            address: "10.0.1.1",
            port: 443,
            ssl: true,
            verify: "required",
            ca_file: "/etc/ssl/ca.pem",
            sni: "str(api.internal)",
            check_ssl: true,
            check_sni: "api.internal"
        }
    ]
}
```

---

## Health Checks

### HTTP Health Checks

```haproxy
# HAProxy Native
backend api
    option httpchk
    http-check connect
    http-check send meth GET uri /health ver HTTP/1.1 hdr Host api.example.com
    http-check expect status 200
```

```javascript
// Modern DSL
backend api {
    options: ["httpchk"]

    http_check: {
        connect: true
        send: {
            method: "GET"
            uri: "/health"
            version: "HTTP/1.1"
            headers: {
                Host: "api.example.com"
            }
        }
        expect: { status: "200" }
    }
}
```

### TCP Health Checks

```haproxy
# HAProxy Native
backend redis
    option tcp-check
    tcp-check connect
    tcp-check send "PING\r\n"
    tcp-check expect string +PONG
```

```javascript
// Modern DSL
backend redis {
    options: ["tcp-check"]

    tcp_check: [
        { connect: true },
        { send: "PING\\r\\n" },
        { expect: { string: "+PONG" } }
    ]
}
```

---

## Advanced Features

### Compression

```haproxy
# HAProxy Native
frontend web
    compression algo gzip
    compression type text/html text/plain text/css application/javascript
    compression offload
```

```javascript
// Modern DSL
frontend web {
    compression: {
        algo: "gzip"
        type: "text/html text/plain text/css application/javascript"
        offload: true
    }
}
```

### Rate Limiting

```haproxy
# HAProxy Native
frontend web
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
```

```javascript
// Modern DSL
frontend web {
    stick_table: {
        type: "ip"
        size: "100k"
        expire: "30s"
        store: "http_req_rate(10s)"
    }

    http-request {
        track-sc0 src
        deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
    }
}
```

### Email Alerts

```haproxy
# HAProxy Native
mailers alerters
    mailer smtp1 smtp.example.com:587

backend api
    email-alert mailers alerters
    email-alert from haproxy@example.com
    email-alert to ops@example.com
    email-alert level alert
```

```javascript
// Modern DSL
mailers alerters {
    mailers: [
        { name: "smtp1", address: "smtp.example.com", port: 587 }
    ]
}

backend api {
    email_alert: {
        mailers: "alerters"
        from: "haproxy@example.com"
        to: "ops@example.com"
        level: "alert"
    }
}
```

---

## Migration Tips

### 1. Start with Structure
Convert the basic structure first (global, defaults, frontends, backends), then add details.

### 2. Use Variables for Repetition
If you see repeated values, extract them to variables:

```javascript
variables {
    check_interval = "3s"
    server_maxconn = 100
}
```

### 3. Use Loops for Similar Servers
Replace repetitive server definitions with loops:

```javascript
// Instead of:
servers: [
    { name: "web1", address: "10.0.1.1", port: 8080 },
    { name: "web2", address: "10.0.1.2", port: 8080 },
    { name: "web3", address: "10.0.1.3", port: 8080 }
]

// Use:
for i in [1, 2, 3] {
    server "web${i}" "10.0.1.${i}":8080 check
}
```

### 4. Leverage Environment Variables
Use environment variables for deployment-specific values:

```javascript
global {
    maxconn: ${env.HAPROXY_MAXCONN:-4096}
}

backend api {
    servers: [
        { name: "api", address: "${env.API_HOST}", port: ${env.API_PORT:-8080} }
    ]
}
```

### 5. Validate Early and Often
Use the validator to catch errors:

```bash
uv run haproxy-translate config.hap --validate
```

---

## See Also

- [Quick Start Guide](QUICK_START.md)
- [Syntax Reference](SYNTAX_REFERENCE.md)
- [Architecture Guide](ARCHITECTURE.md)
