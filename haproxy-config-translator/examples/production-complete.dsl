// Complete Production HAProxy Configuration
// Demonstrates ALL implemented features
// 281 tests passing, 89% coverage

config production_complete {
    // ===== Global Section =====
    global {
        daemon: true
        maxconn: 50000

        // Performance tuning
        nbthread: 16
        maxsslconn: 25000
        ulimit-n: 200000

        // User/group
        user: "haproxy"
        group: "haproxy"

        // Logging
        log "/dev/log" local0 info

        // SSL/TLS hardening
        ssl-default-bind-ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
        ssl-default-bind-options: ["no-sslv3", "no-tlsv10", "no-tlsv11", "no-tls-tickets"]

        // Lua scripts
        lua {
            load "/etc/haproxy/scripts/auth.lua"
        }
    }

    // ===== Defaults Section =====
    defaults {
        mode: http
        retries: 3
        option: [
            "httplog",
            "dontlognull",
            "http-server-close",
            "forwardfor",
            "redispatch"
        ]

        timeout: {
            connect: 5s
            client: 50s
            server: 50s
            http-request: 10s
            http-keep-alive: 10s
            check: 5s
        }
    }

    // ===== Frontend: HTTPS Termination =====
    frontend web_https {
        bind *:80
        bind *:443 ssl {
            cert: "/etc/ssl/certs/production.pem"
            alpn: ["h2", "http/1.1"]
            ssl-min-ver: "TLSv1.2"
            ssl-max-ver: "TLSv1.3"
            ciphers: "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
            curves: "secp384r1:prime256v1"
            no-sslv3: true
            no-tlsv10: true
            no-tlsv11: true
        }

        option: ["httplog", "forwardfor", "http-server-close"]

        // ACLs for routing
        acl {
            is_api path_beg "/api"
            is_static path_beg "/static" path_end ".css" ".js" ".png" ".jpg"
            is_websocket hdr(Upgrade) -i WebSocket
        }

        // Routing rules
        route {
            to api_backend if is_api
            to static_backend if is_static
            to websocket_backend if is_websocket
            default: web_backend
        }

        // Timeouts
        timeout_client: 60s
        timeout_http_request: 15s
        timeout_http_keep_alive: 15s
    }

    // ===== Backend: API Servers =====
    backend api_backend {
        balance: leastconn
        option: ["httplog", "forwardfor", "httpchk"]

        // Default server settings (eliminates duplication!)
        default-server {
            check: true
            inter: 5s
            rise: 2
            fall: 3
            weight: 100
            maxconn: 500
            slowstart: 30s
            send-proxy-v2: true
        }

        // Health check
        health-check {
            method: "GET"
            uri: "/api/health"
            expect: status 200
        }

        // Stick table for session persistence
        stick-table {
            type: "string"
            size: 100000
            expire: 30m
        }

        // Stick rules
        stick store-request hdr(X-Session-ID)
        stick match hdr(X-Session-ID)

        // HTTP request rules
        http-request {
            set-header X-Forwarded-Proto https
            del-header X-Powered-By
        }

        // TCP request rules
        tcp-request {
            inspect-delay timeout 5s
            connection accept
            content accept
        }

        // Servers (inherit all default-server settings)
        servers {
            server api1 {
                address: "10.0.1.1"
                port: 8080
            }
            server api2 {
                address: "10.0.1.2"
                port: 8080
            }
            server api3 {
                address: "10.0.1.3"
                port: 8080
            }
            server api4 {
                address: "10.0.1.4"
                port: 8080
            }
            server api5 {
                address: "10.0.1.5"
                port: 8080
            }
        }

        timeout_server: 60s
        timeout_connect: 5s
        timeout_check: 3s
    }

    // ===== Backend: Web Servers =====
    backend web_backend {
        balance: roundrobin
        option: ["httplog", "forwardfor", "httpchk"]

        default-server {
            check: true
            inter: 5s
            rise: 2
            fall: 3
            weight: 100
        }

        health-check {
            method: "HEAD"
            uri: "/health"
            expect: status 200
        }

        servers {
            server web1 {
                address: "10.0.2.1"
                port: 8080
            }
            server web2 {
                address: "10.0.2.2"
                port: 8080
            }
            server web3 {
                address: "10.0.2.3"
                port: 8080
            }
        }
    }

    // ===== Backend: Static Content (CDN) =====
    backend static_backend {
        balance: roundrobin
        option: ["httplog"]

        // Compression for static assets
        compression {
            algo: "gzip"
            type: ["text/html", "text/css", "text/javascript", "application/json"]
        }

        default-server {
            check: true
            inter: 10s
            rise: 2
            fall: 2
        }

        servers {
            server cdn1 {
                address: "10.0.3.1"
                port: 8080
            }
            server cdn2 {
                address: "10.0.3.2"
                port: 8080
            }
        }
    }

    // ===== Backend: WebSocket Servers =====
    backend websocket_backend {
        balance: source
        option: ["tcplog"]

        default-server {
            check: true
            inter: 5s
        }

        servers {
            server ws1 {
                address: "10.0.4.1"
                port: 8080
            }
            server ws2 {
                address: "10.0.4.2"
                port: 8080
            }
        }

        timeout_server: 3600s
    }
}
