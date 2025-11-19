// Complete Production HAProxy Configuration
// Demonstrates ALL implemented features including Phase 2 proxy directives
// 553 tests passing, 96% coverage
// NEW: redirect, errorfile, http-reuse, source, stats_socket, peers, resolvers, mailers

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

        // Runtime API (stats socket) - NEW!
        stats_socket "/var/run/haproxy.sock" {
            level: "admin"
            mode: "660"
            user: "haproxy"
            group: "haproxy"
        }

        // Lua scripts
        lua {
            load "/etc/haproxy/scripts/auth.lua"
        }
    }

    // ===== Peers Section - NEW! =====
    // For stick table replication across multiple HAProxy instances
    peers mycluster {
        peer haproxy1 "10.0.0.1" 1024
        peer haproxy2 "10.0.0.2" 1024
        peer haproxy3 "10.0.0.3" 1024
    }

    // ===== Resolvers Section - NEW! =====
    // DNS resolution for dynamic backend discovery
    resolvers mydns {
        nameserver dns1 "8.8.8.8" 53
        nameserver dns2 "8.8.4.4" 53
        timeout_resolve: 1s
        timeout_retry: 1s
        hold_valid: 10s
    }

    // ===== Mailers Section - NEW! =====
    // Email alerts for backend failures
    mailers alerts {
        timeout_mail: 10s
        mailer smtp1 "smtp.example.com" 587
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
            http_request: 10s
            http_keep_alive: 10s
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

        // Custom error pages - NEW!
        errorfile 400 "/etc/haproxy/errors/400.html"
        errorfile 403 "/etc/haproxy/errors/403.html"
        errorfile 404 "/etc/haproxy/errors/404.html"
        errorfile 500 "/etc/haproxy/errors/500.html"
        errorfile 502 "/etc/haproxy/errors/502.html"
        errorfile 503 "/etc/haproxy/errors/503.html"

        // ACLs for routing
        acl {
            is_api path_beg "/api"
            is_static path_beg "/static"
            is_websocket hdr_sub "Upgrade" "websocket"
        }

        // HTTPS redirect for non-SSL traffic - NEW!
        redirect scheme "https" code 301

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

        // Connection pooling for performance - NEW!
        http-reuse: safe

        // Source IP binding for outbound connections - NEW!
        source: "10.0.0.100:0"

        // Custom backend error page - NEW!
        errorfile 503 "/etc/haproxy/errors/503-api.html"

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
            type: string
            size: 100000
            expire: 30m
        }

        // Stick rules
        stick store-request hdr(X-Session-ID)
        stick match hdr(X-Session-ID)

        // HTTP request rules
        http-request {
            set_header "X-Forwarded-Proto" "https"
            del_header "X-Powered-By"
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

        // Aggressive connection reuse for web traffic - NEW!
        http-reuse: aggressive

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
