# HAProxy Configuration Examples

This directory contains example configurations demonstrating various features of the HAProxy Configuration Translator DSL.

## Examples

### 1. Simple Load Balancer (`01-simple-loadbalancer.hap`)

**Demonstrates:**

- Basic load balancing with round-robin
- Health checks
- Multiple backend servers
- Simple frontend/backend configuration

**Use Case:** Basic HTTP load balancing across web servers

**Generate:**

```bash
haproxy-translate examples/01-simple-loadbalancer.hap -o haproxy.cfg
```

---

### 2. SSL Termination (`02-ssl-termination.hap`)

**Demonstrates:**

- SSL/TLS termination
- HTTPS to HTTP backends
- HTTP to HTTPS redirect
- SSL cipher configuration
- ALPN protocol negotiation (HTTP/2)
- Security headers
- Environment variable usage

**Use Case:** HTTPS frontend with SSL offloading

**Generate:**

```bash
# Set SSL certificate path
export SSL_CERT_PATH=/etc/haproxy/certs/mysite.pem
haproxy-translate examples/02-ssl-termination.hap -o haproxy.cfg
```

---

### 3. ACL-Based Routing (`03-acl-routing.hap`)

**Demonstrates:**

- Multiple ACL definitions
- ACL block syntax
- Path-based routing
- Header-based routing
- Security rules (authentication, IP filtering)
- Multiple backends
- Different balance algorithms
- Compression
- WebSocket support with custom timeouts

**Use Case:** Microservices architecture with different routing rules

**Generate:**

```bash
haproxy-translate examples/03-acl-routing.hap -o haproxy.cfg
```

---

### 4. Dynamic Server Scaling (`04-dynamic-scaling.hap`)

**Demonstrates:**

- Variable usage
- String interpolation
- Templates for reusable configuration
- For loops for server generation
- Server-template directive
- Environment variable configuration

**Use Case:** Auto-scaling deployment with configurable server count

**Generate:**

```bash
# Configure via environment variables
export NUM_SERVERS=20
export BASE_IP=10.0.1
export BACKEND_PORT=8080
export MAX_CONN=8192
haproxy-translate examples/04-dynamic-scaling.hap -o haproxy.cfg
```

---

### 5. Multi-Environment (`05-multi-environment.hap`)

**Demonstrates:**

- Conditional configuration (if/else)
- Environment-specific settings
- Ternary expressions
- Dynamic configuration based on environment
- Production vs staging vs development setups

**Use Case:** Single configuration file for all environments

**Generate:**

```bash
# Production
export ENVIRONMENT=production
haproxy-translate examples/05-multi-environment.hap -o haproxy-prod.cfg

# Staging
export ENVIRONMENT=staging
haproxy-translate examples/05-multi-environment.hap -o haproxy-staging.cfg

# Development
export ENVIRONMENT=development
haproxy-translate examples/05-multi-environment.hap -o haproxy-dev.cfg
```

---

## Running Examples

### Validate Configuration

Before generating, always validate:

```bash
haproxy-translate examples/01-simple-loadbalancer.hap --validate
```

### Generate with Debug Info

See what transformations are applied:

```bash
haproxy-translate examples/04-dynamic-scaling.hap --debug
```

### Watch Mode

Auto-regenerate on changes (useful during development):

```bash
haproxy-translate examples/03-acl-routing.hap -o haproxy.cfg --watch --verbose
```

### Verify with HAProxy

Always validate generated config with HAProxy:

```bash
haproxy-translate examples/02-ssl-termination.hap -o haproxy.cfg
haproxy -c -f haproxy.cfg
```

---

## Common Patterns

### Using Environment Variables

All examples support environment variable configuration:

```bash
# Set variables
export BACKEND_PORT=8080
export MAX_CONN=4096
export SSL_CERT_PATH=/etc/haproxy/certs/site.pem

# Generate configuration
haproxy-translate examples/04-dynamic-scaling.hap -o haproxy.cfg
```

### Template Reuse

Create reusable templates for common configurations:

```haproxy-dsl
template server_defaults {
    check: true
    inter: 3s
    rise: 2
    fall: 3
    maxconn: 200
}

servers {
    server web1 {
        address: "10.0.1.1"
        port: 8080
        @server_defaults  // Spread template
    }
}
```

### Dynamic Generation

Use loops for scalable configurations:

```haproxy-dsl
servers {
    for i in [1..10] {
        server "web${i}" {
            address: "10.0.1.${i}"
            port: 8080
            check: true
        }
    }
}
```

---

## Best Practices

1. **Always validate** before deploying:

   ```bash
   haproxy-translate config.hap --validate
   ```

2. **Use environment variables** for secrets and environment-specific values

3. **Use templates** to avoid repetition

4. **Use loops** for scalable configurations

5. **Test generated config** with HAProxy:

   ```bash
   haproxy -c -f haproxy.cfg
   ```

6. **Use meaningful names** for frontends, backends, and servers

7. **Comment your configuration** for maintainability

8. **Version control** your DSL files, not generated configs

---

## Advanced Examples

For more advanced patterns, see:

- **[USAGE.md](../USAGE.md)** - Comprehensive usage guide
- **[FEATURES.md](../FEATURES.md)** - Feature reference
- **[tests/](../tests/)** - Test suite with many configuration examples

---

## Need Help?

- Check the [USAGE.md](../USAGE.md) guide
- Read the [README.md](../README.md) for project overview
- Report issues at https://github.com/mattsta/haproxy-config-translator/issues
