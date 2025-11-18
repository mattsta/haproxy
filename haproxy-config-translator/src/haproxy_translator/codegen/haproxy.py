"""HAProxy native configuration code generator."""

import dataclasses
from pathlib import Path

from ..ir.nodes import (
    ACL,
    Backend,
    Bind,
    ConfigIR,
    DefaultsConfig,
    DefaultServer,
    Frontend,
    GlobalConfig,
    HealthCheck,
    HttpRequestRule,
    HttpResponseRule,
    Listen,
    Server,
    ServerTemplate,
    StickRule,
    StickTable,
    TcpRequestRule,
    TcpResponseRule,
)


class HAProxyCodeGenerator:
    """Generate native HAProxy configuration from IR."""

    def __init__(self, indent: str = "    "):
        self.indent_str = indent
        self.lua_files: list[str] = []

    def generate(self, ir: ConfigIR, output_path: Path | None = None) -> str:
        """
        Generate complete HAProxy configuration.

        Args:
            ir: Configuration IR
            output_path: Optional output file path

        Returns:
            Generated configuration as string
        """
        lines = []

        # Header comment
        lines.append(f"# Generated HAProxy configuration: {ir.name}")
        lines.append(f"# Version: {ir.version}")
        lines.append("")

        # Merge top-level lua_scripts into global config (HAProxy requires lua-load in global section)
        global_config = ir.global_config
        if ir.lua_scripts and len(ir.lua_scripts) > 0:
            if global_config:
                # Add top-level lua scripts to global config's lua_scripts
                all_lua_scripts = list(ir.lua_scripts) + list(global_config.lua_scripts)
                global_config = dataclasses.replace(global_config, lua_scripts=all_lua_scripts)
            else:
                # Create a minimal global config with just lua scripts
                global_config = GlobalConfig(lua_scripts=list(ir.lua_scripts))

        # Generate global section
        if global_config:
            lines.extend(self._generate_global(global_config))
            lines.append("")

        # Generate defaults section
        if ir.defaults:
            lines.extend(self._generate_defaults(ir.defaults))
            lines.append("")

        # Generate frontends
        for frontend in ir.frontends:
            lines.extend(self._generate_frontend(frontend))
            lines.append("")

        # Generate backends
        for backend in ir.backends:
            lines.extend(self._generate_backend(backend))
            lines.append("")

        # Generate listens
        for listen in ir.listens:
            lines.extend(self._generate_listen(listen))
            lines.append("")

        config = "\n".join(lines)

        # Write to file if output_path specified
        if output_path:
            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(config, encoding="utf-8")

        return config

    def _generate_global(self, global_config: GlobalConfig) -> list[str]:
        """Generate global section."""
        lines = ["global"]

        if global_config.daemon:
            lines.append(self._indent("daemon"))

        lines.append(self._indent(f"maxconn {global_config.maxconn}"))

        # Process control
        if global_config.nbproc:
            lines.append(self._indent(f"nbproc {global_config.nbproc}"))

        # Rate limiting
        if global_config.maxconnrate:
            lines.append(self._indent(f"maxconnrate {global_config.maxconnrate}"))

        if global_config.maxsslrate:
            lines.append(self._indent(f"maxsslrate {global_config.maxsslrate}"))

        if global_config.maxsessrate:
            lines.append(self._indent(f"maxsessrate {global_config.maxsessrate}"))

        if global_config.user:
            lines.append(self._indent(f"user {global_config.user}"))

        if global_config.group:
            lines.append(self._indent(f"group {global_config.group}"))

        if global_config.uid is not None:
            lines.append(self._indent(f"uid {global_config.uid}"))

        if global_config.gid is not None:
            lines.append(self._indent(f"gid {global_config.gid}"))

        if global_config.chroot:
            lines.append(self._indent(f"chroot {global_config.chroot}"))

        if global_config.pidfile:
            lines.append(self._indent(f"pidfile {global_config.pidfile}"))

        if global_config.node:
            lines.append(self._indent(f"node {global_config.node}"))

        if global_config.description:
            lines.append(self._indent(f"description {global_config.description}"))

        if global_config.hard_stop_after:
            lines.append(self._indent(f"hard-stop-after {global_config.hard_stop_after}"))

        if global_config.external_check is not None:
            if global_config.external_check:
                lines.append(self._indent("external-check"))

        # Connection tuning
        if global_config.maxpipes:
            lines.append(self._indent(f"maxpipes {global_config.maxpipes}"))

        # Master-worker mode
        if global_config.master_worker is not None:
            if global_config.master_worker:
                lines.append(self._indent("master-worker"))

        if global_config.mworker_max_reloads:
            lines.append(self._indent(f"mworker-max-reloads {global_config.mworker_max_reloads}"))

        # SSL/TLS base paths
        if global_config.ca_base:
            lines.append(self._indent(f"ca-base {global_config.ca_base}"))

        if global_config.crt_base:
            lines.append(self._indent(f"crt-base {global_config.crt_base}"))

        if global_config.key_base:
            lines.append(self._indent(f"key-base {global_config.key_base}"))

        # Performance tuning (basic)
        if "nbthread" in global_config.tuning:
            lines.append(self._indent(f"nbthread {global_config.tuning['nbthread']}"))

        if "maxsslconn" in global_config.tuning:
            lines.append(self._indent(f"maxsslconn {global_config.tuning['maxsslconn']}"))

        if "ulimit_n" in global_config.tuning:
            lines.append(self._indent(f"ulimit-n {global_config.tuning['ulimit_n']}"))

        # Performance tuning (tune.* directives)
        for tune_key, tune_value in sorted(global_config.tuning.items()):
            if tune_key not in ("nbthread", "maxsslconn", "ulimit_n"):
                # Keys already in HAProxy format from transformer
                lines.append(self._indent(f"{tune_key} {tune_value}"))

        # Environment variables
        for var_name, var_value in global_config.env_vars.items():
            lines.append(self._indent(f"setenv {var_name} {var_value}"))

        for var_name in global_config.reset_env_vars:
            lines.append(self._indent(f"resetenv {var_name}"))

        for var_name in global_config.unset_env_vars:
            lines.append(self._indent(f"unsetenv {var_name}"))

        # System configuration (Phase 3)
        if global_config.setcap:
            lines.append(self._indent(f"setcap {global_config.setcap}"))

        if global_config.set_dumpable is not None:
            lines.append(self._indent(f"set-dumpable"))

        if global_config.unix_bind:
            lines.append(self._indent(f"unix-bind {global_config.unix_bind}"))

        for process_thread, cpu_list in global_config.cpu_map.items():
            lines.append(self._indent(f"cpu-map {process_thread} {cpu_list}"))

        # Performance & Runtime (Phase 4A)
        if global_config.busy_polling is not None:
            if global_config.busy_polling:
                lines.append(self._indent("busy-polling"))

        if global_config.max_spread_checks is not None:
            lines.append(self._indent(f"max-spread-checks {global_config.max_spread_checks}"))

        if global_config.spread_checks is not None:
            lines.append(self._indent(f"spread-checks {global_config.spread_checks}"))

        if global_config.maxcompcpuusage is not None:
            lines.append(self._indent(f"maxcompcpuusage {global_config.maxcompcpuusage}"))

        if global_config.maxcomprate is not None:
            lines.append(self._indent(f"maxcomprate {global_config.maxcomprate}"))

        if global_config.default_path:
            lines.append(self._indent(f"default-path {global_config.default_path}"))

        # HTTP Client Configuration (Phase 4B Part 1)
        if global_config.httpclient_resolvers_disabled is not None:
            if global_config.httpclient_resolvers_disabled:
                lines.append(self._indent("httpclient.resolvers.disabled"))

        if global_config.httpclient_resolvers_id:
            lines.append(self._indent(f"httpclient.resolvers.id {global_config.httpclient_resolvers_id}"))

        if global_config.httpclient_resolvers_prefer:
            lines.append(self._indent(f"httpclient.resolvers.prefer {global_config.httpclient_resolvers_prefer}"))

        if global_config.httpclient_retries is not None:
            lines.append(self._indent(f"httpclient.retries {global_config.httpclient_retries}"))

        if global_config.httpclient_ssl_verify:
            lines.append(self._indent(f"httpclient.ssl.verify {global_config.httpclient_ssl_verify}"))

        if global_config.httpclient_ssl_ca_file:
            lines.append(self._indent(f"httpclient.ssl.ca-file {global_config.httpclient_ssl_ca_file}"))

        # Platform-Specific Options (Phase 4B Part 1)
        if global_config.noepoll is not None:
            if global_config.noepoll:
                lines.append(self._indent("noepoll"))

        if global_config.nokqueue is not None:
            if global_config.nokqueue:
                lines.append(self._indent("nokqueue"))

        if global_config.nopoll is not None:
            if global_config.nopoll:
                lines.append(self._indent("nopoll"))

        if global_config.nosplice is not None:
            if global_config.nosplice:
                lines.append(self._indent("nosplice"))

        if global_config.nogetaddrinfo is not None:
            if global_config.nogetaddrinfo:
                lines.append(self._indent("nogetaddrinfo"))

        if global_config.noreuseport is not None:
            if global_config.noreuseport:
                lines.append(self._indent("noreuseport"))

        if global_config.limited_quic is not None:
            if global_config.limited_quic:
                lines.append(self._indent("limited-quic"))

        if global_config.localpeer:
            lines.append(self._indent(f"localpeer {global_config.localpeer}"))

        # SSL Advanced (Phase 4B Part 2)
        if global_config.ssl_load_extra_files:
            lines.append(self._indent(f"ssl-load-extra-files {global_config.ssl_load_extra_files}"))

        if global_config.ssl_load_extra_del_ext:
            lines.append(self._indent(f"ssl-load-extra-del-ext {global_config.ssl_load_extra_del_ext}"))

        if global_config.ssl_mode_async is not None:
            if global_config.ssl_mode_async:
                lines.append(self._indent("ssl-mode-async"))

        if global_config.ssl_propquery:
            lines.append(self._indent(f"ssl-propquery {global_config.ssl_propquery}"))

        if global_config.ssl_provider:
            lines.append(self._indent(f"ssl-provider {global_config.ssl_provider}"))

        if global_config.ssl_provider_path:
            lines.append(self._indent(f"ssl-provider-path {global_config.ssl_provider_path}"))

        if global_config.issuers_chain_path:
            lines.append(self._indent(f"issuers-chain-path {global_config.issuers_chain_path}"))

        # Profiling & Debugging (Phase 4B Part 2)
        if global_config.profiling_tasks_on is not None:
            if global_config.profiling_tasks_on:
                lines.append(self._indent("profiling.tasks.on"))

        if global_config.profiling_tasks_automatic is not None:
            if global_config.profiling_tasks_automatic:
                lines.append(self._indent("profiling.tasks.automatic"))

        if global_config.profiling_memory_on is not None:
            if global_config.profiling_memory_on:
                lines.append(self._indent("profiling.memory.on"))

        # Device Detection - DeviceAtlas (Phase 4B Part 4)
        if global_config.deviceatlas_json_file:
            lines.append(self._indent(f"deviceatlas-json-file {global_config.deviceatlas_json_file}"))

        if global_config.deviceatlas_log_level is not None:
            lines.append(self._indent(f"deviceatlas-log-level {global_config.deviceatlas_log_level}"))

        if global_config.deviceatlas_separator:
            lines.append(self._indent(f"deviceatlas-separator {global_config.deviceatlas_separator}"))

        if global_config.deviceatlas_properties_cookie:
            lines.append(self._indent(f"deviceatlas-properties-cookie {global_config.deviceatlas_properties_cookie}"))

        # Device Detection - 51Degrees (Phase 4B Part 4)
        if global_config.fiftyone_degrees_data_file:
            lines.append(self._indent(f"51degrees-data-file {global_config.fiftyone_degrees_data_file}"))

        if global_config.fiftyone_degrees_property_name_list:
            lines.append(self._indent(f"51degrees-property-name-list {global_config.fiftyone_degrees_property_name_list}"))

        if global_config.fiftyone_degrees_property_separator:
            lines.append(self._indent(f"51degrees-property-separator {global_config.fiftyone_degrees_property_separator}"))

        if global_config.fiftyone_degrees_cache_size is not None:
            lines.append(self._indent(f"51degrees-cache-size {global_config.fiftyone_degrees_cache_size}"))

        # Device Detection - WURFL (Phase 4B Part 4)
        if global_config.wurfl_data_file:
            lines.append(self._indent(f"wurfl-data-file {global_config.wurfl_data_file}"))

        if global_config.wurfl_information_list:
            lines.append(self._indent(f"wurfl-information-list {global_config.wurfl_information_list}"))

        if global_config.wurfl_information_list_separator:
            lines.append(self._indent(f"wurfl-information-list-separator {global_config.wurfl_information_list_separator}"))

        if global_config.wurfl_patch_file:
            lines.append(self._indent(f"wurfl-patch-file {global_config.wurfl_patch_file}"))

        if global_config.wurfl_cache_size is not None:
            lines.append(self._indent(f"wurfl-cache-size {global_config.wurfl_cache_size}"))

        if global_config.wurfl_engine_mode:
            lines.append(self._indent(f"wurfl-engine-mode {global_config.wurfl_engine_mode}"))

        if global_config.wurfl_useragent_priority:
            lines.append(self._indent(f"wurfl-useragent-priority {global_config.wurfl_useragent_priority}"))

        # Logging configuration
        if global_config.log_tag:
            lines.append(self._indent(f"log-tag {global_config.log_tag}"))

        if global_config.log_send_hostname:
            lines.append(self._indent(f"log-send-hostname {global_config.log_send_hostname}"))

        # Log targets
        for log in global_config.log_targets:
            log_line = f"log {log.address} {log.facility.value} {log.level.value}"
            if log.minlevel:
                log_line += f" {log.minlevel.value}"
            lines.append(self._indent(log_line))

        # SSL configuration
        if global_config.ssl_dh_param_file:
            lines.append(self._indent(f"ssl-dh-param-file {global_config.ssl_dh_param_file}"))

        if global_config.ssl_default_bind_ciphers:
            lines.append(
                self._indent(f"ssl-default-bind-ciphers {global_config.ssl_default_bind_ciphers}")
            )

        if global_config.ssl_default_bind_ciphersuites:
            lines.append(
                self._indent(f"ssl-default-bind-ciphersuites {global_config.ssl_default_bind_ciphersuites}")
            )

        for option in global_config.ssl_default_bind_options:
            lines.append(self._indent(f"ssl-default-bind-options {option}"))

        if global_config.ssl_default_server_ciphers:
            lines.append(
                self._indent(f"ssl-default-server-ciphers {global_config.ssl_default_server_ciphers}")
            )

        if global_config.ssl_default_server_ciphersuites:
            lines.append(
                self._indent(f"ssl-default-server-ciphersuites {global_config.ssl_default_server_ciphersuites}")
            )

        for option in global_config.ssl_default_server_options:
            lines.append(self._indent(f"ssl-default-server-options {option}"))

        if global_config.ssl_server_verify:
            lines.append(self._indent(f"ssl-server-verify {global_config.ssl_server_verify}"))

        if global_config.ssl_engine:
            lines.append(self._indent(f"ssl-engine {global_config.ssl_engine}"))

        # Lua scripts
        for script in global_config.lua_scripts:
            if script.source_type == "file":
                lines.append(self._indent(f"lua-load {script.content}"))
                self.lua_files.append(script.content)

        # Stats
        if global_config.stats and global_config.stats.enable:
            lines.append(self._indent("stats socket /var/run/haproxy.sock mode 660 level admin"))

        # Tuning
        for key, value in global_config.tuning.items():
            lines.append(self._indent(f"{key} {value}"))

        return lines

    def _generate_defaults(self, defaults: DefaultsConfig) -> list[str]:
        """Generate defaults section."""
        lines = ["defaults"]

        lines.append(self._indent(f"mode {defaults.mode.value}"))

        if defaults.log:
            lines.append(self._indent(f"log {defaults.log}"))

        lines.append(self._indent(f"retries {defaults.retries}"))

        # Timeouts
        lines.append(self._indent(f"timeout connect {defaults.timeout_connect}"))
        lines.append(self._indent(f"timeout client {defaults.timeout_client}"))
        lines.append(self._indent(f"timeout server {defaults.timeout_server}"))

        if defaults.timeout_check:
            lines.append(self._indent(f"timeout check {defaults.timeout_check}"))

        if defaults.timeout_queue:
            lines.append(self._indent(f"timeout queue {defaults.timeout_queue}"))

        if defaults.timeout_http_request:
            lines.append(self._indent(f"timeout http-request {defaults.timeout_http_request}"))

        if defaults.timeout_http_keep_alive:
            lines.append(self._indent(f"timeout http-keep-alive {defaults.timeout_http_keep_alive}"))

        if defaults.timeout_tunnel:
            lines.append(self._indent(f"timeout tunnel {defaults.timeout_tunnel}"))

        if defaults.timeout_client_fin:
            lines.append(self._indent(f"timeout client-fin {defaults.timeout_client_fin}"))

        if defaults.timeout_server_fin:
            lines.append(self._indent(f"timeout server-fin {defaults.timeout_server_fin}"))

        if defaults.timeout_tarpit:
            lines.append(self._indent(f"timeout tarpit {defaults.timeout_tarpit}"))

        # Options
        for option in defaults.options:
            lines.append(self._indent(f"option {option}"))

        # Error files
        for code, file in defaults.errorfiles.items():
            lines.append(self._indent(f"errorfile {code} {file}"))

        # Error redirects
        for code, url in defaults.errorloc.items():
            lines.append(self._indent(f"errorloc {code} {url}"))

        for code, url in defaults.errorloc302.items():
            lines.append(self._indent(f"errorloc302 {code} {url}"))

        for code, url in defaults.errorloc303.items():
            lines.append(self._indent(f"errorloc303 {code} {url}"))

        # HTTP check
        if defaults.http_check:
            lines.extend(self._generate_http_check(defaults.http_check, indent=True))

        return lines

    def _generate_frontend(self, frontend: Frontend) -> list[str]:
        """Generate frontend section."""
        lines = [f"frontend {frontend.name}"]

        # Bind directives
        for bind in frontend.binds:
            lines.append(self._indent(self._format_bind(bind)))

        # Mode
        lines.append(self._indent(f"mode {frontend.mode.value}"))

        # Max connections
        if frontend.maxconn:
            lines.append(self._indent(f"maxconn {frontend.maxconn}"))

        # Timeout
        if frontend.timeout_client:
            lines.append(self._indent(f"timeout client {frontend.timeout_client}"))

        if frontend.timeout_http_request:
            lines.append(self._indent(f"timeout http-request {frontend.timeout_http_request}"))

        if frontend.timeout_http_keep_alive:
            lines.append(self._indent(f"timeout http-keep-alive {frontend.timeout_http_keep_alive}"))

        if frontend.timeout_client_fin:
            lines.append(self._indent(f"timeout client-fin {frontend.timeout_client_fin}"))

        if frontend.timeout_tarpit:
            lines.append(self._indent(f"timeout tarpit {frontend.timeout_tarpit}"))

        # Monitor URI
        if frontend.monitor_uri:
            lines.append(self._indent(f"monitor-uri {frontend.monitor_uri}"))

        # Log format
        if frontend.log_format:
            lines.append(self._indent(f"log-format {frontend.log_format}"))

        # Capture headers
        for header_name, length in frontend.capture_request_headers:
            lines.append(self._indent(f"capture request header {header_name} len {length}"))

        for header_name, length in frontend.capture_response_headers:
            lines.append(self._indent(f"capture response header {header_name} len {length}"))

        # ACLs
        for acl in frontend.acls:
            lines.append(self._indent(self._format_acl(acl)))

        # Stick table
        if frontend.stick_table:
            lines.append(self._indent(self._format_stick_table(frontend.stick_table)))

        # Stick rules
        for stick_rule in frontend.stick_rules:
            lines.append(self._indent(self._format_stick_rule(stick_rule)))

        # TCP request rules
        for tcp_req in frontend.tcp_request_rules:
            lines.append(self._indent(self._format_tcp_request_rule(tcp_req)))

        # TCP response rules
        for tcp_resp in frontend.tcp_response_rules:
            lines.append(self._indent(self._format_tcp_response_rule(tcp_resp)))

        # HTTP request rules
        for req_rule in frontend.http_request_rules:
            lines.append(self._indent(self._format_http_request_rule(req_rule)))

        # HTTP response rules
        for resp_rule in frontend.http_response_rules:
            lines.append(self._indent(self._format_http_response_rule(resp_rule)))

        # Use backend rules
        for backend_rule in frontend.use_backend_rules:
            use_line = f"use_backend {backend_rule.backend}"
            if backend_rule.condition:
                use_line += f" if {backend_rule.condition}"
            lines.append(self._indent(use_line))

        # Default backend
        if frontend.default_backend:
            lines.append(self._indent(f"default_backend {frontend.default_backend}"))

        # Options
        for option in frontend.options:
            lines.append(self._indent(f"option {option}"))

        return lines

    def _generate_backend(self, backend: Backend) -> list[str]:
        """Generate backend section."""
        lines = [f"backend {backend.name}"]

        # Mode
        lines.append(self._indent(f"mode {backend.mode.value}"))

        # Balance algorithm
        lines.append(self._indent(f"balance {backend.balance.value}"))

        # Retries
        if backend.retries is not None:
            lines.append(self._indent(f"retries {backend.retries}"))

        # Timeouts
        if backend.timeout_connect:
            lines.append(self._indent(f"timeout connect {backend.timeout_connect}"))

        if backend.timeout_server:
            lines.append(self._indent(f"timeout server {backend.timeout_server}"))

        if backend.timeout_check:
            lines.append(self._indent(f"timeout check {backend.timeout_check}"))

        if backend.timeout_tunnel:
            lines.append(self._indent(f"timeout tunnel {backend.timeout_tunnel}"))

        if backend.timeout_server_fin:
            lines.append(self._indent(f"timeout server-fin {backend.timeout_server_fin}"))

        # Options
        for option in backend.options:
            lines.append(self._indent(f"option {option}"))

        # Log format
        if backend.log_format:
            lines.append(self._indent(f"log-format {backend.log_format}"))

        # ACLs
        for acl in backend.acls:
            lines.append(self._indent(self._format_acl(acl)))

        # Stick table
        if backend.stick_table:
            lines.append(self._indent(self._format_stick_table(backend.stick_table)))

        # Stick rules
        for stick_rule in backend.stick_rules:
            lines.append(self._indent(self._format_stick_rule(stick_rule)))

        # Cookie
        if backend.cookie:
            lines.append(self._indent(f"cookie {backend.cookie}"))

        # Health check
        if backend.health_check:
            lines.extend(self._generate_http_check(backend.health_check, indent=True))

        # TCP request rules
        for tcp_req in backend.tcp_request_rules:
            lines.append(self._indent(self._format_tcp_request_rule(tcp_req)))

        # TCP response rules
        for tcp_resp in backend.tcp_response_rules:
            lines.append(self._indent(self._format_tcp_response_rule(tcp_resp)))

        # HTTP request rules
        for req_rule in backend.http_request_rules:
            lines.append(self._indent(self._format_http_request_rule(req_rule)))

        # HTTP response rules
        for resp_rule in backend.http_response_rules:
            lines.append(self._indent(self._format_http_response_rule(resp_rule)))

        # Compression
        if backend.compression:
            lines.append(self._indent(f"compression algo {backend.compression.algo}"))
            if backend.compression.types:
                types_str = " ".join(backend.compression.types)
                lines.append(self._indent(f"compression type {types_str}"))

        # Default server
        if backend.default_server:
            lines.append(self._indent(self._format_default_server(backend.default_server)))

        # Servers
        for server in backend.servers:
            lines.append(self._indent(self._format_server(server)))

        # Server templates
        for template in backend.server_templates:
            lines.append(self._indent(self._format_server_template(template)))

        return lines

    def _generate_listen(self, listen: Listen) -> list[str]:
        """Generate listen section (combined frontend/backend)."""
        lines = [f"listen {listen.name}"]

        # Bind directives
        for bind in listen.binds:
            lines.append(self._indent(self._format_bind(bind)))

        # Mode
        lines.append(self._indent(f"mode {listen.mode.value}"))

        # Balance
        lines.append(self._indent(f"balance {listen.balance.value}"))

        # ACLs
        for acl in listen.acls:
            lines.append(self._indent(self._format_acl(acl)))

        # Options
        for option in listen.options:
            lines.append(self._indent(f"option {option}"))

        # Servers
        for server in listen.servers:
            lines.append(self._indent(self._format_server(server)))

        return lines

    def _generate_http_check(self, health_check: HealthCheck, indent: bool = False) -> list[str]:
        """Generate HTTP health check directives."""
        lines = []
        ind = self._indent if indent else lambda x: x

        check_line = f"http-check send meth {health_check.method} uri {health_check.uri}"

        # Add headers
        for name, value in health_check.headers.items():
            check_line += f' hdr {name} "{value}"'

        lines.append(ind(check_line))

        # Expect - build the expectation line
        negate_prefix = "! " if health_check.expect_negate else ""

        if health_check.expect_status:
            lines.append(ind(f"http-check expect {negate_prefix}status {health_check.expect_status}"))
        elif health_check.expect_string:
            lines.append(ind(f"http-check expect {negate_prefix}string {health_check.expect_string}"))
        elif health_check.expect_rstatus:
            lines.append(ind(f"http-check expect {negate_prefix}rstatus {health_check.expect_rstatus}"))
        elif health_check.expect_rstring:
            lines.append(ind(f"http-check expect {negate_prefix}rstring {health_check.expect_rstring}"))

        return lines

    def _format_bind(self, bind: Bind) -> str:
        """Format bind directive."""
        parts = [f"bind {bind.address}"]

        if bind.ssl:
            parts.append("ssl")
            if bind.ssl_cert:
                parts.append(f"crt {bind.ssl_cert}")
            if bind.alpn:
                parts.append(f"alpn {','.join(bind.alpn)}")

        for key, value in bind.options.items():
            if isinstance(value, bool) and value:
                parts.append(key)
            elif value:
                parts.append(f"{key} {value}")

        return " ".join(parts)

    def _format_acl(self, acl: ACL) -> str:
        """Format ACL definition."""
        parts = [f"acl {acl.name} {acl.criterion}"]

        if acl.flags:
            parts.extend(acl.flags)

        if acl.values:
            parts.extend(acl.values)

        return " ".join(parts)

    def _format_http_request_rule(self, rule: HttpRequestRule) -> str:
        """Format HTTP request rule."""
        # Convert underscores to hyphens in action name for HAProxy syntax
        haproxy_action = rule.action.replace("_", "-")
        parts = [f"http-request {haproxy_action}"]

        for key, value in rule.parameters.items():
            # Convert underscores to hyphens for HAProxy syntax
            haproxy_key = key.replace("_", "-")

            if key in ["header", "name"]:
                parts.append(value)
            elif key == "status":
                parts.append(f"status {value}")
            elif key == "deny_status":
                parts.append(f"deny status {value}")
            elif isinstance(value, str) and " " in value:
                parts.append(f'{haproxy_key} "{value}"')
            else:
                parts.append(f"{haproxy_key} {value}")

        if rule.condition:
            parts.append(f"if {rule.condition}")

        return " ".join(parts)

    def _format_http_response_rule(self, rule: HttpResponseRule) -> str:
        """Format HTTP response rule."""
        # Convert underscores to hyphens in action name for HAProxy syntax
        haproxy_action = rule.action.replace("_", "-")
        parts = [f"http-response {haproxy_action}"]

        for key, value in rule.parameters.items():
            # Convert underscores to hyphens for HAProxy syntax
            haproxy_key = key.replace("_", "-")

            if isinstance(value, str) and " " in value:
                parts.append(f'{haproxy_key} "{value}"')
            else:
                parts.append(f"{haproxy_key} {value}")

        if rule.condition:
            parts.append(f"if {rule.condition}")

        return " ".join(parts)

    def _format_default_server(self, default_server: "DefaultServer") -> str:
        """Format default-server directive."""
        parts = ["default-server"]

        if default_server.check:
            parts.append("check")
            if default_server.check_interval:
                parts.append(f"inter {default_server.check_interval}")
            if default_server.rise:
                parts.append(f"rise {default_server.rise}")
            if default_server.fall:
                parts.append(f"fall {default_server.fall}")

        if default_server.weight:
            parts.append(f"weight {default_server.weight}")

        if default_server.maxconn:
            parts.append(f"maxconn {default_server.maxconn}")

        if default_server.ssl:
            parts.append("ssl")
            if default_server.ssl_verify:
                parts.append(f"verify {default_server.ssl_verify}")
            if default_server.sni:
                parts.append(f"sni {default_server.sni}")
            if default_server.alpn:
                alpn_str = ",".join(default_server.alpn)
                parts.append(f"alpn {alpn_str}")

        if default_server.send_proxy:
            parts.append("send-proxy")

        if default_server.send_proxy_v2:
            parts.append("send-proxy-v2")

        if default_server.slowstart:
            parts.append(f"slowstart {default_server.slowstart}")

        # SSL/TLS health check options
        if default_server.check_ssl:
            parts.append("check-ssl")

        if default_server.check_sni:
            parts.append(f"check-sni {default_server.check_sni}")

        # SSL/TLS version constraints
        if default_server.ssl_min_ver:
            parts.append(f"ssl-min-ver {default_server.ssl_min_ver}")

        if default_server.ssl_max_ver:
            parts.append(f"ssl-max-ver {default_server.ssl_max_ver}")

        # Server certificate options
        if default_server.ca_file:
            parts.append(f"ca-file {default_server.ca_file}")

        if default_server.crt:
            parts.append(f"crt {default_server.crt}")

        # Source IP binding
        if default_server.source:
            parts.append(f"source {default_server.source}")

        return " ".join(parts)

    def _format_server(self, server: Server) -> str:
        """Format server definition."""
        parts = [f"server {server.name} {server.address}:{server.port}"]

        if server.check:
            parts.append("check")
            if server.check_interval:
                parts.append(f"inter {server.check_interval}")
            parts.append(f"rise {server.rise}")
            parts.append(f"fall {server.fall}")

        if server.weight != 1:
            parts.append(f"weight {server.weight}")

        if server.maxconn:
            parts.append(f"maxconn {server.maxconn}")

        if server.ssl:
            parts.append("ssl")
            if server.ssl_verify:
                parts.append(f"verify {server.ssl_verify}")
            if server.sni:
                parts.append(f"sni {server.sni}")
            if server.alpn:
                alpn_str = ",".join(server.alpn)
                parts.append(f"alpn {alpn_str}")

        if server.backup:
            parts.append("backup")

        if server.disabled:
            parts.append("disabled")

        if server.send_proxy:
            parts.append("send-proxy")

        if server.send_proxy_v2:
            parts.append("send-proxy-v2")

        if server.slowstart:
            parts.append(f"slowstart {server.slowstart}")

        # SSL/TLS health check options
        if server.check_ssl:
            parts.append("check-ssl")

        if server.check_sni:
            parts.append(f"check-sni {server.check_sni}")

        # SSL/TLS version constraints
        if server.ssl_min_ver:
            parts.append(f"ssl-min-ver {server.ssl_min_ver}")

        if server.ssl_max_ver:
            parts.append(f"ssl-max-ver {server.ssl_max_ver}")

        # Server certificate options
        if server.ca_file:
            parts.append(f"ca-file {server.ca_file}")

        if server.crt:
            parts.append(f"crt {server.crt}")

        # Source IP binding
        if server.source:
            parts.append(f"source {server.source}")

        for key, value in server.options.items():
            if isinstance(value, bool) and value:
                parts.append(key)
            elif value:
                parts.append(f"{key} {value}")

        return " ".join(parts)

    def _format_server_template(self, template: ServerTemplate) -> str:
        """Format server template."""
        parts = [
            f"server-template {template.prefix} {template.count}",
            f"{template.fqdn_pattern}:{template.port}",
        ]

        base = template.base_server
        if base:
            if base.check:
                parts.append("check")
                if base.check_interval:
                    parts.append(f"inter {base.check_interval}")
                parts.append(f"rise {base.rise}")
                parts.append(f"fall {base.fall}")

            if base.weight != 1:
                parts.append(f"weight {base.weight}")

            if base.maxconn:
                parts.append(f"maxconn {base.maxconn}")

            if base.ssl:
                parts.append("ssl")
                if base.ssl_verify:
                    parts.append(f"verify {base.ssl_verify}")

        return " ".join(parts)

    def _indent(self, line: str) -> str:
        """Add indentation to line."""
        return self.indent_str + line

    def get_lua_files(self) -> list[str]:
        """Get list of Lua files referenced in configuration."""
        return self.lua_files

    def _format_stick_table(self, stick_table: "StickTable") -> str:
        """Format stick-table directive."""
        parts = [f"stick-table type {stick_table.type} size {stick_table.size}"]

        if stick_table.expire:
            parts.append(f"expire {stick_table.expire}")

        if stick_table.nopurge:
            parts.append("nopurge")

        if stick_table.peers:
            parts.append(f"peers {stick_table.peers}")

        if stick_table.store:
            store_str = " ".join(stick_table.store)
            parts.append(f"store {store_str}")

        return " ".join(parts)

    def _format_stick_rule(self, stick_rule: "StickRule") -> str:
        """Format stick rule (stick on/match/store)."""
        parts = [f"stick {stick_rule.rule_type}"]

        if stick_rule.pattern:
            parts.append(stick_rule.pattern)

        if stick_rule.table:
            parts.append(f"table {stick_rule.table}")

        if stick_rule.condition:
            parts.append(f"if {stick_rule.condition}")

        return " ".join(parts)

    def _format_tcp_request_rule(self, tcp_req: "TcpRequestRule") -> str:
        """Format tcp-request rule."""
        parts = [f"tcp-request {tcp_req.rule_type} {tcp_req.action}"]

        # Add parameters
        for key, value in tcp_req.parameters.items():
            if key == "params" and isinstance(value, list):
                # Params list should be appended directly without key
                parts.extend(value)
            else:
                parts.append(f"{key} {value}")

        if tcp_req.condition:
            parts.append(f"if {tcp_req.condition}")

        return " ".join(parts)

    def _format_tcp_response_rule(self, tcp_resp: "TcpResponseRule") -> str:
        """Format tcp-response rule."""
        parts = [f"tcp-response {tcp_resp.rule_type} {tcp_resp.action}"]

        # Add parameters
        for key, value in tcp_resp.parameters.items():
            if key == "params" and isinstance(value, list):
                # Params list should be appended directly without key
                parts.extend(value)
            else:
                parts.append(f"{key} {value}")

        if tcp_resp.condition:
            parts.append(f"if {tcp_resp.condition}")

        return " ".join(parts)
