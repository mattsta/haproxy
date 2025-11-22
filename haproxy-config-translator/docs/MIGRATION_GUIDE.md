# HAProxy Config Translator - Migration Guide

This guide shows how to convert existing HAProxy configurations to the modern DSL syntax.

## Important: Config Wrapper Requirement

All DSL configurations must be wrapped in a `config name { }` block:

```javascript
config my_config {
  global { ... }
  defaults { ... }
  frontend name { ... }
  backend name { ... }
}
```

## Table of Contents

1. [Basic Structure](#basic-structure)
2. [Global Section](#global-section)
3. [Defaults Section](#defaults-section)
4. [Frontend Section](#frontend-section)
5. [Backend Section](#backend-section)
6. [Listen Section](#listen-section)
7. [ACLs and Conditions](#acls-and-conditions)
8. [HTTP Rules](#http-rules)
9. [Stick Tables](#stick-tables)
10. [SSL/TLS Configuration](#ssltls-configuration)
11. [Health Checks](#health-checks)

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
config my_app {
  global {
    daemon: true
    maxconn: 4096
    log "/dev/log" local0 info
  }

  defaults {
    mode: http
    timeout: {
      connect: 5s
      client: 30s
      server: 30s
    }
  }

  frontend web {
    bind *:80
    default_backend: servers
  }

  backend servers {
    balance: roundrobin

    servers {
      server web1 {
        address: "192.168.1.10"
        port: 8080
        check: true
      }
    }
  }
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
config my_config {
  global {
    daemon: true
    user: "haproxy"
    group: "haproxy"
    chroot: "/var/lib/haproxy"
    pidfile: "/var/run/haproxy.pid"
    maxconn: 4096
    nbthread: 4
  }
}
```

### Logging

```haproxy
# HAProxy Native
global
    log 127.0.0.1 local0 info
    log-send-hostname myhost
    log-tag haproxy
```

```javascript
// Modern DSL
config my_config {
  global {
    log "/dev/log" local0 info
    log-send-hostname: "myhost"
    log-tag: "haproxy"
  }
}
```

### SSL/TLS Defaults

```haproxy
# HAProxy Native
global
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets
    ssl-dh-param-file /etc/haproxy/dhparam.pem
```

```javascript
// Modern DSL
config my_config {
  global {
    ssl-default-bind-ciphers: "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256"
    ssl-default-bind-ciphersuites: "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384"
    ssl-default-bind-options: ["ssl-min-ver TLSv1.2", "no-tls-tickets"]
    ssl-dh-param-file: "/etc/haproxy/dhparam.pem"
  }
}
```

### Performance Tuning

```haproxy
# HAProxy Native
global
    tune.bufsize 16384
    tune.maxrewrite 1024
    tune.ssl.cachesize 20000
    tune.http.maxhdr 101
```

```javascript
// Modern DSL
config my_config {
  global {
    tune.bufsize: 16384
    tune.maxrewrite: 1024
    tune.ssl.cachesize: 20000
    tune.http.maxhdr: 101
  }
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
```

```javascript
// Modern DSL
config my_config {
  defaults {
    timeout: {
      connect: 5s
      client: 30s
      server: 30s
      check: 5s
      http_request: 10s
    }
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
```

```javascript
// Modern DSL
config my_config {
  defaults {
    option: [
      "httplog",
      "dontlognull",
      "http-server-close",
      "forwardfor except 127.0.0.0/8"
    ]
  }
}
```

### Retries and Error Handling

```haproxy
# HAProxy Native
defaults
    retries 3
    errorloc 503 http://maintenance.example.com
```

```javascript
// Modern DSL
config my_config {
  defaults {
    retries: 3
    errorloc 503 "http://maintenance.example.com"
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
    mode http
    maxconn 10000
    default_backend webservers
```

```javascript
// Modern DSL
config my_config {
  frontend http_in {
    bind *:80
    mode: http
    maxconn: 10000
    default_backend: webservers
  }
}
```

### SSL Bind with Options

```haproxy
# HAProxy Native
frontend https
    bind *:443 ssl crt /etc/ssl/certs/site.pem alpn h2,http/1.1
```

```javascript
// Modern DSL
config my_config {
  frontend https {
    bind *:443 ssl {
      cert: "/etc/ssl/certs/site.pem"
      alpn: ["h2", "http/1.1"]
    }
  }
}
```

### Request Routing with ACLs

```haproxy
# HAProxy Native
frontend web
    bind *:80
    acl is_api path_beg /api/
    acl is_static path_beg /static/

    use_backend api_servers if is_api
    use_backend static_servers if is_static
    default_backend webservers
```

```javascript
// Modern DSL
config my_config {
  frontend web {
    bind *:80

    acl is_api {
      path_beg "/api/"
    }

    acl is_static {
      path_beg "/static/"
    }

    use_backend api_servers if is_api
    use_backend static_servers if is_static
    default_backend: webservers
  }
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
config my_config {
  backend webservers {
    mode: http
    balance: roundrobin
    option: ["httpchk GET /health"]

    servers {
      server web1 {
        address: "192.168.1.10"
        port: 8080
        check: true
        weight: 10
      }
      server web2 {
        address: "192.168.1.11"
        port: 8080
        check: true
        weight: 10
      }
      server web3 {
        address: "192.168.1.12"
        port: 8080
        check: true
        weight: 5
        backup: true
      }
    }
  }
}
```

### Advanced Server Options

```haproxy
# HAProxy Native
backend api
    server api1 10.0.1.1:8080 check inter 3s fall 3 rise 2 maxconn 100 ssl verify none
```

```javascript
// Modern DSL
config my_config {
  backend api {
    servers {
      server api1 {
        address: "10.0.1.1"
        port: 8080
        check: true
        inter: 3s
        fall: 3
        rise: 2
        maxconn: 100
        ssl: true
        verify: "none"
      }
    }
  }
}
```

### Default Server Settings

```haproxy
# HAProxy Native
backend api
    default-server check inter 3s fall 3 rise 2
    server api1 10.0.1.1:8080
    server api2 10.0.1.2:8080
```

```javascript
// Modern DSL
config my_config {
  backend api {
    default-server {
      check: true
      inter: 3s
      fall: 3
      rise: 2
    }

    servers {
      server api1 {
        address: "10.0.1.1"
        port: 8080
      }
      server api2 {
        address: "10.0.1.2"
        port: 8080
      }
    }
  }
}
```

### Server Templates for Dynamic Discovery

```haproxy
# HAProxy Native
backend dynamic
    server-template srv 1-10 _http._tcp.example.com:8080 check resolvers mydns
```

```javascript
// Modern DSL
config my_config {
  backend dynamic {
    server-template srv [1..10] {
      address: "_http._tcp.example.com"
      port: 8080
      check: true
      resolvers: "mydns"
    }
  }
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
```

```javascript
// Modern DSL
config my_config {
  listen stats {
    bind *:8404
    mode: http

    stats {
      enable: true
      uri: "/stats"
      refresh: 10s
      auth: "admin:password"
    }
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
    acl src_internal src 192.168.0.0/16 10.0.0.0/8
```

```javascript
// Modern DSL
config my_config {
  frontend web {
    acl is_api {
      path_beg "-i" "/api/"
    }

    acl is_websocket {
      hdr "Upgrade" "-i" "websocket"
    }

    acl src_internal {
      src "192.168.0.0/16" "10.0.0.0/8"
    }
  }
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
```

```javascript
// Modern DSL
config my_config {
  frontend web {
    http-request {
      deny if { path_beg /admin } !src_internal
      set-header "X-Forwarded-Proto" "https" if ssl_fc
      add-header "X-Request-ID" "%[uuid()]"
    }
  }
}
```

### HTTP Response Rules

```haproxy
# HAProxy Native
backend api
    http-response set-header X-Frame-Options DENY
    http-response del-header Server
```

```javascript
// Modern DSL
config my_config {
  backend api {
    http-response {
      set-header "X-Frame-Options" "DENY"
      del-header "Server"
    }
  }
}
```

---

## Stick Tables

```haproxy
# HAProxy Native
backend api
    stick-table type ip size 100k expire 30m store conn_cur,conn_rate(10s)
    stick on src
    stick match src
```

```javascript
// Modern DSL
config my_config {
  backend api {
    stick-table {
      type: ip
      size: 100000
      expire: 30m
      store: ["conn_cur", "conn_rate(10s)"]
    }

    stick on src
    stick match src
  }
}
```

---

## SSL/TLS Configuration

### SSL Termination

```haproxy
# HAProxy Native
frontend https
    bind *:443 ssl crt /etc/ssl/certs/combined.pem ca-file /etc/ssl/ca.pem verify optional alpn h2,http/1.1
```

```javascript
// Modern DSL
config my_config {
  frontend https {
    bind *:443 ssl {
      cert: "/etc/ssl/certs/combined.pem"
      ca-file: "/etc/ssl/ca.pem"
      verify: "optional"
      alpn: ["h2", "http/1.1"]
    }
  }
}
```

### Backend SSL

```haproxy
# HAProxy Native
backend secure-api
    server api1 10.0.1.1:443 ssl verify required ca-file /etc/ssl/ca.pem check-ssl
```

```javascript
// Modern DSL
config my_config {
  backend secure_api {
    servers {
      server api1 {
        address: "10.0.1.1"
        port: 443
        ssl: true
        verify: "required"
        ca-file: "/etc/ssl/ca.pem"
        check-ssl: true
      }
    }
  }
}
```

---

## Health Checks

### HTTP Health Checks

```haproxy
# HAProxy Native
backend api
    option httpchk
    http-check send meth GET uri /health ver HTTP/1.1 hdr Host api.example.com
    http-check expect status 200
```

```javascript
// Modern DSL
config my_config {
  backend api {
    option: ["httpchk"]

    http-check {
      send method GET uri "/health" headers {
        header "Host" "api.example.com"
      }
      expect status 200
    }
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
config my_config {
  backend redis {
    option: ["tcp-check"]

    tcp-check {
      connect
      send "PING\r\n"
      expect string "+PONG"
    }
  }
}
```

---

## Migration Tips

### 1. Always Start with the Config Wrapper
Every DSL file must have `config name { }` as the outer wrapper.

### 2. Mode Values Are Identifiers
Use `mode: http` not `mode: "http"`.

### 3. Bind Is a Directive, Not a Property
Use `bind *:80` not `bind: "*:80"`.

### 4. Servers Go in a Servers Block
```javascript
servers {
  server name {
    address: "..."
    port: 8080
  }
}
```

### 5. Use Templates for Repeated Settings
```javascript
config my_config {
  template server_defaults {
    check: true
    inter: 3s
    rise: 2
    fall: 3
  }

  backend api {
    servers {
      server api1 {
        address: "10.0.1.1"
        port: 8080
        @server_defaults
      }
    }
  }
}
```

### 6. Validate Early and Often
```bash
uv run haproxy-translate config.hap --validate
```

---

## See Also

- [Quick Start Guide](QUICK_START.md)
- [Syntax Reference](SYNTAX_REFERENCE.md)
- [Architecture Guide](ARCHITECTURE.md)
