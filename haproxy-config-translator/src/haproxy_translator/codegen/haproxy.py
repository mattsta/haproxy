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
    HttpCheckRule,
    HttpRequestRule,
    HttpResponseRule,
    Listen,
    MailersSection,
    PeersSection,
    RedirectRule,
    ResolversSection,
    Server,
    ServerTemplate,
    StickRule,
    StickTable,
    TcpCheckRule,
    TcpRequestRule,
    TcpResponseRule,
    UseServerRule,
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

        # Generate peers sections
        for peers in ir.peers:
            lines.extend(self._generate_peers(peers))
            lines.append("")

        # Generate resolvers sections
        for resolvers in ir.resolvers:
            lines.extend(self._generate_resolvers(resolvers))
            lines.append("")

        # Generate mailers sections
        for mailers in ir.mailers:
            lines.extend(self._generate_mailers(mailers))
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

        if global_config.external_check is not None and global_config.external_check:
            lines.append(self._indent("external-check"))

        # Connection tuning
        if global_config.maxpipes:
            lines.append(self._indent(f"maxpipes {global_config.maxpipes}"))

        # Master-worker mode
        if global_config.master_worker is not None and global_config.master_worker:
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
            lines.append(self._indent("set-dumpable"))

        if global_config.unix_bind:
            lines.append(self._indent(f"unix-bind {global_config.unix_bind}"))

        for process_thread, cpu_list in global_config.cpu_map.items():
            lines.append(self._indent(f"cpu-map {process_thread} {cpu_list}"))

        # Performance & Runtime (Phase 4A)
        if global_config.busy_polling is not None and global_config.busy_polling:
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
        if global_config.noepoll is not None and global_config.noepoll:
            lines.append(self._indent("noepoll"))

        if global_config.nokqueue is not None and global_config.nokqueue:
            lines.append(self._indent("nokqueue"))

        if global_config.nopoll is not None and global_config.nopoll:
            lines.append(self._indent("nopoll"))

        if global_config.nosplice is not None and global_config.nosplice:
            lines.append(self._indent("nosplice"))

        if global_config.nogetaddrinfo is not None and global_config.nogetaddrinfo:
            lines.append(self._indent("nogetaddrinfo"))

        if global_config.noreuseport is not None and global_config.noreuseport:
            lines.append(self._indent("noreuseport"))

        if global_config.limited_quic is not None and global_config.limited_quic:
            lines.append(self._indent("limited-quic"))

        if global_config.localpeer:
            lines.append(self._indent(f"localpeer {global_config.localpeer}"))

        # SSL Advanced (Phase 4B Part 2)
        if global_config.ssl_load_extra_files:
            lines.append(self._indent(f"ssl-load-extra-files {global_config.ssl_load_extra_files}"))

        if global_config.ssl_load_extra_del_ext:
            lines.append(self._indent(f"ssl-load-extra-del-ext {global_config.ssl_load_extra_del_ext}"))

        if global_config.ssl_mode_async is not None and global_config.ssl_mode_async:
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

        # Stats sockets (Runtime API)
        for stats_socket in global_config.stats_sockets:
            socket_line = f"stats socket {stats_socket.path}"
            if stats_socket.level:
                socket_line += f" level {stats_socket.level}"
            if stats_socket.mode:
                socket_line += f" mode {stats_socket.mode}"
            if stats_socket.user:
                socket_line += f" user {stats_socket.user}"
            if stats_socket.group:
                socket_line += f" group {stats_socket.group}"
            if stats_socket.process:
                socket_line += f" process {stats_socket.process}"
            lines.append(self._indent(socket_line))

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

        # Description
        if frontend.description:
            lines.append(self._indent(f"description {frontend.description}"))

        # Status (disabled/enabled)
        if frontend.disabled:
            lines.append(self._indent("disabled"))

        if not frontend.enabled:
            lines.append(self._indent("disabled"))

        # ID
        if frontend.id is not None:
            lines.append(self._indent(f"id {frontend.id}"))

        # GUID (Global Unique Identifier)
        if frontend.guid:
            lines.append(self._indent(f"guid {frontend.guid}"))

        # Max connections
        if frontend.maxconn:
            lines.append(self._indent(f"maxconn {frontend.maxconn}"))

        # Backlog
        if frontend.backlog:
            lines.append(self._indent(f"backlog {frontend.backlog}"))

        # Fullconn (dynamic weight threshold)
        if frontend.fullconn:
            lines.append(self._indent(f"fullconn {frontend.fullconn}"))

        # Keep-alive queue
        if frontend.max_keep_alive_queue:
            lines.append(self._indent(f"max-keep-alive-queue {frontend.max_keep_alive_queue}"))

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

        # Monitor network sources
        for net in frontend.monitor_net:
            lines.append(self._indent(f"monitor-net {net}"))

        # Monitor fail conditions
        for fail_rule in frontend.monitor_fail_rules:
            lines.append(self._indent(f"monitor fail {fail_rule.condition}"))

        # Logging
        for log_target in frontend.log:
            lines.append(self._indent(f"log {log_target}"))

        if frontend.log_tag:
            lines.append(self._indent(f"log-tag {frontend.log_tag}"))

        # Log format
        if frontend.log_format:
            lines.append(self._indent(f"log-format {frontend.log_format}"))

        if frontend.error_log_format:
            lines.append(self._indent(f"error-log-format {frontend.error_log_format}"))

        if frontend.log_format_sd:
            lines.append(self._indent(f"log-format-sd {frontend.log_format_sd}"))

        # Unique ID tracking
        if frontend.unique_id_format:
            lines.append(self._indent(f"unique-id-format {frontend.unique_id_format}"))

        if frontend.unique_id_header:
            lines.append(self._indent(f"unique-id-header {frontend.unique_id_header}"))

        # Stats configuration
        if frontend.stats_config:
            stats = frontend.stats_config
            if stats.enable:
                lines.append(self._indent("stats enable"))
            if stats.uri:
                lines.append(self._indent(f"stats uri {stats.uri}"))
            if stats.realm:
                lines.append(self._indent(f"stats realm {stats.realm}"))
            for auth in stats.auth:
                lines.append(self._indent(f"stats auth {auth}"))
            if stats.hide_version:
                lines.append(self._indent("stats hide-version"))
            if stats.refresh:
                lines.append(self._indent(f"stats refresh {stats.refresh}"))
            if stats.show_legends:
                lines.append(self._indent("stats show-legends"))
            if stats.show_desc:
                lines.append(self._indent(f"stats show-desc {stats.show_desc}"))
            for admin_rule in stats.admin_rules:
                lines.append(self._indent(f"stats admin {admin_rule}"))

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

        # Redirect rules
        for redirect in frontend.redirect_rules:
            lines.append(self._indent(self._format_redirect_rule(redirect)))

        # Error files
        for error_file in frontend.error_files:
            lines.append(self._indent(f"errorfile {error_file.code} {error_file.file}"))

        # Error location redirects
        for code, location in frontend.errorloc.items():
            lines.append(self._indent(f'errorloc {code} "{location}"'))
        for code, location in frontend.errorloc302.items():
            lines.append(self._indent(f'errorloc302 {code} "{location}"'))
        for code, location in frontend.errorloc303.items():
            lines.append(self._indent(f'errorloc303 {code} "{location}"'))

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

        # Description
        if backend.description:
            lines.append(self._indent(f"description {backend.description}"))

        # Status (disabled/enabled)
        if backend.disabled:
            lines.append(self._indent("disabled"))

        if not backend.enabled:
            lines.append(self._indent("disabled"))

        # ID
        if backend.id is not None:
            lines.append(self._indent(f"id {backend.id}"))

        # GUID (Global Unique Identifier)
        if backend.guid:
            lines.append(self._indent(f"guid {backend.guid}"))

        # Balance algorithm
        lines.append(self._indent(f"balance {backend.balance.value}"))

        # Hash type (for hash-based load balancing)
        if backend.hash_type:
            lines.append(self._indent(f"hash-type {backend.hash_type}"))

        # Hash balance factor (tuning for hash-based load balancing)
        if backend.hash_balance_factor:
            lines.append(self._indent(f"hash-balance-factor {backend.hash_balance_factor}"))

        # Load server state from file
        if backend.load_server_state_from:
            lines.append(self._indent(f"load-server-state-from-file {backend.load_server_state_from.value}"))

        # Server state file name
        if backend.server_state_file_name:
            lines.append(self._indent(f"server-state-file-name {backend.server_state_file_name}"))

        # Retries
        if backend.retries is not None:
            lines.append(self._indent(f"retries {backend.retries}"))

        # Max connections
        if backend.maxconn:
            lines.append(self._indent(f"maxconn {backend.maxconn}"))

        # Backlog
        if backend.backlog:
            lines.append(self._indent(f"backlog {backend.backlog}"))

        # Keep-alive queue
        if backend.max_keep_alive_queue:
            lines.append(self._indent(f"max-keep-alive-queue {backend.max_keep_alive_queue}"))

        # Session-server connections
        if backend.max_session_srv_conns:
            lines.append(self._indent(f"max-session-srv-conns {backend.max_session_srv_conns}"))

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

        # Logging
        for log_target in backend.log:
            lines.append(self._indent(f"log {log_target}"))

        if backend.log_tag:
            lines.append(self._indent(f"log-tag {backend.log_tag}"))

        # Log format
        if backend.log_format:
            lines.append(self._indent(f"log-format {backend.log_format}"))

        if backend.error_log_format:
            lines.append(self._indent(f"error-log-format {backend.error_log_format}"))

        if backend.log_format_sd:
            lines.append(self._indent(f"log-format-sd {backend.log_format_sd}"))

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

        # Redirect rules
        for redirect in backend.redirect_rules:
            lines.append(self._indent(self._format_redirect_rule(redirect)))

        # Error files
        for error_file in backend.error_files:
            lines.append(self._indent(f"errorfile {error_file.code} {error_file.file}"))

        # Error location redirects
        for code, location in backend.errorloc.items():
            lines.append(self._indent(f'errorloc {code} "{location}"'))
        for code, location in backend.errorloc302.items():
            lines.append(self._indent(f'errorloc302 {code} "{location}"'))
        for code, location in backend.errorloc303.items():
            lines.append(self._indent(f'errorloc303 {code} "{location}"'))

        # Error files directory
        if backend.errorfiles:
            lines.append(self._indent(f"errorfiles {backend.errorfiles}"))

        # Dispatch (simple load balancing)
        if backend.dispatch:
            lines.append(self._indent(f"dispatch {backend.dispatch}"))

        # FastCGI application
        if backend.use_fcgi_app:
            lines.append(self._indent(f"use-fcgi-app {backend.use_fcgi_app}"))

        # HTTP reuse (connection pooling)
        if backend.http_reuse:
            lines.append(self._indent(f"http-reuse {backend.http_reuse}"))

        # HTTP send name header
        if backend.http_send_name_header:
            lines.append(self._indent(f"http-send-name-header {backend.http_send_name_header}"))

        # Retry conditions
        if backend.retry_on:
            lines.append(self._indent(f"retry-on {backend.retry_on}"))

        # External health check
        if backend.external_check_command:
            lines.append(self._indent(f"external-check command {backend.external_check_command}"))
        if backend.external_check_path:
            lines.append(self._indent(f"external-check path {backend.external_check_path}"))

        # Source IP binding
        if backend.source:
            lines.append(self._indent(f"source {backend.source}"))

        # HTTP check rules (advanced health checks)
        for http_check in backend.http_check_rules:
            lines.append(self._indent(self._format_http_check_rule(http_check)))

        # TCP check rules (advanced health checks)
        for tcp_check in backend.tcp_check_rules:
            lines.append(self._indent(self._format_tcp_check_rule(tcp_check)))

        # Use-server rules (conditional server selection)
        for use_server in backend.use_server_rules:
            lines.append(self._indent(self._format_use_server_rule(use_server)))

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

        # Description
        if listen.description:
            lines.append(self._indent(f"description {listen.description}"))

        # Status (disabled/enabled)
        if listen.disabled:
            lines.append(self._indent("disabled"))

        if not listen.enabled:
            lines.append(self._indent("disabled"))

        # ID
        if listen.id is not None:
            lines.append(self._indent(f"id {listen.id}"))

        # GUID (Global Unique Identifier)
        if listen.guid:
            lines.append(self._indent(f"guid {listen.guid}"))

        # Balance
        lines.append(self._indent(f"balance {listen.balance.value}"))

        # Load server state from file
        if listen.load_server_state_from:
            lines.append(self._indent(f"load-server-state-from-file {listen.load_server_state_from.value}"))

        # Server state file name
        if listen.server_state_file_name:
            lines.append(self._indent(f"server-state-file-name {listen.server_state_file_name}"))

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

    def _format_redirect_rule(self, redirect: "RedirectRule") -> str:
        """Format redirect rule."""
        parts = [f"redirect {redirect.type}"]

        # Add target
        # Handle scheme redirect which has type as part of directive
        if redirect.type == "scheme":
            parts.append(redirect.target)
        else:
            # For location and prefix, add the target URL/path
            parts.append(redirect.target)

        # Add optional code
        if redirect.code:
            parts.append(f"code {redirect.code}")

        # Add options
        for key, value in redirect.options.items():
            if key in ("drop-query", "append-slash"):
                if value:  # Only add if True
                    parts.append(key)
            elif key in ("set-cookie", "clear-cookie"):
                parts.append(f"{key} {value}")

        # Add condition
        if redirect.condition:
            parts.append(redirect.condition)

        return " ".join(parts)

    def _format_use_server_rule(self, use_server: "UseServerRule") -> str:
        """Format use-server rule."""
        parts = [f"use-server {use_server.server}"]

        # Add condition
        if use_server.condition:
            parts.append(use_server.condition)

        return " ".join(parts)

    def _format_http_check_rule(self, http_check: "HttpCheckRule") -> str:
        """Format http-check rule."""
        if http_check.type == "send":
            parts = ["http-check send"]
            if http_check.method:
                parts.append(f"meth {http_check.method}")
            if http_check.uri:
                parts.append(f"uri {http_check.uri}")
            if http_check.headers:
                for header_name, header_value in http_check.headers.items():
                    parts.append(f"hdr {header_name} {header_value}")
            return " ".join(parts)

        if http_check.type == "expect":
            parts = ["http-check expect"]
            if http_check.expect_negate:
                parts.append("!")
            if http_check.expect_type == "status":
                parts.append(f"status {http_check.expect_value}")
            elif http_check.expect_type == "string":
                parts.append(f"string {http_check.expect_value}")
            elif http_check.expect_type == "rstatus":
                parts.append(f"rstatus {http_check.expect_value}")
            elif http_check.expect_type == "rstring":
                parts.append(f"rstring {http_check.expect_value}")
            return " ".join(parts)

        if http_check.type == "connect":
            parts = ["http-check connect"]
            if http_check.port:
                parts.append(f"port {http_check.port}")
            if http_check.ssl:
                parts.append("ssl")
            if http_check.sni:
                parts.append(f"sni {http_check.sni}")
            if http_check.alpn:
                parts.append(f"alpn {http_check.alpn}")
            return " ".join(parts)

        if http_check.type == "disable-on-404":
            return "http-check disable-on-404"

        return ""

    def _format_tcp_check_rule(self, tcp_check: "TcpCheckRule") -> str:
        """Format tcp-check rule."""
        if tcp_check.type == "connect":
            parts = ["tcp-check connect"]
            if tcp_check.port:
                parts.append(f"port {tcp_check.port}")
            if tcp_check.ssl:
                parts.append("ssl")
            if tcp_check.sni:
                parts.append(f"sni {tcp_check.sni}")
            if tcp_check.alpn:
                parts.append(f"alpn {tcp_check.alpn}")
            return " ".join(parts)

        if tcp_check.type == "send":
            return f"tcp-check send {tcp_check.data}"

        if tcp_check.type == "send-binary":
            return f"tcp-check send-binary {tcp_check.data}"

        if tcp_check.type == "expect":
            parts = ["tcp-check expect"]
            if tcp_check.pattern:
                parts.append(tcp_check.pattern)
            return " ".join(parts)

        if tcp_check.type == "comment":
            return f"tcp-check comment {tcp_check.comment}"

        return ""

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

    def _generate_peers(self, peers: "PeersSection") -> list[str]:
        """Generate peers section for stick table replication."""
        lines = [f"peers {peers.name}"]

        if peers.disabled:
            lines.append(self._indent("disabled"))

        for peer in peers.peers:
            lines.append(self._indent(f"peer {peer.name} {peer.address}:{peer.port}"))

        return lines

    def _generate_resolvers(self, resolvers: "ResolversSection") -> list[str]:
        """Generate resolvers section for DNS resolution."""
        lines = [f"resolvers {resolvers.name}"]

        for nameserver in resolvers.nameservers:
            lines.append(self._indent(f"nameserver {nameserver.name} {nameserver.address}:{nameserver.port}"))

        if resolvers.accepted_payload_size:
            lines.append(self._indent(f"accepted_payload_size {resolvers.accepted_payload_size}"))

        if resolvers.hold_nx:
            lines.append(self._indent(f"hold nx {resolvers.hold_nx}"))
        if resolvers.hold_obsolete:
            lines.append(self._indent(f"hold obsolete {resolvers.hold_obsolete}"))
        if resolvers.hold_other:
            lines.append(self._indent(f"hold other {resolvers.hold_other}"))
        if resolvers.hold_refused:
            lines.append(self._indent(f"hold refused {resolvers.hold_refused}"))
        if resolvers.hold_timeout:
            lines.append(self._indent(f"hold timeout {resolvers.hold_timeout}"))
        if resolvers.hold_valid:
            lines.append(self._indent(f"hold valid {resolvers.hold_valid}"))

        if resolvers.resolve_retries:
            lines.append(self._indent(f"resolve_retries {resolvers.resolve_retries}"))
        if resolvers.timeout_resolve:
            lines.append(self._indent(f"timeout resolve {resolvers.timeout_resolve}"))
        if resolvers.timeout_retry:
            lines.append(self._indent(f"timeout retry {resolvers.timeout_retry}"))

        return lines

    def _generate_mailers(self, mailers: "MailersSection") -> list[str]:
        """Generate mailers section for email alerts."""
        lines = [f"mailers {mailers.name}"]

        if mailers.timeout_mail:
            lines.append(self._indent(f"timeout mail {mailers.timeout_mail}"))

        for mailer in mailers.mailers:
            lines.append(self._indent(f"mailer {mailer.name} {mailer.address}:{mailer.port}"))

        return lines

