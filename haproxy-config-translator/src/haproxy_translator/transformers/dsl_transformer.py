"""Lark transformer to convert parse tree to IR."""

from typing import Any, cast

from lark import Token, Transformer

from ..ir.nodes import (
    ACL,
    Backend,
    BalanceAlgorithm,
    Bind,
    CompressionConfig,
    ConfigIR,
    DeclareCapture,
    DefaultsConfig,
    DefaultServer,
    EmailAlert,
    ErrorFile,
    Filter,
    ForcePersistRule,
    ForLoop,
    Frontend,
    GlobalConfig,
    HealthCheck,
    HttpAfterResponseRule,
    HttpCheckRule,
    HttpError,
    HttpRequestRule,
    HttpResponseRule,
    IgnorePersistRule,
    Listen,
    LogFacility,
    LogLevel,
    LogTarget,
    LuaScript,
    Mailer,
    MailersSection,
    Mode,
    MonitorFailRule,
    Nameserver,
    Peer,
    PeersSection,
    QuicInitialRule,
    RedirectRule,
    ResolversSection,
    Server,
    ServerTemplate,
    StatsConfig,
    StatsSocket,
    StickRule,
    StickTable,
    TcpCheckRule,
    TcpRequestRule,
    TcpResponseRule,
    Template,
    UseBackendRule,
    UseServerRule,
    Variable,
)


class DSLTransformer(Transformer):
    """Transform Lark parse tree to ConfigIR."""

    def __init__(self, filepath: str = "<input>"):
        self.filepath = filepath
        self.variables: dict[str, Variable] = {}
        self.templates: dict[str, Template] = {}

    # ===== Top Level =====
    def config(self, items: list[Any]) -> ConfigIR:
        """Transform top-level config."""
        name = str(items[0])
        statements = items[1:]

        global_config = None
        defaults = None
        frontends = []
        backends = []
        listens = []
        imports = []
        lua_scripts = []
        peers = []
        resolvers = []
        mailers = []

        for stmt in statements:
            if isinstance(stmt, GlobalConfig):
                global_config = stmt
            elif isinstance(stmt, DefaultsConfig):
                defaults = stmt
            elif isinstance(stmt, Frontend):
                frontends.append(stmt)
            elif isinstance(stmt, Backend):
                backends.append(stmt)
            elif isinstance(stmt, Listen):
                listens.append(stmt)
            elif isinstance(stmt, PeersSection):
                peers.append(stmt)
            elif isinstance(stmt, ResolversSection):
                resolvers.append(stmt)
            elif isinstance(stmt, MailersSection):
                mailers.append(stmt)
            elif isinstance(stmt, list):
                # lua_section returns a list of LuaScript objects
                for item in stmt:
                    if isinstance(item, LuaScript):
                        lua_scripts.append(item)
            elif isinstance(stmt, LuaScript):
                # Single lua script
                lua_scripts.append(stmt)
            elif isinstance(stmt, Variable):
                self.variables[stmt.name] = stmt
            elif isinstance(stmt, Template):
                self.templates[stmt.name] = stmt
            elif isinstance(stmt, str) and stmt.startswith("import:"):
                imports.append(stmt[7:])

        return ConfigIR(
            name=name,
            global_config=global_config,
            defaults=defaults,
            frontends=frontends,
            backends=backends,
            listens=listens,
            lua_scripts=lua_scripts,
            peers=peers,
            resolvers=resolvers,
            mailers=mailers,
            variables=self.variables,
            templates=self.templates,
            imports=imports,
        )

    # ===== Global Section =====
    def global_section(self, items: list[Any]) -> GlobalConfig:
        """Transform global section."""
        # Process management
        daemon = True
        user = None
        group = None
        uid = None
        gid = None
        chroot = None
        pidfile = None
        nbproc = None
        nbthread = None  # Phase 10
        thread_groups = None  # Phase 10
        master_worker = None
        mworker_max_reloads = None
        node = None
        description = None
        hard_stop_after = None
        external_check = None
        numa_cpu_mapping = None  # Phase 10

        # Connection limits
        maxconn = 2000
        maxconnrate = None
        maxsslrate = None
        maxsessrate = None
        maxpipes = None

        # Resource limits (Phase 10 Batch 2)
        fd_hard_limit = None
        maxzlibmem = None
        strict_limits = None

        # SSL/TLS paths
        ca_base = None
        crt_base = None
        key_base = None

        # SSL/TLS configuration
        ssl_dh_param_file = None
        ssl_default_bind_ciphers = None
        ssl_default_bind_options = []
        ssl_default_bind_ciphersuites = None
        ssl_default_server_ciphers = None
        ssl_default_server_ciphersuites = None
        ssl_default_server_options = []
        ssl_server_verify = None
        ssl_engine = None

        # SSL/TLS Advanced Configuration (Phase 13 Batch 4)
        ssl_default_bind_curves = None
        ssl_default_bind_sigalgs = None
        ssl_default_bind_client_sigalgs = None
        ssl_default_server_curves = None
        ssl_default_server_sigalgs = None
        ssl_default_server_client_sigalgs = None
        ssl_security_level = None

        # Logging configuration
        log_tag = None
        log_send_hostname = None
        log_targets = []

        # Environment variables
        env_vars = {}
        reset_env_vars = []
        unset_env_vars = []

        # System configuration (Phase 3)
        setcap = None
        set_dumpable = None
        unix_bind = None
        cpu_map = {}

        # Performance & Runtime (Phase 4A)
        busy_polling = None
        max_spread_checks = None
        spread_checks = None
        maxcompcpuusage = None
        maxcomprate = None
        default_path = None

        # Server State Management (Phase 10 Batch 3)
        server_state_base = None
        server_state_file = None
        load_server_state_from_file = None

        # HTTP Client Configuration (Phase 4B Part 1)
        httpclient_resolvers_disabled = None
        httpclient_resolvers_id = None
        httpclient_resolvers_prefer = None
        httpclient_retries = None
        httpclient_ssl_verify = None
        httpclient_ssl_ca_file = None
        httpclient_timeout_connect = None  # Phase 12 Batch 3

        # Platform-Specific Options (Phase 4B Part 1)
        noepoll = None
        nokqueue = None
        nopoll = None
        nosplice = None
        nogetaddrinfo = None
        noreuseport = None
        noevports = None  # Phase 12 Batch 6
        noktls = None  # Phase 12 Batch 6
        no_memory_trimming = None  # Phase 12 Batch 6
        limited_quic = None
        localpeer = None

        # SSL Advanced (Phase 4B Part 2)
        ssl_load_extra_files = None
        ssl_load_extra_del_ext = None
        ssl_mode_async = None
        ssl_propquery = None
        ssl_provider = None
        ssl_provider_path = None
        issuers_chain_path = None

        # Profiling & Debugging (Phase 4B Part 2)
        profiling_tasks_on = None
        profiling_tasks_automatic = None
        profiling_memory_on = None
        profiling_memory = None  # Phase 12 Batch 6
        profiling_tasks = None  # Phase 12 Batch 6

        # Debugging & Development (Phase 7)
        quiet = None
        debug_counters = None
        anonkey = None
        zero_warning = None
        warn_blocked_traffic_after = None
        force_cfg_parser_pause = None

        # Device Detection - DeviceAtlas (Phase 4B Part 4)
        deviceatlas_json_file = None
        deviceatlas_log_level = None
        deviceatlas_separator = None
        deviceatlas_properties_cookie = None

        # Device Detection - 51Degrees (Phase 4B Part 4)
        fiftyone_degrees_data_file = None
        fiftyone_degrees_property_name_list = None
        fiftyone_degrees_property_separator = None
        fiftyone_degrees_cache_size = None

        # Device Detection - WURFL (Phase 4B Part 4)
        wurfl_data_file = None
        wurfl_information_list = None
        wurfl_information_list_separator = None
        wurfl_patch_file = None
        wurfl_cache_size = None
        wurfl_engine_mode = None
        wurfl_useragent_priority = None

        # Lua scripts
        lua_scripts = []

        # Lua global directives (Phase 13 Batch 3)
        lua_load_files = []
        lua_load_per_thread_files = []
        lua_prepend_paths = []

        # Stats
        stats = None
        stats_sockets = []

        # Performance tuning
        tuning = {}

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "daemon":
                    daemon = value
                elif key == "maxconn":
                    maxconn = value
                elif key == "nbproc":
                    nbproc = value
                elif key == "nbthread":  # Phase 10
                    nbthread = value
                elif key == "thread_groups":  # Phase 10
                    thread_groups = value
                elif key == "maxconnrate":
                    maxconnrate = value
                elif key == "maxsslrate":
                    maxsslrate = value
                elif key == "maxsessrate":
                    maxsessrate = value
                elif key == "user":
                    user = value
                elif key == "group":
                    group = value
                elif key == "chroot":
                    chroot = value
                elif key == "pidfile":
                    pidfile = value
                elif key == "maxpipes":
                    maxpipes = value
                # Phase 10 Batch 2 - Resource limits
                elif key == "fd_hard_limit":
                    fd_hard_limit = value
                elif key == "maxzlibmem":
                    maxzlibmem = value
                elif key == "strict_limits":
                    strict_limits = value
                elif key == "ca_base":
                    ca_base = value
                elif key == "crt_base":
                    crt_base = value
                elif key == "key_base":
                    key_base = value
                elif key == "log_tag":
                    log_tag = value
                elif key == "log_send_hostname":
                    log_send_hostname = value
                elif key == "ssl_dh_param_file":
                    ssl_dh_param_file = value
                elif key == "ssl_default_bind_ciphers":
                    ssl_default_bind_ciphers = value
                elif key == "ssl_default_bind_options":
                    ssl_default_bind_options = value
                elif key == "ssl_default_bind_ciphersuites":
                    ssl_default_bind_ciphersuites = value
                elif key == "ssl_default_server_ciphers":
                    ssl_default_server_ciphers = value
                elif key == "ssl_default_server_ciphersuites":
                    ssl_default_server_ciphersuites = value
                elif key == "ssl_default_server_options":
                    ssl_default_server_options = value
                elif key == "ssl_server_verify":
                    ssl_server_verify = value
                elif key == "ssl_engine":
                    ssl_engine = value
                # Phase 13 Batch 4 - SSL Advanced Configuration
                elif key == "ssl_default_bind_curves":
                    ssl_default_bind_curves = value
                elif key == "ssl_default_bind_sigalgs":
                    ssl_default_bind_sigalgs = value
                elif key == "ssl_default_bind_client_sigalgs":
                    ssl_default_bind_client_sigalgs = value
                elif key == "ssl_default_server_curves":
                    ssl_default_server_curves = value
                elif key == "ssl_default_server_sigalgs":
                    ssl_default_server_sigalgs = value
                elif key == "ssl_default_server_client_sigalgs":
                    ssl_default_server_client_sigalgs = value
                elif key == "ssl_security_level":
                    ssl_security_level = value
                elif key == "master_worker":
                    master_worker = value
                elif key == "mworker_max_reloads":
                    mworker_max_reloads = value
                elif key == "uid":
                    uid = value
                elif key == "gid":
                    gid = value
                elif key == "node":
                    node = value
                elif key == "description":
                    description = value
                elif key == "hard_stop_after":
                    hard_stop_after = value
                elif key == "external_check":
                    external_check = value
                elif key == "numa_cpu_mapping":  # Phase 10
                    numa_cpu_mapping = value
                # Phase 4A - Performance & Runtime
                elif key == "busy_polling":
                    busy_polling = value
                elif key == "max_spread_checks":
                    max_spread_checks = value
                elif key == "spread_checks":
                    spread_checks = value
                elif key == "maxcompcpuusage":
                    maxcompcpuusage = value
                elif key == "maxcomprate":
                    maxcomprate = value
                elif key == "default_path":
                    default_path = value
                # Phase 10 Batch 3 - Server State Management
                elif key == "server_state_base":
                    server_state_base = value
                elif key == "server_state_file":
                    server_state_file = value
                elif key == "load_server_state_from_file":
                    load_server_state_from_file = value
                # Phase 4B Part 1 - HTTP Client Configuration
                elif key == "httpclient_resolvers_disabled":
                    httpclient_resolvers_disabled = value
                elif key == "httpclient_resolvers_id":
                    httpclient_resolvers_id = value
                elif key == "httpclient_resolvers_prefer":
                    httpclient_resolvers_prefer = value
                elif key == "httpclient_retries":
                    httpclient_retries = value
                elif key == "httpclient_ssl_verify":
                    httpclient_ssl_verify = value
                elif key == "httpclient_ssl_ca_file":
                    httpclient_ssl_ca_file = value
                elif key == "httpclient_timeout_connect":  # Phase 12 Batch 3
                    httpclient_timeout_connect = value
                # Phase 4B Part 1 - Platform-Specific Options
                elif key == "noepoll":
                    noepoll = value
                elif key == "nokqueue":
                    nokqueue = value
                elif key == "nopoll":
                    nopoll = value
                elif key == "nosplice":
                    nosplice = value
                elif key == "nogetaddrinfo":
                    nogetaddrinfo = value
                elif key == "noreuseport":
                    noreuseport = value
                elif key == "noevports":  # Phase 12 Batch 6
                    noevports = value
                elif key == "noktls":  # Phase 12 Batch 6
                    noktls = value
                elif key == "no_memory_trimming":  # Phase 12 Batch 6
                    no_memory_trimming = value
                elif key == "limited_quic":
                    limited_quic = value
                elif key == "localpeer":
                    localpeer = value
                # Phase 4B Part 2 - SSL Advanced
                elif key == "ssl_load_extra_files":
                    ssl_load_extra_files = value
                elif key == "ssl_load_extra_del_ext":
                    ssl_load_extra_del_ext = value
                elif key == "ssl_mode_async":
                    ssl_mode_async = value
                elif key == "ssl_propquery":
                    ssl_propquery = value
                elif key == "ssl_provider":
                    ssl_provider = value
                elif key == "ssl_provider_path":
                    ssl_provider_path = value
                elif key == "issuers_chain_path":
                    issuers_chain_path = value
                # Phase 4B Part 2 - Profiling & Debugging
                elif key == "profiling_tasks_on":
                    profiling_tasks_on = value
                elif key == "profiling_tasks_automatic":
                    profiling_tasks_automatic = value
                elif key == "profiling_memory_on":
                    profiling_memory_on = value
                elif key == "profiling_memory":  # Phase 12 Batch 6
                    profiling_memory = value
                elif key == "profiling_tasks":  # Phase 12 Batch 6
                    profiling_tasks = value
                # Phase 7 - Debugging & Development
                elif key == "quiet":
                    quiet = value
                elif key == "debug_counters":
                    debug_counters = value
                elif key == "anonkey":
                    anonkey = value
                elif key == "zero_warning":
                    zero_warning = value
                elif key == "warn_blocked_traffic_after":
                    warn_blocked_traffic_after = value
                elif key == "force_cfg_parser_pause":
                    force_cfg_parser_pause = value
                # Phase 4B Part 4 - Device Detection - DeviceAtlas
                elif key == "deviceatlas_json_file":
                    deviceatlas_json_file = value
                elif key == "deviceatlas_log_level":
                    deviceatlas_log_level = value
                elif key == "deviceatlas_separator":
                    deviceatlas_separator = value
                elif key == "deviceatlas_properties_cookie":
                    deviceatlas_properties_cookie = value
                # Phase 4B Part 4 - Device Detection - 51Degrees
                elif key == "fiftyone_degrees_data_file":
                    fiftyone_degrees_data_file = value
                elif key == "fiftyone_degrees_property_name_list":
                    fiftyone_degrees_property_name_list = value
                elif key == "fiftyone_degrees_property_separator":
                    fiftyone_degrees_property_separator = value
                elif key == "fiftyone_degrees_cache_size":
                    fiftyone_degrees_cache_size = value
                # Phase 4B Part 4 - Device Detection - WURFL
                elif key == "wurfl_data_file":
                    wurfl_data_file = value
                elif key == "wurfl_information_list":
                    wurfl_information_list = value
                elif key == "wurfl_information_list_separator":
                    wurfl_information_list_separator = value
                elif key == "wurfl_patch_file":
                    wurfl_patch_file = value
                elif key == "wurfl_cache_size":
                    wurfl_cache_size = value
                elif key == "wurfl_engine_mode":
                    wurfl_engine_mode = value
                elif key == "wurfl_useragent_priority":
                    wurfl_useragent_priority = value
                elif key == "setcap":
                    setcap = value
                elif key == "set_dumpable":
                    set_dumpable = value
                elif key == "unix_bind":
                    unix_bind = value
                elif key == "cpu_map":
                    # cpu_map returns tuple (process/thread, cpu_list)
                    cpu_map[value[0]] = value[1]
                elif key in {"setenv", "presetenv"}:
                    env_vars[value[0]] = value[1]
                elif key == "resetenv":
                    reset_env_vars.append(value)
                elif key == "unsetenv":
                    unset_env_vars.append(value)
                # Phase 13 Batch 3 - Lua global directives
                elif key == "lua_load":
                    lua_load_files.append(value)
                elif key == "lua_load_per_thread":
                    lua_load_per_thread_files.append(value)
                elif key == "lua_prepend_path":
                    lua_prepend_paths.append(value)
                elif key in ("nbthread", "maxsslconn", "ulimit_n"):
                    tuning[key] = value
                elif key.startswith("tune_"):
                    # All tune.* directives go into tuning dict
                    # Convert transformer key to HAProxy format
                    # e.g., tune_ssl_bufsize → tune.ssl.bufsize
                    # e.g., tune_h2_be_glitches_threshold → tune.h2.be.glitches-threshold
                    # e.g., tune_ssl_ocsp_update_minthour → tune.ssl.ocsp-update.minthour
                    # e.g., tune_idle_pool_shared → tune.idle-pool.shared
                    parts = key.split("_")
                    if len(parts) >= 3:
                        # parts[0] = "tune", parts[1] = category, rest = directive

                        # Special case for QUIC directives
                        if parts[1] == "quic":
                            if len(parts) >= 4 and parts[2] in ("frontend", "socket"):
                                # tune_quic_frontend_conn_tx_buffers_limit → tune.quic.frontend.conn-tx-buffers.limit
                                # tune_quic_socket_owner → tune.quic.socket.owner
                                subcategory = parts[2]
                                directive_parts = parts[3:]
                                tune_key = f"tune.quic.{subcategory}.{'-'.join(directive_parts)}"
                            elif len(parts) >= 4 and parts[2] in ("be", "fe"):
                                # Phase 13 Batch 2: Modern QUIC backend/frontend directives
                                # tune_quic_be_cc_cubic_min_losses → tune.quic.be.cc.cubic-min-losses
                                # tune_quic_fe_stream_rxbuf → tune.quic.fe.stream.rxbuf
                                # tune_quic_be_max_idle_timeout → tune.quic.be.max-idle-timeout
                                subcategory = parts[2]  # be or fe
                                if len(parts) >= 5 and parts[3] in ("cc", "sec", "stream", "tx"):
                                    # Has a sub-subcategory (cc, sec, stream, tx)
                                    subsubcategory = parts[3]
                                    directive_parts = parts[4:]
                                    tune_key = f"tune.quic.{subcategory}.{subsubcategory}.{'-'.join(directive_parts)}"
                                else:
                                    # No sub-subcategory (e.g., max-idle-timeout)
                                    directive_parts = parts[3:]
                                    tune_key = f"tune.quic.{subcategory}.{'-'.join(directive_parts)}"
                            elif len(parts) >= 4 and parts[2] == "mem":
                                # Phase 13 Batch 2: tune_quic_mem_tx_max → tune.quic.mem.tx-max
                                directive_parts = parts[3:]
                                tune_key = f"tune.quic.mem.{'-'.join(directive_parts)}"
                            else:
                                # tune_quic_retry_threshold → tune.quic.retry-threshold
                                # tune_quic_max_frame_loss → tune.quic.max-frame-loss
                                # tune_quic_listen → tune.quic.listen
                                directive_parts = parts[2:]
                                tune_key = f"tune.quic.{'-'.join(directive_parts)}"
                        # Special case for ocsp-update directives
                        elif len(parts) >= 5 and parts[2:4] == ["ocsp", "update"]:
                            # tune_ssl_ocsp_update_minthour → tune.ssl.ocsp-update.minthour
                            category = parts[1]
                            suffix = parts[4]
                            tune_key = f"tune.{category}.ocsp-update.{suffix}"
                        # Special case for idle-pool directives
                        elif len(parts) == 4 and parts[1:3] == ["idle", "pool"]:
                            # tune_idle_pool_shared → tune.idle-pool.shared
                            tune_key = f"tune.idle-pool.{parts[3]}"
                        # Special case for lua.log directives
                        elif len(parts) == 4 and parts[1:3] == ["lua", "log"]:
                            # tune_lua_log_loggers → tune.lua.log.loggers
                            tune_key = f"tune.lua.log.{parts[3]}"
                        # Special case for single-level compound directives (e.g., stick-counters, pattern-cache-size)
                        elif len(parts) == 3 and parts[1] in ("stick", "pattern"):
                            # tune_stick_counters → tune.stick-counters
                            # tune_pattern_cache_size → tune.pattern-cache-size (already 3 parts but handled below)
                            tune_key = f"tune.{'-'.join(parts[1:])}"
                        # Check if there's a subcategory (be, fe)
                        elif len(parts) >= 4 and parts[2] in ("be", "fe"):
                            category = parts[1]
                            subcategory = parts[2]
                            directive_parts = parts[3:]
                            tune_key = f"tune.{category}.{subcategory}.{'-'.join(directive_parts)}"
                        # Special case for top-level multi-word tune directives (Phase 6 & 12 Batch 6)
                        elif len(parts) == 3 and parts[1] in ("recv", "runqueue", "pipesize", "fail"):
                            # tune_recv_enough, tune_runqueue_depth, tune_pipesize, tune_fail_alloc
                            tune_key = f"tune.{'-'.join(parts[1:])}"
                        # Special case for categorized directives with sub-params (Phase 12 Batch 6)
                        elif len(parts) == 3 and parts[1] in ("epoll", "renice"):
                            # tune_epoll_mask_events → tune.epoll.mask-events
                            # tune_renice_runtime → tune.renice.runtime
                            category = parts[1]
                            directive_parts = [parts[2]]
                            tune_key = f"tune.{category}.{'-'.join(directive_parts)}"
                        # Special case for very long multi-word directives (Phase 12 Batch 6)
                        elif len(parts) == 5 and parts[1] == "takeover":
                            # tune_takeover_other_tg_connections → tune.takeover-other-tg-connections
                            tune_key = f"tune.{'-'.join(parts[1:])}"
                        elif len(parts) >= 3 and parts[1] == "max":
                            # tune_max_checks_per_thread, tune_max_rules_at_once
                            tune_key = f"tune.{'-'.join(parts[1:])}"
                        elif len(parts) >= 3 and parts[1] == "disable":
                            # tune_disable_fast_forward, tune_disable_zero_copy_forwarding
                            tune_key = f"tune.{'-'.join(parts[1:])}"
                        else:
                            category = parts[1]
                            directive_parts = parts[2:]
                            tune_key = f"tune.{category}.{'-'.join(directive_parts)}"
                    else:
                        # Fallback: just convert all underscores to dots
                        tune_key = key.replace("_", ".")
                    tuning[tune_key] = value
            elif isinstance(item, LogTarget):
                log_targets.append(item)
            elif isinstance(item, list) and all(isinstance(x, LuaScript) for x in item):
                lua_scripts.extend(item)
            elif isinstance(item, StatsConfig):
                stats = item
            elif isinstance(item, StatsSocket):
                stats_sockets.append(item)

        return GlobalConfig(
            # Process management
            daemon=daemon,
            user=user,
            group=group,
            uid=uid,
            gid=gid,
            chroot=chroot,
            pidfile=pidfile,
            nbproc=nbproc,
            nbthread=nbthread,  # Phase 10
            thread_groups=thread_groups,  # Phase 10
            master_worker=master_worker,
            mworker_max_reloads=mworker_max_reloads,
            node=node,
            description=description,
            hard_stop_after=hard_stop_after,
            external_check=external_check,
            numa_cpu_mapping=numa_cpu_mapping,  # Phase 10
            # Connection limits
            maxconn=maxconn,
            maxconnrate=maxconnrate,
            maxsslrate=maxsslrate,
            maxsessrate=maxsessrate,
            maxpipes=maxpipes,
            # Resource limits (Phase 10 Batch 2)
            fd_hard_limit=fd_hard_limit,
            maxzlibmem=maxzlibmem,
            strict_limits=strict_limits,
            # SSL/TLS paths
            ca_base=ca_base,
            crt_base=crt_base,
            key_base=key_base,
            # SSL/TLS configuration
            ssl_dh_param_file=ssl_dh_param_file,
            ssl_default_bind_ciphers=ssl_default_bind_ciphers,
            ssl_default_bind_options=ssl_default_bind_options,
            ssl_default_bind_ciphersuites=ssl_default_bind_ciphersuites,
            ssl_default_server_ciphers=ssl_default_server_ciphers,
            ssl_default_server_ciphersuites=ssl_default_server_ciphersuites,
            ssl_default_server_options=ssl_default_server_options,
            ssl_server_verify=ssl_server_verify,
            ssl_engine=ssl_engine,
            # SSL/TLS Advanced Configuration (Phase 13 Batch 4)
            ssl_default_bind_curves=ssl_default_bind_curves,
            ssl_default_bind_sigalgs=ssl_default_bind_sigalgs,
            ssl_default_bind_client_sigalgs=ssl_default_bind_client_sigalgs,
            ssl_default_server_curves=ssl_default_server_curves,
            ssl_default_server_sigalgs=ssl_default_server_sigalgs,
            ssl_default_server_client_sigalgs=ssl_default_server_client_sigalgs,
            ssl_security_level=ssl_security_level,
            # Logging configuration
            log_tag=log_tag,
            log_send_hostname=log_send_hostname,
            log_targets=log_targets,
            # Environment variables
            env_vars=env_vars,
            reset_env_vars=reset_env_vars,
            unset_env_vars=unset_env_vars,
            # System configuration (Phase 3)
            setcap=setcap,
            set_dumpable=set_dumpable,
            unix_bind=unix_bind,
            cpu_map=cpu_map,
            # Performance & Runtime (Phase 4A)
            busy_polling=busy_polling,
            max_spread_checks=max_spread_checks,
            spread_checks=spread_checks,
            maxcompcpuusage=maxcompcpuusage,
            maxcomprate=maxcomprate,
            default_path=default_path,
            # Server State Management (Phase 10 Batch 3)
            server_state_base=server_state_base,
            server_state_file=server_state_file,
            load_server_state_from_file=load_server_state_from_file,
            # HTTP Client Configuration (Phase 4B Part 1)
            httpclient_resolvers_disabled=httpclient_resolvers_disabled,
            httpclient_resolvers_id=httpclient_resolvers_id,
            httpclient_resolvers_prefer=httpclient_resolvers_prefer,
            httpclient_retries=httpclient_retries,
            httpclient_ssl_verify=httpclient_ssl_verify,
            httpclient_ssl_ca_file=httpclient_ssl_ca_file,
            httpclient_timeout_connect=httpclient_timeout_connect,  # Phase 12 Batch 3
            # Platform-Specific Options (Phase 4B Part 1)
            noepoll=noepoll,
            nokqueue=nokqueue,
            nopoll=nopoll,
            nosplice=nosplice,
            nogetaddrinfo=nogetaddrinfo,
            noreuseport=noreuseport,
            noevports=noevports,  # Phase 12 Batch 6
            noktls=noktls,  # Phase 12 Batch 6
            no_memory_trimming=no_memory_trimming,  # Phase 12 Batch 6
            limited_quic=limited_quic,
            localpeer=localpeer,
            # SSL Advanced (Phase 4B Part 2)
            ssl_load_extra_files=ssl_load_extra_files,
            ssl_load_extra_del_ext=ssl_load_extra_del_ext,
            ssl_mode_async=ssl_mode_async,
            ssl_propquery=ssl_propquery,
            ssl_provider=ssl_provider,
            ssl_provider_path=ssl_provider_path,
            issuers_chain_path=issuers_chain_path,
            # Profiling & Debugging (Phase 4B Part 2)
            profiling_tasks_on=profiling_tasks_on,
            profiling_tasks_automatic=profiling_tasks_automatic,
            profiling_memory_on=profiling_memory_on,
            profiling_memory=profiling_memory,  # Phase 12 Batch 6
            profiling_tasks=profiling_tasks,  # Phase 12 Batch 6
            # Debugging & Development (Phase 7)
            quiet=quiet,
            debug_counters=debug_counters,
            anonkey=anonkey,
            zero_warning=zero_warning,
            warn_blocked_traffic_after=warn_blocked_traffic_after,
            force_cfg_parser_pause=force_cfg_parser_pause,
            # Device Detection - DeviceAtlas (Phase 4B Part 4)
            deviceatlas_json_file=deviceatlas_json_file,
            deviceatlas_log_level=deviceatlas_log_level,
            deviceatlas_separator=deviceatlas_separator,
            deviceatlas_properties_cookie=deviceatlas_properties_cookie,
            # Device Detection - 51Degrees (Phase 4B Part 4)
            fiftyone_degrees_data_file=fiftyone_degrees_data_file,
            fiftyone_degrees_property_name_list=fiftyone_degrees_property_name_list,
            fiftyone_degrees_property_separator=fiftyone_degrees_property_separator,
            fiftyone_degrees_cache_size=fiftyone_degrees_cache_size,
            # Device Detection - WURFL (Phase 4B Part 4)
            wurfl_data_file=wurfl_data_file,
            wurfl_information_list=wurfl_information_list,
            wurfl_information_list_separator=wurfl_information_list_separator,
            wurfl_patch_file=wurfl_patch_file,
            wurfl_cache_size=wurfl_cache_size,
            wurfl_engine_mode=wurfl_engine_mode,
            wurfl_useragent_priority=wurfl_useragent_priority,
            # Lua scripts
            lua_scripts=lua_scripts,
            # Lua global directives (Phase 13 Batch 3)
            lua_load_files=lua_load_files,
            lua_load_per_thread_files=lua_load_per_thread_files,
            lua_prepend_paths=lua_prepend_paths,
            # Stats
            stats=stats,
            stats_sockets=stats_sockets,
            # Performance tuning
            tuning=tuning,
        )

    def global_daemon(self, items: list[Any]) -> tuple[str, bool]:
        return ("daemon", items[0])

    def global_maxconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxconn", items[0])

    def global_user(self, items: list[Any]) -> tuple[str, str]:
        return ("user", items[0])

    def global_group(self, items: list[Any]) -> tuple[str, str]:
        return ("group", items[0])

    def global_chroot(self, items: list[Any]) -> tuple[str, str]:
        return ("chroot", items[0])

    def global_pidfile(self, items: list[Any]) -> tuple[str, str]:
        return ("pidfile", items[0])

    def global_log(self, items: list[Any]) -> LogTarget:
        return cast("LogTarget", items[0])

    def global_lua(self, items: list[Any]) -> list[LuaScript]:
        return cast("list[LuaScript]", items[0])

    def global_stats(self, items: list[Any]) -> StatsConfig:
        return cast("StatsConfig", items[0])

    def global_ssl_default_bind_ciphers(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_default_bind_ciphers", items[0])

    def global_ssl_default_bind_options(self, items: list[Any]) -> tuple[str, list[str]]:
        return ("ssl_default_bind_options", items[0])

    def global_nbthread(self, items: list[Any]) -> tuple[str, int]:
        return ("nbthread", items[0])

    def global_thread_groups(self, items: list[Any]) -> tuple[str, int]:
        return ("thread_groups", items[0])

    def global_maxsslconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxsslconn", items[0])

    def global_ulimit_n(self, items: list[Any]) -> tuple[str, int]:
        return ("ulimit_n", items[0])

    def global_fd_hard_limit(self, items: list[Any]) -> tuple[str, int]:
        return ("fd_hard_limit", items[0])

    def global_maxzlibmem(self, items: list[Any]) -> tuple[str, int]:
        return ("maxzlibmem", items[0])

    def global_strict_limits(self, items: list[Any]) -> tuple[str, bool]:
        return ("strict_limits", items[0])

    def global_nbproc(self, items: list[Any]) -> tuple[str, int]:
        return ("nbproc", items[0])

    def global_maxconnrate(self, items: list[Any]) -> tuple[str, int]:
        return ("maxconnrate", items[0])

    def global_maxsslrate(self, items: list[Any]) -> tuple[str, int]:
        return ("maxsslrate", items[0])

    def global_maxsessrate(self, items: list[Any]) -> tuple[str, int]:
        return ("maxsessrate", items[0])

    def global_ca_base(self, items: list[Any]) -> tuple[str, str]:
        return ("ca_base", items[0])

    def global_crt_base(self, items: list[Any]) -> tuple[str, str]:
        return ("crt_base", items[0])

    def global_log_tag(self, items: list[Any]) -> tuple[str, str]:
        return ("log_tag", items[0])

    def global_log_send_hostname(self, items: list[Any]) -> tuple[str, str]:
        return ("log_send_hostname", items[0])

    def global_ssl_dh_param_file(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_dh_param_file", items[0])

    def global_ssl_default_server_ciphers(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_default_server_ciphers", items[0])

    def global_ssl_server_verify(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_server_verify", items[0])

    def global_setenv(self, items: list[Any]) -> tuple[str, tuple[str, str]]:
        return ("setenv", (items[0], items[1]))

    def global_presetenv(self, items: list[Any]) -> tuple[str, tuple[str, str]]:
        return ("presetenv", (items[0], items[1]))

    def global_resetenv(self, items: list[Any]) -> tuple[str, str]:
        return ("resetenv", items[0])

    def global_unsetenv(self, items: list[Any]) -> tuple[str, str]:
        return ("unsetenv", items[0])

    # Phase 13 Batch 3 - Lua Global Directives
    def global_lua_load(self, items: list[Any]) -> tuple[str, tuple[str, list[str]]]:
        """Phase 13 Batch 3 - Load Lua file in shared context."""
        file_path = items[0]
        args = list(items[1:]) if len(items) > 1 else []
        return ("lua_load", (file_path, args))

    def global_lua_load_per_thread(self, items: list[Any]) -> tuple[str, tuple[str, list[str]]]:
        """Phase 13 Batch 3 - Load Lua file per thread."""
        file_path = items[0]
        args = list(items[1:]) if len(items) > 1 else []
        return ("lua_load_per_thread", (file_path, args))

    def global_lua_prepend_path(self, items: list[Any]) -> tuple[str, tuple[str, str]]:
        """Phase 13 Batch 3 - Prepend to Lua's package.path or package.cpath."""
        path = items[0]
        path_type = items[1] if len(items) > 1 else "path"  # Default to "path"
        return ("lua_prepend_path", (path, path_type))

    # Phase 2 global directives - Buffer and performance tuning
    def global_maxpipes(self, items: list[Any]) -> tuple[str, int]:
        return ("maxpipes", items[0])

    def global_tune_bufsize(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_bufsize", items[0])

    def global_tune_maxrewrite(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_maxrewrite", items[0])

    # Phase 2 - SSL/TLS Phase 2 directives
    def global_key_base(self, items: list[Any]) -> tuple[str, str]:
        return ("key_base", items[0])

    def global_ssl_default_bind_ciphersuites(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_default_bind_ciphersuites", items[0])

    def global_ssl_default_server_ciphersuites(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_default_server_ciphersuites", items[0])

    def global_ssl_default_server_options(self, items: list[Any]) -> tuple[str, list[str]]:
        return ("ssl_default_server_options", items[0])

    def global_ssl_engine(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_engine", items[0])

    # Phase 13 Batch 4 - SSL Advanced Configuration
    def global_ssl_default_bind_curves(self, items: list[Any]) -> tuple[str, str]:
        """Phase 13 Batch 4 - SSL/TLS elliptic curves for bind."""
        return ("ssl_default_bind_curves", items[0])

    def global_ssl_default_bind_sigalgs(self, items: list[Any]) -> tuple[str, str]:
        """Phase 13 Batch 4 - SSL/TLS signature algorithms for bind."""
        return ("ssl_default_bind_sigalgs", items[0])

    def global_ssl_default_bind_client_sigalgs(self, items: list[Any]) -> tuple[str, str]:
        """Phase 13 Batch 4 - SSL/TLS client signature algorithms for bind."""
        return ("ssl_default_bind_client_sigalgs", items[0])

    def global_ssl_default_server_curves(self, items: list[Any]) -> tuple[str, str]:
        """Phase 13 Batch 4 - SSL/TLS elliptic curves for server."""
        return ("ssl_default_server_curves", items[0])

    def global_ssl_default_server_sigalgs(self, items: list[Any]) -> tuple[str, str]:
        """Phase 13 Batch 4 - SSL/TLS signature algorithms for server."""
        return ("ssl_default_server_sigalgs", items[0])

    def global_ssl_default_server_client_sigalgs(self, items: list[Any]) -> tuple[str, str]:
        """Phase 13 Batch 4 - SSL/TLS client signature algorithms for server."""
        return ("ssl_default_server_client_sigalgs", items[0])

    def global_ssl_security_level(self, items: list[Any]) -> tuple[str, int]:
        """Phase 13 Batch 4 - OpenSSL security level."""
        return ("ssl_security_level", items[0])

    # Phase 2 - Master-worker mode
    def global_master_worker(self, items: list[Any]) -> tuple[str, bool]:
        return ("master_worker", items[0])

    def global_mworker_max_reloads(self, items: list[Any]) -> tuple[str, int]:
        return ("mworker_max_reloads", items[0])

    # Phase 2 - SSL tuning directives
    def global_tune_ssl_bufsize(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_bufsize", items[0])

    def global_tune_ssl_cachesize(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_cachesize", items[0])

    def global_tune_ssl_lifetime(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_ssl_lifetime", items[0])

    def global_tune_ssl_maxrecord(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_maxrecord", items[0])

    def global_tune_ssl_keylog(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_ssl_keylog", items[0])

    def global_tune_ssl_capture_cipherlist_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_capture_cipherlist_size", items[0])

    def global_tune_ssl_capture_buffer_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_capture_buffer_size", items[0])

    def global_tune_ssl_default_dh_param(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_default_dh_param", items[0])

    def global_tune_ssl_ocsp_update_minthour(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_ocsp_update_minthour", items[0])

    def global_tune_ssl_ocsp_update_maxhour(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ssl_ocsp_update_maxhour", items[0])

    def global_tune_ssl_ocsp_update_maxdelay(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 4 - SSL OCSP update max delay."""
        return ("tune_ssl_ocsp_update_maxdelay", items[0])

    def global_tune_ssl_ocsp_update_mindelay(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 4 - SSL OCSP update min delay."""
        return ("tune_ssl_ocsp_update_mindelay", items[0])

    def global_tune_ssl_hard_maxrecord(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 4 - SSL hard max record size."""
        return ("tune_ssl_hard_maxrecord", items[0])

    def global_tune_ssl_ctx_cache_size(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 4 - SSL context cache size."""
        return ("tune_ssl_ssl_ctx_cache_size", items[0])

    # Phase 2 - HTTP/2 tuning directives
    def global_tune_h2_be_glitches_threshold(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_be_glitches_threshold", items[0])

    def global_tune_h2_be_initial_window_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_be_initial_window_size", items[0])

    def global_tune_h2_be_max_concurrent_streams(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_be_max_concurrent_streams", items[0])

    def global_tune_h2_be_rxbuf(self, items: list[Any]) -> tuple[str, int]:
        """Phase 13 Batch 1 - HTTP/2 backend receive buffer."""
        return ("tune_h2_be_rxbuf", items[0])

    def global_tune_h2_fe_glitches_threshold(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_glitches_threshold", items[0])

    def global_tune_h2_fe_initial_window_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_initial_window_size", items[0])

    def global_tune_h2_fe_max_concurrent_streams(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_max_concurrent_streams", items[0])

    def global_tune_h2_fe_max_total_streams(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_max_total_streams", items[0])

    def global_tune_h2_fe_rxbuf(self, items: list[Any]) -> tuple[str, int]:
        """Phase 13 Batch 1 - HTTP/2 frontend receive buffer."""
        return ("tune_h2_fe_rxbuf", items[0])

    def global_tune_h2_header_table_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_header_table_size", items[0])

    def global_tune_h2_initial_window_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_initial_window_size", items[0])

    def global_tune_h2_max_concurrent_streams(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_max_concurrent_streams", items[0])

    def global_tune_h2_max_frame_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_max_frame_size", items[0])

    # Phase 2 - HTTP tuning directives
    def global_tune_http_maxhdr(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_http_maxhdr", items[0])

    def global_tune_http_cookielen(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_http_cookielen", items[0])

    def global_tune_http_logurilen(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_http_logurilen", items[0])

    # Phase 3 - Memory tuning directives
    def global_tune_memory_pool_allocator(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_memory_pool_allocator", items[0])

    def global_tune_memory_fail_alloc(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_memory_fail_alloc", items[0])

    def global_tune_buffers_limit(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_buffers_limit", items[0])

    def global_tune_buffers_reserve(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_buffers_reserve", items[0])

    # Phase 3 - Performance tuning
    def global_tune_fd_edge_triggered(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_fd_edge_triggered", items[0])

    def global_tune_comp_maxlevel(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_comp_maxlevel", items[0])

    # Phase 3 - System integration
    def global_uid(self, items: list[Any]) -> tuple[str, int]:
        return ("uid", items[0])

    def global_gid(self, items: list[Any]) -> tuple[str, int]:
        return ("gid", items[0])

    def global_setcap(self, items: list[Any]) -> tuple[str, str]:
        return ("setcap", items[0])

    def global_set_dumpable(self, items: list[Any]) -> tuple[str, bool]:
        return ("set_dumpable", items[0])

    def global_unix_bind(self, items: list[Any]) -> tuple[str, str]:
        return ("unix_bind", items[0])

    def global_cpu_map(self, items: list[Any]) -> tuple[str, tuple[str, str]]:
        # cpu-map process/thread cpu_list
        return ("cpu_map", (items[0], items[1]))

    # Phase 3 - Advanced options
    def global_hard_stop_after(self, items: list[Any]) -> tuple[str, str]:
        return ("hard_stop_after", items[0])

    def global_node(self, items: list[Any]) -> tuple[str, str]:
        return ("node", items[0])

    def global_description(self, items: list[Any]) -> tuple[str, str]:
        return ("description", items[0])

    def global_external_check(self, items: list[Any]) -> tuple[str, bool]:
        return ("external_check", items[0])

    def global_numa_cpu_mapping(self, items: list[Any]) -> tuple[str, bool]:
        return ("numa_cpu_mapping", items[0])

    # Phase 4A - Performance & Runtime directives
    def global_busy_polling(self, items: list[Any]) -> tuple[str, bool]:
        return ("busy_polling", items[0])

    def global_max_spread_checks(self, items: list[Any]) -> tuple[str, int]:
        return ("max_spread_checks", items[0])

    def global_spread_checks(self, items: list[Any]) -> tuple[str, int]:
        return ("spread_checks", items[0])

    def global_maxcompcpuusage(self, items: list[Any]) -> tuple[str, int]:
        return ("maxcompcpuusage", items[0])

    def global_maxcomprate(self, items: list[Any]) -> tuple[str, int]:
        return ("maxcomprate", items[0])

    def global_tune_idle_pool_shared(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_idle_pool_shared", items[0])

    def global_tune_pattern_cache_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_pattern_cache_size", items[0])

    def global_tune_stick_counters(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_stick_counters", items[0])

    def global_default_path(self, items: list[Any]) -> tuple[str, str]:
        return ("default_path", items[0])

    # Phase 10 Batch 3 - Server State Management directives
    def global_server_state_base(self, items: list[Any]) -> tuple[str, str]:
        return ("server_state_base", items[0])

    def global_server_state_file(self, items: list[Any]) -> tuple[str, str]:
        return ("server_state_file", items[0])

    def global_load_server_state_from_file(self, items: list[Any]) -> tuple[str, str]:
        return ("load_server_state_from_file", items[0])

    # Phase 4A - Lua Configuration directives
    def global_tune_lua_forced_yield(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_lua_forced_yield", items[0])

    def global_tune_lua_maxmem(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_lua_maxmem", items[0])

    def global_tune_lua_session_timeout(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_lua_session_timeout", items[0])

    def global_tune_lua_task_timeout(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_lua_task_timeout", items[0])

    def global_tune_lua_service_timeout(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_lua_service_timeout", items[0])

    def global_tune_lua_log_loggers(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_lua_log_loggers", items[0])

    def global_tune_lua_bool_sample_conversion(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 5 - Lua boolean sample conversion."""
        return ("tune_lua_bool_sample_conversion", items[0])

    def global_tune_lua_burst_timeout(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 5 - Lua burst timeout in milliseconds."""
        return ("tune_lua_burst_timeout", items[0])

    def global_tune_lua_log_stderr(self, items: list[Any]) -> tuple[str, str]:
        """Phase 12 Batch 5 - Lua log to stderr (on/off/auto)."""
        return ("tune_lua_log_stderr", items[0])

    # Phase 4A - Variables Configuration directives
    def global_tune_vars_global_max_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_vars_global_max_size", items[0])

    def global_tune_vars_proc_max_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_vars_proc_max_size", items[0])

    def global_tune_vars_reqres_max_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_vars_reqres_max_size", items[0])

    def global_tune_vars_sess_max_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_vars_sess_max_size", items[0])

    def global_tune_vars_txn_max_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_vars_txn_max_size", items[0])

    # Phase 4A - Connection Pool directives
    def global_tune_pool_high_fd_ratio(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_pool_high_fd_ratio", items[0])

    def global_tune_pool_low_fd_ratio(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_pool_low_fd_ratio", items[0])

    # Phase 4A - Socket Buffers directives
    def global_tune_rcvbuf_client(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_rcvbuf_client", items[0])

    def global_tune_rcvbuf_server(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_rcvbuf_server", items[0])

    def global_tune_sndbuf_client(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_sndbuf_client", items[0])

    def global_tune_sndbuf_server(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_sndbuf_server", items[0])

    # Phase 6 - Performance Tuning directives
    def global_tune_rcvbuf_frontend(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_rcvbuf_frontend", items[0])

    def global_tune_rcvbuf_backend(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_rcvbuf_backend", items[0])

    def global_tune_sndbuf_frontend(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_sndbuf_frontend", items[0])

    def global_tune_sndbuf_backend(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_sndbuf_backend", items[0])

    def global_tune_maxaccept(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_maxaccept", items[0])

    def global_tune_maxpollevents(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_maxpollevents", items[0])

    def global_tune_bufsize_small(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_bufsize_small", items[0])

    def global_tune_pipesize(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_pipesize", items[0])

    def global_tune_recv_enough(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_recv_enough", items[0])

    def global_tune_idletimer(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_idletimer", items[0])

    def global_tune_runqueue_depth(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_runqueue_depth", items[0])

    def global_tune_sched_low_latency(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_sched_low_latency", items[0])

    def global_tune_max_checks_per_thread(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_max_checks_per_thread", items[0])

    def global_tune_max_rules_at_once(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_max_rules_at_once", items[0])

    def global_tune_disable_fast_forward(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_disable_fast_forward", items[0])

    def global_tune_disable_zero_copy_forwarding(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_disable_zero_copy_forwarding", items[0])

    def global_tune_events_max_events_at_once(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_events_max_events_at_once", items[0])

    def global_tune_memory_hot_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_memory_hot_size", items[0])

    def global_tune_peers_max_updates_at_once(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_peers_max_updates_at_once", items[0])

    def global_tune_ring_queues(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_ring_queues", items[0])

    def global_tune_epoll_mask_events(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 6 - Epoll mask events."""
        return ("tune_epoll_mask_events", items[0])

    def global_tune_fail_alloc(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 6 - Fail allocation threshold."""
        return ("tune_fail_alloc", items[0])

    def global_tune_renice_runtime(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 6 - Renice priority at runtime."""
        return ("tune_renice_runtime", items[0])

    def global_tune_renice_startup(self, items: list[Any]) -> tuple[str, int]:
        """Phase 12 Batch 6 - Renice priority at startup."""
        return ("tune_renice_startup", items[0])

    def global_tune_takeover_other_tg_connections(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 6 - Takeover connections from other thread groups."""
        return ("tune_takeover_other_tg_connections", items[0])

    def global_tune_applet_zero_copy_forwarding(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_applet_zero_copy_forwarding", items[0])

    def global_tune_h1_zero_copy_fwd_recv(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 6 - H1 zero-copy forwarding receive."""
        return ("tune_h1_zero_copy_fwd_recv", items[0])

    def global_tune_h1_zero_copy_fwd_send(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 6 - H1 zero-copy forwarding send."""
        return ("tune_h1_zero_copy_fwd_send", items[0])

    def global_tune_pt_zero_copy_forwarding(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 6 - Pass-through zero-copy forwarding."""
        return ("tune_pt_zero_copy_forwarding", items[0])

    def global_tune_ssl_force_private_cache(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_ssl_force_private_cache", items[0])

    # Phase 4B Part 1 - HTTP Client Configuration directives
    def global_httpclient_resolvers_disabled(self, items: list[Any]) -> tuple[str, bool]:
        return ("httpclient_resolvers_disabled", items[0])

    def global_httpclient_resolvers_id(self, items: list[Any]) -> tuple[str, str]:
        return ("httpclient_resolvers_id", items[0])

    def global_httpclient_resolvers_prefer(self, items: list[Any]) -> tuple[str, str]:
        return ("httpclient_resolvers_prefer", items[0])

    def global_httpclient_retries(self, items: list[Any]) -> tuple[str, int]:
        return ("httpclient_retries", items[0])

    def global_httpclient_ssl_verify(self, items: list[Any]) -> tuple[str, str]:
        return ("httpclient_ssl_verify", items[0])

    def global_httpclient_ssl_ca_file(self, items: list[Any]) -> tuple[str, str]:
        return ("httpclient_ssl_ca_file", items[0])

    def global_httpclient_timeout_connect(self, items: list[Any]) -> tuple[str, str]:
        """Phase 12 Batch 3 - HTTPClient timeout.connect directive."""
        return ("httpclient_timeout_connect", items[0])

    # Phase 4B Part 1 - Platform-Specific Options directives
    def global_noepoll(self, items: list[Any]) -> tuple[str, bool]:
        return ("noepoll", items[0])

    def global_nokqueue(self, items: list[Any]) -> tuple[str, bool]:
        return ("nokqueue", items[0])

    def global_nopoll(self, items: list[Any]) -> tuple[str, bool]:
        return ("nopoll", items[0])

    def global_nosplice(self, items: list[Any]) -> tuple[str, bool]:
        return ("nosplice", items[0])

    def global_nogetaddrinfo(self, items: list[Any]) -> tuple[str, bool]:
        return ("nogetaddrinfo", items[0])

    def global_noreuseport(self, items: list[Any]) -> tuple[str, bool]:
        return ("noreuseport", items[0])

    def global_limited_quic(self, items: list[Any]) -> tuple[str, bool]:
        return ("limited_quic", items[0])

    def global_localpeer(self, items: list[Any]) -> tuple[str, str]:
        return ("localpeer", items[0])

    def global_noevports(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 6 - Disable evports polling."""
        return ("noevports", items[0])

    def global_noktls(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 6 - Disable kernel TLS."""
        return ("noktls", items[0])

    def global_no_memory_trimming(self, items: list[Any]) -> tuple[str, bool]:
        """Phase 12 Batch 6 - Disable memory trimming."""
        return ("no_memory_trimming", items[0])

    # Phase 4B Part 2 - SSL Advanced directives
    def global_ssl_load_extra_files(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_load_extra_files", items[0])

    def global_ssl_load_extra_del_ext(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_load_extra_del_ext", items[0])

    def global_ssl_mode_async(self, items: list[Any]) -> tuple[str, bool]:
        return ("ssl_mode_async", items[0])

    def global_ssl_propquery(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_propquery", items[0])

    def global_ssl_provider(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_provider", items[0])

    def global_ssl_provider_path(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_provider_path", items[0])

    def global_issuers_chain_path(self, items: list[Any]) -> tuple[str, str]:
        return ("issuers_chain_path", items[0])

    # Phase 4B Part 2 - Profiling & Debugging directives
    def global_profiling_tasks_on(self, items: list[Any]) -> tuple[str, bool]:
        return ("profiling_tasks_on", items[0])

    def global_profiling_tasks_automatic(self, items: list[Any]) -> tuple[str, bool]:
        return ("profiling_tasks_automatic", items[0])

    def global_profiling_memory_on(self, items: list[Any]) -> tuple[str, bool]:
        return ("profiling_memory_on", items[0])

    def global_profiling_memory(self, items: list[Any]) -> tuple[str, str]:
        """Phase 12 Batch 6 - Profiling memory (on/off)."""
        return ("profiling_memory", items[0])

    def global_profiling_tasks(self, items: list[Any]) -> tuple[str, str]:
        """Phase 12 Batch 6 - Profiling tasks (on/off)."""
        return ("profiling_tasks", items[0])

    # Phase 7 - Debugging & Development directives
    def global_quiet(self, items: list[Any]) -> tuple[str, bool]:
        return ("quiet", items[0])

    def global_debug_counters(self, items: list[Any]) -> tuple[str, str]:
        return ("debug_counters", items[0])

    def global_anonkey(self, items: list[Any]) -> tuple[str, int]:
        return ("anonkey", items[0])

    def global_zero_warning(self, items: list[Any]) -> tuple[str, bool]:
        return ("zero_warning", items[0])

    def global_warn_blocked_traffic_after(self, items: list[Any]) -> tuple[str, str]:
        return ("warn_blocked_traffic_after", items[0])

    def global_force_cfg_parser_pause(self, items: list[Any]) -> tuple[str, bool]:
        return ("force_cfg_parser_pause", items[0])

    # Phase 4B Part 3 - QUIC/HTTP3 Support directives
    def global_tune_quic_frontend_conn_tx_buffers_limit(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_quic_frontend_conn_tx_buffers_limit", items[0])

    def global_tune_quic_frontend_max_idle_timeout(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_quic_frontend_max_idle_timeout", items[0])

    def global_tune_quic_frontend_max_streams_bidi(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_quic_frontend_max_streams_bidi", items[0])

    def global_tune_quic_frontend_glitches_threshold(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_quic_frontend_glitches_threshold", items[0])

    def global_tune_quic_retry_threshold(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_quic_retry_threshold", items[0])

    def global_tune_quic_socket_owner(self, items: list[Any]) -> tuple[str, str]:
        return ("tune_quic_socket_owner", items[0])

    def global_tune_quic_max_frame_loss(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_quic_max_frame_loss", items[0])

    # Phase 8 - Additional QUIC/HTTP3 directives
    def global_tune_quic_cc_hystart(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_quic_cc_hystart", items[0])

    def global_tune_quic_reorder_ratio(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_quic_reorder_ratio", items[0])

    def global_tune_quic_zero_copy_fwd_send(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_quic_zero_copy_fwd_send", items[0])

    def global_tune_h2_zero_copy_fwd_send(self, items: list[Any]) -> tuple[str, bool]:
        return ("tune_h2_zero_copy_fwd_send", items[0])

    # Phase 13 Batch 2 - Modern QUIC Backend Directives (12 methods)
    def global_tune_quic_be_cc_cubic_min_losses(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend cubic congestion control minimum losses."""
        return ("tune_quic_be_cc_cubic_min_losses", items[0])

    def global_tune_quic_be_cc_hystart(self, items: list[Any]) -> tuple[str, bool]:
        """QUIC backend hystart congestion control."""
        return ("tune_quic_be_cc_hystart", items[0])

    def global_tune_quic_be_cc_max_frame_loss(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend maximum frame loss."""
        return ("tune_quic_be_cc_max_frame_loss", items[0])

    def global_tune_quic_be_cc_max_win_size(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend maximum window size."""
        return ("tune_quic_be_cc_max_win_size", items[0])

    def global_tune_quic_be_cc_reorder_ratio(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend reorder ratio (0-100 percent)."""
        return ("tune_quic_be_cc_reorder_ratio", items[0])

    def global_tune_quic_be_max_idle_timeout(self, items: list[Any]) -> tuple[str, str]:
        """QUIC backend maximum idle timeout."""
        return ("tune_quic_be_max_idle_timeout", items[0])

    def global_tune_quic_be_sec_glitches_threshold(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend security glitches threshold."""
        return ("tune_quic_be_sec_glitches_threshold", items[0])

    def global_tune_quic_be_stream_data_ratio(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend stream data ratio (0-100 percent)."""
        return ("tune_quic_be_stream_data_ratio", items[0])

    def global_tune_quic_be_stream_max_concurrent(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend maximum concurrent streams."""
        return ("tune_quic_be_stream_max_concurrent", items[0])

    def global_tune_quic_be_stream_rxbuf(self, items: list[Any]) -> tuple[str, int]:
        """QUIC backend stream receive buffer size."""
        return ("tune_quic_be_stream_rxbuf", items[0])

    def global_tune_quic_be_tx_pacing(self, items: list[Any]) -> tuple[str, bool]:
        """QUIC backend TX pacing."""
        return ("tune_quic_be_tx_pacing", items[0])

    def global_tune_quic_be_tx_udp_gso(self, items: list[Any]) -> tuple[str, bool]:
        """QUIC backend UDP GSO (Generic Segmentation Offload)."""
        return ("tune_quic_be_tx_udp_gso", items[0])

    # Phase 13 Batch 2 - Modern QUIC Frontend Directives (14 methods)
    def global_tune_quic_fe_cc_cubic_min_losses(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend cubic congestion control minimum losses."""
        return ("tune_quic_fe_cc_cubic_min_losses", items[0])

    def global_tune_quic_fe_cc_hystart(self, items: list[Any]) -> tuple[str, bool]:
        """QUIC frontend hystart congestion control."""
        return ("tune_quic_fe_cc_hystart", items[0])

    def global_tune_quic_fe_cc_max_frame_loss(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend maximum frame loss."""
        return ("tune_quic_fe_cc_max_frame_loss", items[0])

    def global_tune_quic_fe_cc_max_win_size(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend maximum window size."""
        return ("tune_quic_fe_cc_max_win_size", items[0])

    def global_tune_quic_fe_cc_reorder_ratio(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend reorder ratio (0-100 percent)."""
        return ("tune_quic_fe_cc_reorder_ratio", items[0])

    def global_tune_quic_fe_max_idle_timeout(self, items: list[Any]) -> tuple[str, str]:
        """QUIC frontend maximum idle timeout."""
        return ("tune_quic_fe_max_idle_timeout", items[0])

    def global_tune_quic_fe_sec_glitches_threshold(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend security glitches threshold."""
        return ("tune_quic_fe_sec_glitches_threshold", items[0])

    def global_tune_quic_fe_sec_retry_threshold(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend security retry threshold."""
        return ("tune_quic_fe_sec_retry_threshold", items[0])

    def global_tune_quic_fe_sock_per_conn(self, items: list[Any]) -> tuple[str, str]:
        """QUIC frontend socket per connection (default-on/force-off)."""
        return ("tune_quic_fe_sock_per_conn", items[0])

    def global_tune_quic_fe_stream_data_ratio(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend stream data ratio (0-100 percent)."""
        return ("tune_quic_fe_stream_data_ratio", items[0])

    def global_tune_quic_fe_stream_max_concurrent(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend maximum concurrent streams."""
        return ("tune_quic_fe_stream_max_concurrent", items[0])

    def global_tune_quic_fe_stream_rxbuf(self, items: list[Any]) -> tuple[str, int]:
        """QUIC frontend stream receive buffer size."""
        return ("tune_quic_fe_stream_rxbuf", items[0])

    def global_tune_quic_fe_tx_pacing(self, items: list[Any]) -> tuple[str, bool]:
        """QUIC frontend TX pacing."""
        return ("tune_quic_fe_tx_pacing", items[0])

    def global_tune_quic_fe_tx_udp_gso(self, items: list[Any]) -> tuple[str, bool]:
        """QUIC frontend UDP GSO (Generic Segmentation Offload)."""
        return ("tune_quic_fe_tx_udp_gso", items[0])

    # Phase 13 Batch 2 - QUIC Global Directives (2 methods)
    def global_tune_quic_listen(self, items: list[Any]) -> tuple[str, bool]:
        """QUIC listen on all bind addresses."""
        return ("tune_quic_listen", items[0])

    def global_tune_quic_mem_tx_max(self, items: list[Any]) -> tuple[str, int]:
        """QUIC maximum TX memory."""
        return ("tune_quic_mem_tx_max", items[0])

    # Phase 4B Part 4 - Device Detection directives
    # DeviceAtlas
    def global_deviceatlas_json_file(self, items: list[Any]) -> tuple[str, str]:
        return ("deviceatlas_json_file", items[0])

    def global_deviceatlas_log_level(self, items: list[Any]) -> tuple[str, int]:
        return ("deviceatlas_log_level", items[0])

    def global_deviceatlas_separator(self, items: list[Any]) -> tuple[str, str]:
        return ("deviceatlas_separator", items[0])

    def global_deviceatlas_properties_cookie(self, items: list[Any]) -> tuple[str, str]:
        return ("deviceatlas_properties_cookie", items[0])

    # 51Degrees
    def global_51degrees_data_file(self, items: list[Any]) -> tuple[str, str]:
        return ("fiftyone_degrees_data_file", items[0])

    def global_51degrees_property_name_list(self, items: list[Any]) -> tuple[str, str]:
        return ("fiftyone_degrees_property_name_list", items[0])

    def global_51degrees_property_separator(self, items: list[Any]) -> tuple[str, str]:
        return ("fiftyone_degrees_property_separator", items[0])

    def global_51degrees_cache_size(self, items: list[Any]) -> tuple[str, int]:
        return ("fiftyone_degrees_cache_size", items[0])

    # WURFL
    def global_wurfl_data_file(self, items: list[Any]) -> tuple[str, str]:
        return ("wurfl_data_file", items[0])

    def global_wurfl_information_list(self, items: list[Any]) -> tuple[str, str]:
        return ("wurfl_information_list", items[0])

    def global_wurfl_information_list_separator(self, items: list[Any]) -> tuple[str, str]:
        return ("wurfl_information_list_separator", items[0])

    def global_wurfl_patch_file(self, items: list[Any]) -> tuple[str, str]:
        return ("wurfl_patch_file", items[0])

    def global_wurfl_cache_size(self, items: list[Any]) -> tuple[str, int]:
        return ("wurfl_cache_size", items[0])

    def global_wurfl_engine_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("wurfl_engine_mode", items[0])

    def global_wurfl_useragent_priority(self, items: list[Any]) -> tuple[str, str]:
        return ("wurfl_useragent_priority", items[0])

    # Compression Tuning (Final Phase - 2 directives)
    def global_tune_zlib_memlevel(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_zlib_memlevel", items[0])

    def global_tune_zlib_windowsize(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_zlib_windowsize", items[0])

    def log_target(self, items: list[Any]) -> LogTarget:
        address = items[0]
        facility = LogFacility(items[1])
        level = LogLevel(items[2])
        return LogTarget(address=address, facility=facility, level=level)

    def stats_section(self, items: list[Any]) -> StatsConfig:
        """Transform global stats section (simple version for backwards compatibility)."""
        enable = True
        uri = "/stats"
        auth_list: list[str] = []
        refresh = None

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "enable":
                    enable = value
                elif key == "uri":
                    uri = value
                elif key == "auth":
                    # Convert single auth string to list for compatibility with new StatsConfig
                    auth_list = [value] if value else []
                elif key == "refresh":
                    refresh = value

        # Use the comprehensive StatsConfig with basic values
        return StatsConfig(
            enable=enable,
            uri=uri,
            auth=auth_list,
            refresh=refresh,
        )

    def stats_enable(self, items: list[Any]) -> tuple[str, bool]:
        """Transform stats enable (works for both global and proxy stats)."""
        # If items provided, use the boolean value; otherwise default to True
        return ("enable", items[0] if items else True)

    def stats_uri(self, items: list[Any]) -> tuple[str, str]:
        return ("uri", str(items[0]))

    def stats_auth(self, items: list[Any]) -> tuple[str, str]:
        return ("auth", str(items[0]))

    # ===== Stats Socket (Runtime API) =====
    def global_stats_socket(self, items: list[Any]) -> StatsSocket:
        """Transform stats_socket from global section."""
        return cast("StatsSocket", items[0])

    def stats_socket_item(self, items: list[Any]) -> StatsSocket:
        """Build StatsSocket from path and optional parameters block."""
        path = str(items[0])
        level = "operator"  # Default level
        mode = None
        user = None
        group = None
        process = None

        # Process optional parameters (items after the path are tuples from the param block)
        for item in items[1:]:
            if isinstance(item, tuple):
                key, value = item
                if key == "level":
                    level = value
                elif key == "mode":
                    mode = value
                elif key == "user":
                    user = value
                elif key == "group":
                    group = value
                elif key == "process":
                    process = value

        return StatsSocket(
            path=path,
            level=level,
            mode=mode,
            user=user,
            group=group,
            process=process,
        )

    def stats_socket_level(self, items: list[Any]) -> tuple[str, str]:
        return ("level", str(items[0]))

    def stats_socket_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", str(items[0]))

    def stats_socket_user(self, items: list[Any]) -> tuple[str, str]:
        return ("user", str(items[0]))

    def stats_socket_group(self, items: list[Any]) -> tuple[str, str]:
        return ("group", str(items[0]))

    def stats_socket_process(self, items: list[Any]) -> tuple[str, str]:
        return ("process", str(items[0]))

    # ===== Peers Section =====
    def peers_section(self, items: list[Any]) -> PeersSection:
        """Transform peers section for stick table replication."""
        name = str(items[0])
        peers_list = []
        disabled = False

        for item in items[1:]:
            if isinstance(item, Peer):
                peers_list.append(item)
            elif isinstance(item, tuple):
                key, value = item
                if key == "disabled":
                    disabled = value

        return PeersSection(name=name, peers=peers_list, disabled=disabled)

    def peer_definition(self, items: list[Any]) -> Peer:
        """Transform individual peer definition."""
        name = str(items[0])
        address = str(items[1])
        port = int(items[2])
        return Peer(name=name, address=address, port=port)

    def peers_disabled(self, items: list[Any]) -> tuple[str, bool]:
        return ("disabled", items[0])

    # ===== Resolvers Section =====
    def resolvers_section(self, items: list[Any]) -> ResolversSection:
        """Transform resolvers section for DNS resolution."""
        name = str(items[0])
        nameservers = []
        accepted_payload_size = None
        hold_nx = None
        hold_obsolete = None
        hold_other = None
        hold_refused = None
        hold_timeout = None
        hold_valid = None
        resolve_retries = None
        timeout_resolve = None
        timeout_retry = None

        for item in items[1:]:
            if isinstance(item, Nameserver):
                nameservers.append(item)
            elif isinstance(item, tuple):
                key, value = item
                if key == "accepted_payload_size":
                    accepted_payload_size = value
                elif key == "hold_nx":
                    hold_nx = value
                elif key == "hold_obsolete":
                    hold_obsolete = value
                elif key == "hold_other":
                    hold_other = value
                elif key == "hold_refused":
                    hold_refused = value
                elif key == "hold_timeout":
                    hold_timeout = value
                elif key == "hold_valid":
                    hold_valid = value
                elif key == "resolve_retries":
                    resolve_retries = value
                elif key == "timeout_resolve":
                    timeout_resolve = value
                elif key == "timeout_retry":
                    timeout_retry = value

        return ResolversSection(
            name=name,
            nameservers=nameservers,
            accepted_payload_size=accepted_payload_size,
            hold_nx=hold_nx,
            hold_obsolete=hold_obsolete,
            hold_other=hold_other,
            hold_refused=hold_refused,
            hold_timeout=hold_timeout,
            hold_valid=hold_valid,
            resolve_retries=resolve_retries,
            timeout_resolve=timeout_resolve,
            timeout_retry=timeout_retry,
        )

    def nameserver_definition(self, items: list[Any]) -> Nameserver:
        """Transform individual nameserver definition."""
        name = str(items[0])
        address = str(items[1])
        port = int(items[2])
        return Nameserver(name=name, address=address, port=port)

    def resolvers_accepted_payload_size(self, items: list[Any]) -> tuple[str, int]:
        return ("accepted_payload_size", items[0])

    def resolvers_hold_nx(self, items: list[Any]) -> tuple[str, str]:
        return ("hold_nx", str(items[0]))

    def resolvers_hold_obsolete(self, items: list[Any]) -> tuple[str, str]:
        return ("hold_obsolete", str(items[0]))

    def resolvers_hold_other(self, items: list[Any]) -> tuple[str, str]:
        return ("hold_other", str(items[0]))

    def resolvers_hold_refused(self, items: list[Any]) -> tuple[str, str]:
        return ("hold_refused", str(items[0]))

    def resolvers_hold_timeout(self, items: list[Any]) -> tuple[str, str]:
        return ("hold_timeout", str(items[0]))

    def resolvers_hold_valid(self, items: list[Any]) -> tuple[str, str]:
        return ("hold_valid", str(items[0]))

    def resolvers_resolve_retries(self, items: list[Any]) -> tuple[str, int]:
        return ("resolve_retries", items[0])

    def resolvers_timeout_resolve(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_resolve", str(items[0]))

    def resolvers_timeout_retry(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_retry", str(items[0]))

    # ===== Mailers Section =====
    def mailers_section(self, items: list[Any]) -> MailersSection:
        """Transform mailers section for email alerts."""
        name = str(items[0])
        mailers_list = []
        timeout_mail = None

        for item in items[1:]:
            if isinstance(item, Mailer):
                mailers_list.append(item)
            elif isinstance(item, tuple):
                key, value = item
                if key == "timeout_mail":
                    timeout_mail = value

        return MailersSection(name=name, mailers=mailers_list, timeout_mail=timeout_mail)

    def mailer_definition(self, items: list[Any]) -> Mailer:
        """Transform individual mailer definition."""
        name = str(items[0])
        address = str(items[1])
        port = int(items[2])
        return Mailer(name=name, address=address, port=port)

    def mailers_timeout_mail(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_mail", str(items[0]))

    def lua_section(self, items: list[Any]) -> list[LuaScript]:
        scripts = []
        for item in items:
            if isinstance(item, LuaScript):
                scripts.append(item)
        return scripts

    def lua_load(self, items: list[Any]) -> LuaScript:
        path = items[0]
        return LuaScript(source_type="file", content=path)

    def lua_script(self, items: list[Any]) -> LuaScript:
        name = str(items[0])
        code = str(items[-1])  # Last item is always LUA_CODE

        # Check if there are parameters (if len > 2, params are in the middle)
        parameters = {}
        if len(items) > 2:
            # Parse parameters
            param_items = items[1:-1]
            for i in range(0, len(param_items), 2):
                param_name = str(param_items[i])
                param_value = str(param_items[i + 1]) if i + 1 < len(param_items) else ""
                parameters[param_name] = param_value

        return LuaScript(name=name, source_type="inline", content=code, parameters=parameters)

    # ===== Defaults Section =====
    def defaults_section(self, items: list[Any]) -> DefaultsConfig:
        mode = Mode.HTTP
        retries = 3
        timeout_connect = "5s"
        timeout_client = "50s"
        timeout_server = "50s"
        timeout_check = None
        timeout_http_request = None
        timeout_http_keep_alive = None
        timeout_tunnel = None
        timeout_client_fin = None
        timeout_server_fin = None
        timeout_tarpit = None
        log = "global"
        options = []
        errorloc = {}
        errorloc302 = {}
        errorloc303 = {}
        error_log_format = None
        log_steps = None
        email_alert = None
        rate_limit_sessions = None  # Phase 5B
        # TCP keepalive (Phase 5B)
        clitcpka_cnt = None
        clitcpka_idle = None
        clitcpka_intvl = None
        srvtcpka_cnt = None
        srvtcpka_idle = None
        srvtcpka_intvl = None
        persist_rdp_cookie = None
        quic_initial_rules = []

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "mode":
                    mode = Mode(value)
                elif key == "retries":
                    retries = value
                elif key == "log":
                    log = value
                elif key == "option":
                    if isinstance(value, list):
                        options.extend(value)
                    else:
                        options.append(value)
                elif key == "clitcpka_cnt":
                    clitcpka_cnt = value
                elif key == "clitcpka_idle":
                    clitcpka_idle = value
                elif key == "clitcpka_intvl":
                    clitcpka_intvl = value
                elif key == "srvtcpka_cnt":
                    srvtcpka_cnt = value
                elif key == "srvtcpka_idle":
                    srvtcpka_idle = value
                elif key == "srvtcpka_intvl":
                    srvtcpka_intvl = value
                elif key == "persist_rdp_cookie":
                    persist_rdp_cookie = value  # Empty string means use default "msts"
                elif key == "rate_limit_sessions":
                    rate_limit_sessions = value
                elif key == "errorloc":
                    code, url = value
                    errorloc[code] = url
                elif key == "errorloc302":
                    code, url = value
                    errorloc302[code] = url
                elif key == "errorloc303":
                    code, url = value
                    errorloc303[code] = url
                elif key == "error_log_format":
                    error_log_format = value
                elif key == "log_steps":
                    log_steps = value
                elif key == "timeout":
                    for timeout_key, timeout_value in value.items():
                        if timeout_key == "connect":
                            timeout_connect = timeout_value
                        elif timeout_key == "client":
                            timeout_client = timeout_value
                        elif timeout_key == "server":
                            timeout_server = timeout_value
                        elif timeout_key == "check":
                            timeout_check = timeout_value
                        elif timeout_key == "http_request":
                            timeout_http_request = timeout_value
                        elif timeout_key == "http_keep_alive":
                            timeout_http_keep_alive = timeout_value
                        elif timeout_key == "tunnel":
                            timeout_tunnel = timeout_value
                        elif timeout_key == "client_fin":
                            timeout_client_fin = timeout_value
                        elif timeout_key == "server_fin":
                            timeout_server_fin = timeout_value
                        elif timeout_key == "tarpit":
                            timeout_tarpit = timeout_value
            elif isinstance(item, EmailAlert):
                email_alert = item
            elif isinstance(item, list) and all(isinstance(r, QuicInitialRule) for r in item):
                quic_initial_rules = item

        return DefaultsConfig(
            mode=mode,
            retries=retries,
            timeout_connect=timeout_connect,
            timeout_client=timeout_client,
            timeout_server=timeout_server,
            timeout_check=timeout_check,
            timeout_http_request=timeout_http_request,
            timeout_http_keep_alive=timeout_http_keep_alive,
            timeout_tunnel=timeout_tunnel,
            timeout_client_fin=timeout_client_fin,
            timeout_server_fin=timeout_server_fin,
            timeout_tarpit=timeout_tarpit,
            log=log,
            options=options,
            errorloc=errorloc,
            errorloc302=errorloc302,
            errorloc303=errorloc303,
            error_log_format=error_log_format,
            log_steps=log_steps,
            email_alert=email_alert,
            rate_limit_sessions=rate_limit_sessions,
            clitcpka_cnt=clitcpka_cnt,
            clitcpka_idle=clitcpka_idle,
            clitcpka_intvl=clitcpka_intvl,
            srvtcpka_cnt=srvtcpka_cnt,
            srvtcpka_idle=srvtcpka_idle,
            srvtcpka_intvl=srvtcpka_intvl,
            persist_rdp_cookie=persist_rdp_cookie,
            quic_initial_rules=quic_initial_rules,
        )

    def defaults_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

    def defaults_retries(self, items: list[Any]) -> tuple[str, int]:
        return ("retries", items[0])

    def defaults_log(self, items: list[Any]) -> tuple[str, str]:
        return ("log", items[0])

    def defaults_error_log_format(self, items: list[Any]) -> tuple[str, str]:
        """Transform error-log-format directive (custom error logging format)."""
        return ("error_log_format", str(items[0]))

    def defaults_log_steps(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-steps directive (logging steps for transaction processing)."""
        return ("log_steps", str(items[0]))

    def defaults_option(self, items: list[Any]) -> tuple[str, Any]:
        return ("option", items[0])

    def defaults_errorloc(self, items: list[Any]) -> tuple[str, tuple[int, str]]:
        return ("errorloc", (int(items[0]), str(items[1])))

    def defaults_errorloc302(self, items: list[Any]) -> tuple[str, tuple[int, str]]:
        return ("errorloc302", (int(items[0]), str(items[1])))

    def defaults_errorloc303(self, items: list[Any]) -> tuple[str, tuple[int, str]]:
        return ("errorloc303", (int(items[0]), str(items[1])))

    def defaults_timeout(self, items: list[Any]) -> tuple[str, dict[str, str]]:
        return ("timeout", items[0])

    def timeout_block(self, items: list[Any]) -> dict[str, str]:
        timeouts = {}
        for item in items:
            if isinstance(item, tuple):
                timeouts[item[0]] = item[1]
        return timeouts

    def timeout_item(self, items: list[Any]) -> tuple[str, str]:
        name = str(items[0])
        duration = str(items[1])
        return (name, duration)

    # ===== Frontend Section =====
    def frontend_section(self, items: list[Any]) -> Frontend:
        name = str(items[0])
        properties = items[1:]

        mode = Mode.HTTP
        description = None
        disabled = False
        enabled = True
        id = None
        guid = None
        binds = []
        acls = []
        filters = []
        http_request_rules = []
        http_response_rules = []
        http_after_response_rules = []
        tcp_request_rules = []
        tcp_response_rules = []
        quic_initial_rules = []
        use_backend_rules = []
        default_backend = None
        options = []
        stick_table = None
        stick_rules = []
        timeout_client = None
        timeout_http_request = None
        timeout_http_keep_alive = None
        timeout_client_fin = None
        timeout_tarpit = None
        monitor_uri = None
        monitor_net = []
        monitor_fail_rules = []
        maxconn = None
        backlog = None
        fullconn = None
        max_keep_alive_queue = None
        log = []
        log_tag = None
        log_format = None
        error_log_format = None
        log_format_sd = None
        log_steps = None
        unique_id_format = None
        unique_id_header = None
        stats_config = None
        capture_request_headers = []
        capture_response_headers = []
        redirect_rules = []
        error_files = []
        http_errors = []
        email_alert = None
        declare_captures = []
        force_persist_rules = []
        ignore_persist_rules = []
        errorloc = {}
        errorloc302 = {}
        errorloc303 = {}
        rate_limit_sessions = None  # Phase 5B
        # TCP keepalive (Phase 5B)
        clitcpka_cnt = None
        clitcpka_idle = None
        clitcpka_intvl = None

        for prop in properties:
            if isinstance(prop, Bind):
                binds.append(prop)
            elif isinstance(prop, ACL):
                acls.append(prop)
            elif isinstance(prop, RedirectRule):
                redirect_rules.append(prop)
            elif isinstance(prop, ErrorFile):
                error_files.append(prop)
            elif isinstance(prop, HttpError):
                http_errors.append(prop)
            elif isinstance(prop, EmailAlert):
                email_alert = prop
            elif isinstance(prop, DeclareCapture):
                declare_captures.append(prop)
            elif isinstance(prop, ForcePersistRule):
                force_persist_rules.append(prop)
            elif isinstance(prop, IgnorePersistRule):
                ignore_persist_rules.append(prop)
            elif isinstance(prop, StatsConfig):
                stats_config = prop
            elif isinstance(prop, MonitorFailRule):
                monitor_fail_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, ACL) for x in prop):
                acls.extend(prop)
            elif isinstance(prop, HttpRequestRule):
                http_request_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, HttpRequestRule) for x in prop):
                http_request_rules.extend(prop)
            elif isinstance(prop, HttpResponseRule):
                http_response_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, HttpResponseRule) for x in prop):
                http_response_rules.extend(prop)
            elif isinstance(prop, HttpAfterResponseRule):
                http_after_response_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, HttpAfterResponseRule) for x in prop):
                http_after_response_rules.extend(prop)
            elif isinstance(prop, TcpRequestRule):
                tcp_request_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, TcpRequestRule) for x in prop):
                tcp_request_rules.extend(prop)
            elif isinstance(prop, TcpResponseRule):
                tcp_response_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, TcpResponseRule) for x in prop):
                tcp_response_rules.extend(prop)
            elif isinstance(prop, QuicInitialRule):
                quic_initial_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, QuicInitialRule) for x in prop):
                quic_initial_rules.extend(prop)
            elif isinstance(prop, StickTable):
                stick_table = prop
            elif isinstance(prop, StickRule):
                stick_rules.append(prop)
            elif isinstance(prop, UseBackendRule):
                use_backend_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, UseBackendRule) for x in prop):
                use_backend_rules.extend(prop)
            elif isinstance(prop, list):
                # Handle routing_block which returns mixed list of UseBackendRule and tuples
                for item in prop:
                    if isinstance(item, UseBackendRule):
                        use_backend_rules.append(item)
                    elif isinstance(item, tuple):
                        key, value = item
                        if key == "default_backend":
                            default_backend = value
            elif isinstance(prop, tuple):
                key, value = prop
                if key == "mode":
                    mode = Mode(value)
                elif key == "description":
                    description = value
                elif key == "disabled":
                    disabled = value
                elif key == "enabled":
                    enabled = value
                elif key == "id":
                    id = value
                elif key == "guid":
                    guid = value
                elif key == "default_backend":
                    default_backend = value
                elif key == "option":
                    if isinstance(value, list):
                        options.extend(value)
                    else:
                        options.append(value)
                elif key == "timeout_client":
                    timeout_client = value
                elif key == "timeout_http_request":
                    timeout_http_request = value
                elif key == "timeout_http_keep_alive":
                    timeout_http_keep_alive = value
                elif key == "timeout_client_fin":
                    timeout_client_fin = value
                elif key == "timeout_tarpit":
                    timeout_tarpit = value
                elif key == "monitor_uri":
                    monitor_uri = value
                elif key == "monitor_net":
                    monitor_net.append(value)
                elif key == "maxconn":
                    maxconn = value
                elif key == "backlog":
                    backlog = value
                elif key == "fullconn":
                    fullconn = value
                elif key == "max_keep_alive_queue":
                    max_keep_alive_queue = value
                elif key == "log":
                    log.append(value)
                elif key == "log_tag":
                    log_tag = value
                elif key == "log_format":
                    log_format = value
                elif key == "error_log_format":
                    error_log_format = value
                elif key == "log_format_sd":
                    log_format_sd = value
                elif key == "log_steps":
                    log_steps = value
                elif key == "unique_id_format":
                    unique_id_format = value
                elif key == "unique_id_header":
                    unique_id_header = value
                elif key == "capture_request_header":
                    capture_request_headers.append(value)
                elif key == "capture_response_header":
                    capture_response_headers.append(value)
                elif key == "errorloc":
                    errorloc.update(value)
                elif key == "errorloc302":
                    errorloc302.update(value)
                elif key == "errorloc303":
                    errorloc303.update(value)
                elif key == "filters":
                    filters = value
                elif key == "clitcpka_cnt":
                    clitcpka_cnt = value
                elif key == "clitcpka_idle":
                    clitcpka_idle = value
                elif key == "clitcpka_intvl":
                    clitcpka_intvl = value
                elif key == "rate_limit_sessions":
                    rate_limit_sessions = value

        return Frontend(
            name=name,
            description=description,
            disabled=disabled,
            enabled=enabled,
            id=id,
            guid=guid,
            mode=mode,
            binds=binds,
            acls=acls,
            filters=filters,
            http_request_rules=http_request_rules,
            http_response_rules=http_response_rules,
            http_after_response_rules=http_after_response_rules,
            tcp_request_rules=tcp_request_rules,
            tcp_response_rules=tcp_response_rules,
            quic_initial_rules=quic_initial_rules,
            use_backend_rules=use_backend_rules,
            default_backend=default_backend,
            options=options,
            stick_table=stick_table,
            stick_rules=stick_rules,
            timeout_client=timeout_client,
            timeout_http_request=timeout_http_request,
            timeout_http_keep_alive=timeout_http_keep_alive,
            timeout_client_fin=timeout_client_fin,
            timeout_tarpit=timeout_tarpit,
            monitor_uri=monitor_uri,
            monitor_net=monitor_net,
            monitor_fail_rules=monitor_fail_rules,
            maxconn=maxconn,
            backlog=backlog,
            fullconn=fullconn,
            max_keep_alive_queue=max_keep_alive_queue,
            log=log,
            log_tag=log_tag,
            log_format=log_format,
            error_log_format=error_log_format,
            log_format_sd=log_format_sd,
            log_steps=log_steps,
            unique_id_format=unique_id_format,
            unique_id_header=unique_id_header,
            stats_config=stats_config,
            capture_request_headers=capture_request_headers,
            capture_response_headers=capture_response_headers,
            redirect_rules=redirect_rules,
            error_files=error_files,
            http_errors=http_errors,
            email_alert=email_alert,
            declare_captures=declare_captures,
            force_persist_rules=force_persist_rules,
            ignore_persist_rules=ignore_persist_rules,
            errorloc=errorloc,
            errorloc302=errorloc302,
            errorloc303=errorloc303,
            rate_limit_sessions=rate_limit_sessions,
            clitcpka_cnt=clitcpka_cnt,
            clitcpka_idle=clitcpka_idle,
            clitcpka_intvl=clitcpka_intvl,
        )

    def frontend_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

    def frontend_description(self, items: list[Any]) -> tuple[str, str]:
        """Transform description directive."""
        return ("description", str(items[0]))

    def frontend_disabled(self, items: list[Any]) -> tuple[str, bool]:
        """Transform disabled directive."""
        return ("disabled", items[0])

    def frontend_enabled(self, items: list[Any]) -> tuple[str, bool]:
        """Transform enabled directive."""
        return ("enabled", items[0])

    def frontend_id(self, items: list[Any]) -> tuple[str, int]:
        """Transform id directive."""
        return ("id", items[0])

    def frontend_guid(self, items: list[Any]) -> tuple[str, str]:
        """Transform guid directive (global unique identifier)."""
        return ("guid", str(items[0]))

    def frontend_unique_id_format(self, items: list[Any]) -> tuple[str, str]:
        """Transform unique-id-format directive."""
        return ("unique_id_format", str(items[0]))

    def frontend_unique_id_header(self, items: list[Any]) -> tuple[str, str]:
        """Transform unique-id-header directive."""
        return ("unique_id_header", str(items[0]))

    def frontend_default_backend(self, items: list[Any]) -> tuple[str, str]:
        return ("default_backend", str(items[0]))

    def frontend_option(self, items: list[Any]) -> tuple[str, Any]:
        return ("option", items[0])

    def frontend_timeout_client(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_client", str(items[0]))

    def frontend_timeout_http_request(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_http_request", str(items[0]))

    def frontend_timeout_http_keep_alive(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_http_keep_alive", str(items[0]))

    def frontend_timeout_client_fin(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_client_fin", str(items[0]))

    def frontend_timeout_tarpit(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_tarpit", str(items[0]))

    def frontend_monitor_uri(self, items: list[Any]) -> tuple[str, str]:
        return ("monitor_uri", str(items[0]))

    def frontend_monitor_net(self, items: list[Any]) -> tuple[str, str]:
        """Transform monitor-net directive."""
        return ("monitor_net", str(items[0]))

    def frontend_monitor_fail(self, items: list[Any]) -> MonitorFailRule:
        """Transform monitor fail directive."""
        # items[0] is the if_condition tuple
        condition = None
        if items[0] is not None:
            if isinstance(items[0], tuple):
                _, acl_name = items[0]
                condition = f"if {acl_name}"
            else:
                condition = str(items[0])
        return MonitorFailRule(condition=condition or "")

    def frontend_maxconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxconn", items[0])

    def frontend_backlog(self, items: list[Any]) -> tuple[str, int]:
        """Transform backlog directive."""
        return ("backlog", items[0])

    def frontend_fullconn(self, items: list[Any]) -> tuple[str, int]:
        """Transform fullconn directive."""
        return ("fullconn", items[0])

    def frontend_max_keep_alive_queue(self, items: list[Any]) -> tuple[str, int]:
        """Transform max-keep-alive-queue directive."""
        return ("max_keep_alive_queue", items[0])

    def frontend_log(self, items: list[Any]) -> tuple[str, str]:
        """Transform log directive."""
        return ("log", str(items[0]))

    def frontend_log_tag(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-tag directive."""
        return ("log_tag", str(items[0]))

    def frontend_log_format(self, items: list[Any]) -> tuple[str, str]:
        return ("log_format", items[0])

    def frontend_error_log_format(self, items: list[Any]) -> tuple[str, str]:
        """Transform error-log-format directive."""
        return ("error_log_format", str(items[0]))

    def frontend_log_format_sd(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-format-sd directive (RFC 5424 structured data)."""
        return ("log_format_sd", str(items[0]))

    def frontend_log_steps(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-steps directive (logging steps for transaction processing)."""
        return ("log_steps", str(items[0]))

    def frontend_stats(self, items: list[Any]) -> StatsConfig:
        """Transform stats block."""
        return cast("StatsConfig", items[0])

    def stats_block(self, items: list[Any]) -> StatsConfig:
        """Build StatsConfig from stats properties."""
        enable = False
        uri = None
        realm = None
        auth = []
        hide_version = False
        refresh = None
        show_legends = False
        show_desc = None
        admin_rules = []

        for prop in items:
            if isinstance(prop, tuple):
                key, value = prop
                if key == "enable":
                    enable = value
                elif key == "uri":
                    uri = value
                elif key == "realm":
                    realm = value
                elif key == "auth":
                    auth.append(value)
                elif key == "hide_version":
                    hide_version = value
                elif key == "refresh":
                    refresh = value
                elif key == "show_legends":
                    show_legends = value
                elif key == "show_desc":
                    show_desc = value
                elif key == "admin":
                    admin_rules.append(value)

        return StatsConfig(
            enable=enable,
            uri=uri,
            realm=realm,
            auth=auth,
            hide_version=hide_version,
            refresh=refresh,
            show_legends=show_legends,
            show_desc=show_desc,
            admin_rules=admin_rules,
        )

    def stats_realm(self, items: list[Any]) -> tuple[str, str]:
        """Transform stats realm."""
        return ("realm", str(items[0]))

    def stats_hide_version(self, items: list[Any]) -> tuple[str, bool]:
        """Transform stats hide-version."""
        return ("hide_version", True)

    def stats_refresh(self, items: list[Any]) -> tuple[str, str]:
        """Transform stats refresh."""
        return ("refresh", str(items[0]))

    def stats_show_legends(self, items: list[Any]) -> tuple[str, bool]:
        """Transform stats show-legends."""
        return ("show_legends", True)

    def stats_show_desc(self, items: list[Any]) -> tuple[str, str]:
        """Transform stats show-desc."""
        return ("show_desc", str(items[0]))

    def stats_admin(self, items: list[Any]) -> tuple[str, str]:
        """Transform stats admin with ACL condition."""
        condition = None
        if items[0] is not None:
            if isinstance(items[0], tuple):
                _, acl_name = items[0]
                condition = f"if {acl_name}"
            else:
                condition = str(items[0])
        return ("admin", condition or "")

    def frontend_capture_request_header(self, items: list[Any]) -> tuple[str, tuple[str, int]]:
        return ("capture_request_header", (items[0], items[1]))

    def frontend_capture_response_header(self, items: list[Any]) -> tuple[str, tuple[str, int]]:
        return ("capture_response_header", (items[0], items[1]))

    # ===== Redirect Rules =====
    def frontend_redirect(self, items: list[Any]) -> RedirectRule:
        return cast("RedirectRule", items[0])

    def backend_redirect(self, items: list[Any]) -> RedirectRule:
        return cast("RedirectRule", items[0])

    def redirect_rule(self, items: list[Any]) -> RedirectRule:
        """Transform redirect rule."""
        redirect_type = str(items[0])  # location, prefix, or scheme
        target = str(items[1])
        code = None
        condition = None
        options = {}

        # Process optional redirect options
        if len(items) > 2:
            for item in items[2:]:
                if isinstance(item, tuple):
                    key, value = item
                    if key == "code":
                        code = value
                    elif key == "if":
                        condition = f"if {value}"
                    elif key == "unless":
                        condition = f"unless {value}"
                    elif key in ("drop-query", "append-slash"):
                        options[key] = True
                    elif key in ("set-cookie", "clear-cookie"):
                        options[key] = value

        return RedirectRule(type=redirect_type, target=target, code=code, condition=condition, options=options)

    def redirect_location(self, items: list[Any]) -> str:
        return "location"

    def redirect_prefix(self, items: list[Any]) -> str:
        return "prefix"

    def redirect_scheme(self, items: list[Any]) -> str:
        return "scheme"

    def redirect_code(self, items: list[Any]) -> tuple[str, int]:
        return ("code", items[0])

    def redirect_drop_query(self, items: list[Any]) -> tuple[str, bool]:
        return ("drop-query", True)

    def redirect_append_slash(self, items: list[Any]) -> tuple[str, bool]:
        return ("append-slash", True)

    def redirect_set_cookie(self, items: list[Any]) -> tuple[str, str]:
        return ("set-cookie", items[0])

    def redirect_clear_cookie(self, items: list[Any]) -> tuple[str, str]:
        return ("clear-cookie", items[0])

    def redirect_if(self, items: list[Any]) -> tuple[str, str]:
        return ("if", str(items[0]))

    def redirect_unless(self, items: list[Any]) -> tuple[str, str]:
        return ("unless", str(items[0]))

    # ===== Error Files =====
    def frontend_errorfile(self, items: list[Any]) -> ErrorFile:
        return cast("ErrorFile", items[0])

    def backend_errorfile(self, items: list[Any]) -> ErrorFile:
        return cast("ErrorFile", items[0])

    def frontend_http_error(self, items: list[Any]) -> HttpError:
        """Transform http-error for frontend."""
        return cast("HttpError", items[0])

    def backend_http_error(self, items: list[Any]) -> HttpError:
        """Transform http-error for backend."""
        return cast("HttpError", items[0])

    def listen_http_error(self, items: list[Any]) -> HttpError:
        """Transform http-error for listen."""
        return cast("HttpError", items[0])

    def frontend_email_alert(self, items: list[Any]) -> EmailAlert:
        """Transform email-alert for frontend."""
        return cast("EmailAlert", items[0])

    def backend_email_alert(self, items: list[Any]) -> EmailAlert:
        """Transform email-alert for backend."""
        return cast("EmailAlert", items[0])

    def listen_email_alert(self, items: list[Any]) -> EmailAlert:
        """Transform email-alert for listen."""
        return cast("EmailAlert", items[0])

    def defaults_email_alert(self, items: list[Any]) -> EmailAlert:
        """Transform email-alert for defaults."""
        return cast("EmailAlert", items[0])

    # TCP keepalive methods (Phase 5B)
    def defaults_clitcpka_cnt(self, items: list[Any]) -> tuple[str, int]:
        """Transform clitcpka-cnt for defaults."""
        return ("clitcpka_cnt", int(items[0]))

    def defaults_clitcpka_idle(self, items: list[Any]) -> tuple[str, str]:
        """Transform clitcpka-idle for defaults."""
        return ("clitcpka_idle", str(items[0]))

    def defaults_clitcpka_intvl(self, items: list[Any]) -> tuple[str, str]:
        """Transform clitcpka-intvl for defaults."""
        return ("clitcpka_intvl", str(items[0]))

    def defaults_srvtcpka_cnt(self, items: list[Any]) -> tuple[str, int]:
        """Transform srvtcpka-cnt for defaults."""
        return ("srvtcpka_cnt", int(items[0]))

    def defaults_srvtcpka_idle(self, items: list[Any]) -> tuple[str, str]:
        """Transform srvtcpka-idle for defaults."""
        return ("srvtcpka_idle", str(items[0]))

    def defaults_srvtcpka_intvl(self, items: list[Any]) -> tuple[str, str]:
        """Transform srvtcpka-intvl for defaults."""
        return ("srvtcpka_intvl", str(items[0]))

    def frontend_clitcpka_cnt(self, items: list[Any]) -> tuple[str, int]:
        """Transform clitcpka-cnt for frontend."""
        return ("clitcpka_cnt", int(items[0]))

    def frontend_clitcpka_idle(self, items: list[Any]) -> tuple[str, str]:
        """Transform clitcpka-idle for frontend."""
        return ("clitcpka_idle", str(items[0]))

    def frontend_clitcpka_intvl(self, items: list[Any]) -> tuple[str, str]:
        """Transform clitcpka-intvl for frontend."""
        return ("clitcpka_intvl", str(items[0]))

    def backend_srvtcpka_cnt(self, items: list[Any]) -> tuple[str, int]:
        """Transform srvtcpka-cnt for backend."""
        return ("srvtcpka_cnt", int(items[0]))

    def backend_srvtcpka_idle(self, items: list[Any]) -> tuple[str, str]:
        """Transform srvtcpka-idle for backend."""
        return ("srvtcpka_idle", str(items[0]))

    def backend_srvtcpka_intvl(self, items: list[Any]) -> tuple[str, str]:
        """Transform srvtcpka-intvl for backend."""
        return ("srvtcpka_intvl", str(items[0]))

    def backend_persist_rdp_cookie(self, items: list[Any]) -> tuple[str, str]:
        """Transform persist rdp-cookie for backend (default msts cookie)."""
        return ("persist_rdp_cookie", "")  # Empty string means use default "msts"

    def backend_persist_rdp_cookie_named(self, items: list[Any]) -> tuple[str, str]:
        """Transform persist rdp-cookie with custom cookie name for backend."""
        return ("persist_rdp_cookie", str(items[0]))

    def listen_clitcpka_cnt(self, items: list[Any]) -> tuple[str, int]:
        """Transform clitcpka-cnt for listen."""
        return ("clitcpka_cnt", int(items[0]))

    def listen_clitcpka_idle(self, items: list[Any]) -> tuple[str, str]:
        """Transform clitcpka-idle for listen."""
        return ("clitcpka_idle", str(items[0]))

    def listen_clitcpka_intvl(self, items: list[Any]) -> tuple[str, str]:
        """Transform clitcpka-intvl for listen."""
        return ("clitcpka_intvl", str(items[0]))

    def listen_srvtcpka_cnt(self, items: list[Any]) -> tuple[str, int]:
        """Transform srvtcpka-cnt for listen."""
        return ("srvtcpka_cnt", int(items[0]))

    def listen_srvtcpka_idle(self, items: list[Any]) -> tuple[str, str]:
        """Transform srvtcpka-idle for listen."""
        return ("srvtcpka_idle", str(items[0]))

    def listen_srvtcpka_intvl(self, items: list[Any]) -> tuple[str, str]:
        """Transform srvtcpka-intvl for listen."""
        return ("srvtcpka_intvl", str(items[0]))

    # Rate limit methods (Phase 5B)
    def defaults_rate_limit_sessions(self, items: list[Any]) -> tuple[str, int]:
        """Transform rate-limit sessions for defaults."""
        return ("rate_limit_sessions", int(items[0]))

    def defaults_persist_rdp_cookie(self, items: list[Any]) -> tuple[str, str]:
        """Transform persist rdp-cookie (default msts cookie)."""
        return ("persist_rdp_cookie", "")  # Empty string means use default "msts"

    def defaults_persist_rdp_cookie_named(self, items: list[Any]) -> tuple[str, str]:
        """Transform persist rdp-cookie with custom cookie name."""
        return ("persist_rdp_cookie", str(items[0]))

    def frontend_rate_limit_sessions(self, items: list[Any]) -> tuple[str, int]:
        """Transform rate-limit sessions for frontend."""
        return ("rate_limit_sessions", int(items[0]))

    def listen_rate_limit_sessions(self, items: list[Any]) -> tuple[str, int]:
        """Transform rate-limit sessions for listen."""
        return ("rate_limit_sessions", int(items[0]))

    def listen_persist_rdp_cookie(self, items: list[Any]) -> tuple[str, str]:
        """Transform persist rdp-cookie for listen (default msts cookie)."""
        return ("persist_rdp_cookie", "")  # Empty string means use default "msts"

    def listen_persist_rdp_cookie_named(self, items: list[Any]) -> tuple[str, str]:
        """Transform persist rdp-cookie with custom cookie name for listen."""
        return ("persist_rdp_cookie", str(items[0]))

    def frontend_declare_capture(self, items: list[Any]) -> DeclareCapture:
        """Transform declare capture for frontend."""
        return cast("DeclareCapture", items[0])

    def backend_declare_capture(self, items: list[Any]) -> DeclareCapture:
        """Transform declare capture for backend."""
        return cast("DeclareCapture", items[0])

    def listen_declare_capture(self, items: list[Any]) -> DeclareCapture:
        """Transform declare capture for listen."""
        return cast("DeclareCapture", items[0])

    def frontend_force_persist(self, items: list[Any]) -> ForcePersistRule:
        """Transform force-persist for frontend."""
        return cast("ForcePersistRule", items[0])

    def backend_force_persist(self, items: list[Any]) -> ForcePersistRule:
        """Transform force-persist for backend."""
        return cast("ForcePersistRule", items[0])

    def listen_force_persist(self, items: list[Any]) -> ForcePersistRule:
        """Transform force-persist for listen."""
        return cast("ForcePersistRule", items[0])

    def frontend_ignore_persist(self, items: list[Any]) -> IgnorePersistRule:
        """Transform ignore-persist for frontend."""
        return cast("IgnorePersistRule", items[0])

    def backend_ignore_persist(self, items: list[Any]) -> IgnorePersistRule:
        """Transform ignore-persist for backend."""
        return cast("IgnorePersistRule", items[0])

    def listen_ignore_persist(self, items: list[Any]) -> IgnorePersistRule:
        """Transform ignore-persist for listen."""
        return cast("IgnorePersistRule", items[0])

    def listen_http_after_response(self, items: list[Any]) -> list[HttpAfterResponseRule]:
        """Transform http-after-response for listen."""
        return cast("list[HttpAfterResponseRule]", items[0])

    def errorfile_directive(self, items: list[Any]) -> ErrorFile:
        """Transform errorfile directive."""
        code = int(items[0])
        file = str(items[1])
        return ErrorFile(code=code, file=file)

    # ===== Error Location Redirects =====
    def frontend_errorloc(self, items: list[Any]) -> tuple[str, Any]:
        """Transform errorloc directive for frontend."""
        return cast("tuple[str, Any]", items[0])

    def backend_errorloc(self, items: list[Any]) -> tuple[str, Any]:
        """Transform errorloc directive for backend."""
        return cast("tuple[str, Any]", items[0])

    def errorloc(self, items: list[Any]) -> tuple[str, dict[int, str]]:
        """Transform errorloc (302 redirect by default)."""
        code = int(items[0])
        location = str(items[1])
        return ("errorloc", {code: location})

    def errorloc302(self, items: list[Any]) -> tuple[str, dict[int, str]]:
        """Transform errorloc302 (explicit 302 redirect)."""
        code = int(items[0])
        location = str(items[1])
        return ("errorloc302", {code: location})

    def errorloc303(self, items: list[Any]) -> tuple[str, dict[int, str]]:
        """Transform errorloc303 (303 See Other redirect)."""
        code = int(items[0])
        location = str(items[1])
        return ("errorloc303", {code: location})

    # ===== HTTP Reuse =====
    def http_reuse_mode(self, items: list[Token]) -> str:
        """Extract http-reuse mode string from grammar alternatives."""
        return str(items[0]) if items else "safe"

    def backend_http_reuse(self, items: list[Any]) -> tuple[str, str]:
        return ("http_reuse", items[0])

    def backend_http_send_name_header(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-send-name-header directive."""
        return ("http_send_name_header", str(items[0]))

    def backend_retry_on(self, items: list[Any]) -> tuple[str, str]:
        """Transform retry-on directive."""
        return ("retry_on", str(items[0]))

    def backend_source(self, items: list[Any]) -> tuple[str, str]:
        return ("source", str(items[0]))

    def backend_hash_type(self, items: list[Any]) -> tuple[str, str]:
        """Transform hash-type directive."""
        hash_spec = items[0]  # Result from hash_type_spec
        return ("hash_type", hash_spec)

    def backend_hash_balance_factor(self, items: list[Any]) -> tuple[str, int]:
        """Transform hash-balance-factor directive."""
        return ("hash_balance_factor", int(items[0]))

    def backend_hash_preserve_affinity(self, items: list[Any]) -> tuple[str, str]:
        """Transform hash-preserve-affinity directive (Phase 5B)."""
        return ("hash_preserve_affinity", str(items[0]))

    def backend_load_server_state_from(self, items: list[Any]) -> tuple[str, str]:
        """Transform load-server-state-from-file directive."""
        return ("load_server_state_from", str(items[0]))

    def backend_server_state_file_name(self, items: list[Any]) -> tuple[str, str]:
        """Transform server-state-file-name directive (use-backend-name or file path)."""
        return ("server_state_file_name", str(items[0]))

    def hash_type_spec(self, items: list[Any]) -> str:
        """Build hash-type specification string from components."""
        # items: [method, function?, modifier?]
        parts = []
        for item in items:
            if item is not None:
                parts.append(str(item))
        return " ".join(parts)

    def hash_method(self, items: list[Any]) -> str:
        """Transform hash method (map-based or consistent)."""
        return str(items[0])

    def hash_function(self, items: list[Any]) -> str:
        """Transform hash function (sdbm, djb2, wt6, crc32)."""
        return str(items[0])

    def hash_modifier(self, items: list[Any]) -> str:
        """Transform hash modifier (avalanche)."""
        return str(items[0])

    # ===== use-server Directive =====
    def backend_use_server(self, items: list[Any]) -> UseServerRule:
        return cast("UseServerRule", items[0])

    def use_server_rule(self, items: list[Any]) -> UseServerRule:
        """Transform use-server rule."""
        server = str(items[0])
        condition = None

        if len(items) > 1 and items[1] is not None:
            # if_condition returns a tuple ("condition", acl_name)
            if isinstance(items[1], tuple):
                _, acl_name = items[1]
                condition = f"if {acl_name}"
            else:
                condition = str(items[1])

        return UseServerRule(server=server, condition=condition)

    # ===== http-check Block =====
    def backend_http_check(self, items: list[Any]) -> list[HttpCheckRule]:
        """Backend http-check block returns list of rules."""
        return cast("list[HttpCheckRule]", items[0])  # http_check_block already returns a list

    def http_check_block(self, items: list[Any]) -> list[HttpCheckRule]:
        """Transform http-check block."""
        return items  # List of HttpCheckRule objects

    def http_check_send_with_uri(self, items: list[Any]) -> tuple[str, str | None, dict[str, str]]:
        """Transform http-check send with method and uri."""
        method = str(items[0])
        uri = str(items[1]) if len(items) > 1 else None

        # Headers come as a list of tuples from header_definition
        headers = {}
        if len(items) > 2 and isinstance(items[2], list):
            headers = dict(items[2])

        return (method, uri, headers)

    def http_check_send_method_only(self, items: list[Any]) -> tuple[str, str | None, dict[str, str]]:
        """Transform http-check send with method only."""
        method = str(items[0])

        # Headers come as a list of tuples from header_definition
        headers = {}
        if len(items) > 1 and isinstance(items[1], list):
            headers = dict(items[1])

        return (method, None, headers)

    def http_check_send(self, items: list[Any]) -> HttpCheckRule:
        """Transform http-check send rule."""
        # items[0] contains the send options (method, uri, headers) from http_check_send_options
        send_opts = items[0]

        method = None
        uri = None
        headers: dict[str, str] = {}

        if isinstance(send_opts, tuple) and len(send_opts) >= 2:
            method = send_opts[0]
            uri = send_opts[1]
            headers = send_opts[2] if len(send_opts) > 2 else {}

        return HttpCheckRule(type="send", method=method, uri=uri, headers=headers)

    def http_check_expect(self, items: list[Any]) -> HttpCheckRule:
        """Transform http-check expect rule."""
        expect = items[0]  # expect_value result (tuple of type and value)

        if isinstance(expect, tuple):
            expect_type, expect_value, expect_negate = expect
            return HttpCheckRule(type="expect", expect_type=expect_type, expect_value=expect_value, expect_negate=expect_negate)

        return HttpCheckRule(type="expect")

    def http_check_connect_with_port(self, items: list[Any]) -> dict[str, Any]:
        """Transform http-check connect with port."""
        port = int(items[0])
        ssl_opts = self._parse_ssl_options(items[1:]) if len(items) > 1 else {}
        return {"port": port, **ssl_opts}

    def http_check_connect_ssl_only(self, items: list[Any]) -> dict[str, Any]:
        """Transform http-check connect with SSL only."""
        return self._parse_ssl_options(items)

    def _parse_ssl_options(self, items: list[Any]) -> dict[str, Any]:
        """Parse SSL options from inlined ssl_options rule."""
        opts: dict[str, bool | str | None] = {"ssl": False, "sni": None, "alpn": None}
        if not items:
            return opts

        # Items will be tokens from the inlined rule: may contain sni and alpn strings
        for _i, item in enumerate(items):
            if isinstance(item, str):
                # First string after ssl is sni, second is alpn
                if opts["sni"] is None:
                    opts["sni"] = item
                else:
                    opts["alpn"] = item

        # If we have any items, ssl must be True
        if items:
            opts["ssl"] = True

        return opts

    def http_check_connect(self, items: list[Any]) -> HttpCheckRule:
        """Transform http-check connect rule."""
        conn_opts = items[0] if items else {}

        port = conn_opts.get("port") if isinstance(conn_opts, dict) else None
        ssl = conn_opts.get("ssl", False) if isinstance(conn_opts, dict) else False
        sni = conn_opts.get("sni") if isinstance(conn_opts, dict) else None
        alpn = conn_opts.get("alpn") if isinstance(conn_opts, dict) else None

        return HttpCheckRule(type="connect", port=port, ssl=ssl, sni=sni, alpn=alpn)

    def http_check_disable_on_404(self, items: list[Any]) -> HttpCheckRule:
        """Transform http-check disable-on-404 rule."""
        return HttpCheckRule(type="disable-on-404")

    # ===== http-error Block =====
    def http_error_block(self, items: list[Any]) -> HttpError:
        """Build HttpError from http-error properties."""
        status = 0
        content_type = None
        default_errorfiles = False
        errorfile = None
        errorfiles_name = None
        file = None
        lf_file = None
        string = None
        lf_string = None
        headers: dict[str, str] = {}

        for prop in items:
            if isinstance(prop, tuple):
                key, value = prop
                if key == "status":
                    status = int(value)
                elif key == "content_type":
                    content_type = str(value)
                elif key == "file":
                    file = str(value)
                elif key == "lf_file":
                    lf_file = str(value)
                elif key == "string":
                    string = str(value)
                elif key == "lf_string":
                    lf_string = str(value)
                elif key == "errorfile":
                    errorfile = str(value)
                elif key == "errorfiles_name":
                    errorfiles_name = str(value)
                elif key == "default_errorfiles":
                    default_errorfiles = bool(value)

        return HttpError(
            status=status,
            content_type=content_type,
            default_errorfiles=default_errorfiles,
            errorfile=errorfile,
            errorfiles_name=errorfiles_name,
            file=file,
            lf_file=lf_file,
            string=string,
            lf_string=lf_string,
            headers=headers,
        )

    def http_error_status(self, items: list[Any]) -> tuple[str, int]:
        """Transform http-error status property."""
        return ("status", int(items[0]))

    def http_error_content_type(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-error content-type property."""
        return ("content_type", str(items[0]))

    def http_error_file(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-error file property."""
        return ("file", str(items[0]))

    def http_error_lf_file(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-error lf-file property."""
        return ("lf_file", str(items[0]))

    def http_error_string(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-error string property."""
        return ("string", str(items[0]))

    def http_error_lf_string(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-error lf-string property."""
        return ("lf_string", str(items[0]))

    def http_error_errorfile(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-error errorfile property."""
        return ("errorfile", str(items[0]))

    def http_error_errorfiles_name(self, items: list[Any]) -> tuple[str, str]:
        """Transform http-error errorfiles-name property."""
        return ("errorfiles_name", str(items[0]))

    def http_error_default_errorfiles(self, items: list[Any]) -> tuple[str, bool]:
        """Transform http-error default-errorfiles property."""
        return ("default_errorfiles", bool(items[0]))

    # ===== email-alert Block =====
    def email_alert_block(self, items: list[Any]) -> EmailAlert:
        """Build EmailAlert from email-alert properties."""
        level = None
        mailers = None
        from_email = None
        to_email = None
        myhostname = None

        for prop in items:
            if isinstance(prop, tuple):
                key, value = prop
                if key == "level":
                    level = str(value)
                elif key == "mailers":
                    mailers = str(value)
                elif key == "from":
                    from_email = str(value)
                elif key == "to":
                    to_email = str(value)
                elif key == "myhostname":
                    myhostname = str(value)

        return EmailAlert(
            level=level,
            mailers=mailers,
            from_email=from_email,
            to_email=to_email,
            myhostname=myhostname,
        )

    def email_alert_level(self, items: list[Any]) -> tuple[str, str]:
        """Transform email-alert level property."""
        return ("level", str(items[0]))

    def email_alert_mailers(self, items: list[Any]) -> tuple[str, str]:
        """Transform email-alert mailers property."""
        return ("mailers", str(items[0]))

    def email_alert_from(self, items: list[Any]) -> tuple[str, str]:
        """Transform email-alert from property."""
        return ("from", str(items[0]))

    def email_alert_to(self, items: list[Any]) -> tuple[str, str]:
        """Transform email-alert to property."""
        return ("to", str(items[0]))

    def email_alert_myhostname(self, items: list[Any]) -> tuple[str, str]:
        """Transform email-alert myhostname property."""
        return ("myhostname", str(items[0]))

    def declare_capture_directive(self, items: list[Any]) -> DeclareCapture:
        """Build DeclareCapture from declare capture directive."""
        # items[0] is the capture_type token (CAPTURE_REQUEST or CAPTURE_RESPONSE)
        # items[1] is the length (number)
        capture_type = str(items[0])
        length = int(items[1])
        return DeclareCapture(capture_type=capture_type, length=length)

    def force_persist_directive(self, items: list[Any]) -> ForcePersistRule:
        """Build ForcePersistRule from force-persist directive."""
        # items[0] is the if_condition tuple ("condition", "acl_name")
        condition = None
        if items and isinstance(items[0], tuple) and len(items[0]) == 2:
            # Reconstruct the condition as "if acl_name"
            condition = f"if {items[0][1]}"
        return ForcePersistRule(condition=condition)

    def ignore_persist_directive(self, items: list[Any]) -> IgnorePersistRule:
        """Build IgnorePersistRule from ignore-persist directive."""
        # items[0] is the if_condition tuple ("condition", "acl_name")
        condition = None
        if items and isinstance(items[0], tuple) and len(items[0]) == 2:
            # Reconstruct the condition as "if acl_name"
            condition = f"if {items[0][1]}"
        return IgnorePersistRule(condition=condition)

    # ===== tcp-check Block =====
    def backend_tcp_check(self, items: list[Any]) -> list[TcpCheckRule]:
        """Backend tcp-check block returns list of rules."""
        return cast("list[TcpCheckRule]", items[0])  # tcp_check_block already returns a list

    def tcp_check_block(self, items: list[Any]) -> list[TcpCheckRule]:
        """Transform tcp-check block."""
        return items  # List of TcpCheckRule objects

    def tcp_check_connect_with_port(self, items: list[Any]) -> dict[str, Any]:
        """Transform tcp-check connect with port."""
        port = int(items[0])
        ssl_opts = self._parse_ssl_options(items[1:]) if len(items) > 1 else {}
        return {"port": port, **ssl_opts}

    def tcp_check_connect_ssl_only(self, items: list[Any]) -> dict[str, Any]:
        """Transform tcp-check connect with SSL only."""
        return self._parse_ssl_options(items)

    def tcp_check_connect(self, items: list[Any]) -> TcpCheckRule:
        """Transform tcp-check connect rule."""
        conn_opts = items[0] if items else {}

        port = conn_opts.get("port") if isinstance(conn_opts, dict) else None
        ssl = conn_opts.get("ssl", False) if isinstance(conn_opts, dict) else False
        sni = conn_opts.get("sni") if isinstance(conn_opts, dict) else None
        alpn = conn_opts.get("alpn") if isinstance(conn_opts, dict) else None

        return TcpCheckRule(type="connect", port=port, ssl=ssl, sni=sni, alpn=alpn)

    def tcp_check_send(self, items: list[Any]) -> TcpCheckRule:
        """Transform tcp-check send rule."""
        data = str(items[0]) if items else ""
        return TcpCheckRule(type="send", data=data)

    def tcp_check_send_binary(self, items: list[Any]) -> TcpCheckRule:
        """Transform tcp-check send-binary rule."""
        data = str(items[0]) if items else ""
        return TcpCheckRule(type="send-binary", data=data)

    def tcp_check_expect(self, items: list[Any]) -> TcpCheckRule:
        """Transform tcp-check expect rule."""
        expect_opts = items[0] if items else None
        pattern = str(expect_opts) if expect_opts else None
        return TcpCheckRule(type="expect", pattern=pattern)

    def tcp_check_comment(self, items: list[Any]) -> TcpCheckRule:
        """Transform tcp-check comment rule."""
        comment = str(items[0]) if items else ""
        return TcpCheckRule(type="comment", comment=comment)

    def bind_directive(self, items: list[Any]) -> Bind:
        address = str(items[0])
        ssl = False
        ssl_cert = None
        alpn = []
        options = {}

        for item in items[1:]:
            if isinstance(item, dict):
                # SSL block
                ssl = True
                for key, value in item.items():
                    if key == "cert":
                        ssl_cert = value
                    elif key == "alpn":
                        alpn = value
                    else:
                        options[key] = value
            elif isinstance(item, tuple):
                key, value = item
                options[key] = value

        return Bind(address=address, ssl=ssl, ssl_cert=ssl_cert, alpn=alpn, options=options)

    def ssl_block(self, items: list[Any]) -> dict[str, Any]:
        ssl_opts = {}
        for item in items:
            if isinstance(item, tuple):
                ssl_opts[item[0]] = item[1]
        return ssl_opts

    def ssl_cert(self, items: list[Any]) -> tuple[str, str]:
        return ("cert", items[0])

    def ssl_alpn(self, items: list[Any]) -> tuple[str, list[str]]:
        return ("alpn", items[0])

    def ssl_generic(self, items: list[Any]) -> tuple[str, Any]:
        return (str(items[0]), items[1])

    def bind_generic_option(self, items: list[Any]) -> tuple[str, Any]:
        return (str(items[0]), items[1])

    def http_request_block(self, items: list[Any]) -> list[HttpRequestRule]:
        return items

    def http_response_block(self, items: list[Any]) -> list[HttpResponseRule]:
        return items

    def http_request_rule(self, items: list[Any]) -> HttpRequestRule:
        # items[0] is the tuple from action_expr: (action_name, parameters)
        # items[1] (if present) is the condition
        action_data = items[0]

        if isinstance(action_data, tuple):
            action, parameters = action_data
        else:
            # Fallback for old format
            action = str(action_data)
            parameters = {}

        condition = None
        if len(items) > 1 and isinstance(items[1], tuple) and items[1][0] == "condition":
            condition = items[1][1]

        return HttpRequestRule(action=action, parameters=parameters, condition=condition)

    def http_response_rule(self, items: list[Any]) -> HttpResponseRule:
        # items[0] is the tuple from action_expr: (action_name, parameters)
        # items[1] (if present) is the condition
        action_data = items[0]

        if isinstance(action_data, tuple):
            action, parameters = action_data
        else:
            # Fallback for old format
            action = str(action_data)
            parameters = {}

        condition = None
        if len(items) > 1 and isinstance(items[1], tuple) and items[1][0] == "condition":
            condition = items[1][1]

        return HttpResponseRule(action=action, parameters=parameters, condition=condition)

    def http_after_response_block(self, items: list[Any]) -> list[HttpAfterResponseRule]:
        return items

    def http_after_response_rule(self, items: list[Any]) -> HttpAfterResponseRule:
        # items[0] is the tuple from action_expr: (action_name, parameters)
        # items[1] (if present) is the condition
        action_data = items[0]

        if isinstance(action_data, tuple):
            action, parameters = action_data
        else:
            # Fallback for old format
            action = str(action_data)
            parameters = {}

        condition = None
        if len(items) > 1 and isinstance(items[1], tuple) and items[1][0] == "condition":
            condition = items[1][1]

        return HttpAfterResponseRule(action=action, parameters=parameters, condition=condition)

    def action_expr(self, items: list[Any]) -> tuple[str, dict[str, Any]]:
        """Transform action expression with action name and parameters."""
        action_name = str(items[0])
        parameters = {}

        # Collect parameters from items[1:]
        for item in items[1:]:
            if isinstance(item, tuple):
                parameters[item[0]] = item[1]
            elif isinstance(item, str):
                # Positional value - use generic "value" key
                if "value" not in parameters:
                    parameters["value"] = item
                else:
                    # Multiple values - create a list
                    if not isinstance(parameters["value"], list):
                        parameters["value"] = [parameters["value"]]
                    parameters["value"].append(item)

        return (action_name, parameters)

    def action_name(self, items: list[Any]) -> str:
        return cast("str", items[0])

    def qualified_identifier(self, items: list[Any]) -> str:
        return ".".join(str(i) for i in items)

    def http_rule_param(self, items: list[Any]) -> tuple[str, Any]:
        return (str(items[0]), items[1])

    def http_rule_value(self, items: list[Any]) -> str:
        return cast("str", items[0])

    def if_condition(self, items: list[Any]) -> tuple[str, str]:
        return ("condition", str(items[0]))

    def condition_expr(self, items: list[Any]) -> str:
        return str(items[0])

    def use_acl_directive(self, items: list[Any]) -> list[ACL]:
        acl_names = items[0]
        # Return placeholder ACLs - they should be resolved later
        return [ACL(name=name, criterion="") for name in acl_names]

    def routing_block(self, items: list[Any]) -> list[UseBackendRule]:
        return items

    def route_to(self, items: list[Any]) -> UseBackendRule:
        backend = str(items[0])
        condition = items[1][1] if len(items) > 1 and isinstance(items[1], tuple) else None
        return UseBackendRule(backend=backend, condition=condition)

    def route_default(self, items: list[Any]) -> tuple[str, str]:
        return ("default_backend", str(items[0]))

    def single_use_backend(self, items: list[Any]) -> UseBackendRule:
        backend = str(items[0])
        condition = items[1][1] if len(items) > 1 and isinstance(items[1], tuple) else None
        return UseBackendRule(backend=backend, condition=condition)

    # ===== Backend Section =====
    def backend_section(self, items: list[Any]) -> Backend:
        name = str(items[0])
        properties = items[1:]

        mode = Mode.HTTP
        description = None
        disabled = False
        enabled = True
        id = None
        guid = None
        balance = BalanceAlgorithm.ROUNDROBIN
        servers = []
        server_templates = []
        server_loops = []  # Collect for loops
        default_server = None
        health_check = None
        acls = []
        filters = []
        options = []
        http_request_rules = []
        http_response_rules = []
        http_after_response_rules = []
        tcp_request_rules = []
        tcp_response_rules = []
        compression = None
        cookie = None
        stick_table = None
        stick_rules = []
        timeout_server = None
        timeout_connect = None
        timeout_check = None
        timeout_tunnel = None
        timeout_server_fin = None
        retries = None
        maxconn = None
        backlog = None
        max_keep_alive_queue = None
        max_session_srv_conns = None
        log = []
        log_tag = None
        log_format = None
        error_log_format = None
        log_format_sd = None
        redirect_rules = []
        error_files = []
        http_errors = []
        email_alert = None
        declare_captures = []
        force_persist_rules = []
        ignore_persist_rules = []
        errorloc: dict[int, str] = {}
        errorloc302: dict[int, str] = {}
        errorloc303: dict[int, str] = {}
        # TCP keepalive (Phase 5B)
        srvtcpka_cnt = None
        srvtcpka_idle = None
        srvtcpka_intvl = None
        persist_rdp_cookie = None
        errorfiles = None
        dispatch = None
        use_fcgi_app = None
        http_reuse = None
        http_send_name_header = None
        retry_on = None
        http_check_rules = []
        tcp_check_rules = []
        use_server_rules = []
        external_check_command = None
        external_check_path = None
        source = None
        hash_type = None
        hash_balance_factor = None
        hash_preserve_affinity = None  # Phase 5B
        load_server_state_from = None
        server_state_file_name = None

        for prop in properties:
            if isinstance(prop, Server):
                servers.append(prop)
            elif isinstance(prop, ForLoop):
                server_loops.append(prop)
            elif isinstance(prop, DefaultServer):
                default_server = prop
            elif isinstance(prop, ACL):
                acls.append(prop)
            elif isinstance(prop, RedirectRule):
                redirect_rules.append(prop)
            elif isinstance(prop, ErrorFile):
                error_files.append(prop)
            elif isinstance(prop, HttpError):
                http_errors.append(prop)
            elif isinstance(prop, EmailAlert):
                email_alert = prop
            elif isinstance(prop, DeclareCapture):
                declare_captures.append(prop)
            elif isinstance(prop, ForcePersistRule):
                force_persist_rules.append(prop)
            elif isinstance(prop, IgnorePersistRule):
                ignore_persist_rules.append(prop)
            elif isinstance(prop, HttpCheckRule):
                http_check_rules.append(prop)
            elif isinstance(prop, TcpCheckRule):
                tcp_check_rules.append(prop)
            elif isinstance(prop, UseServerRule):
                use_server_rules.append(prop)
            elif isinstance(prop, StickTable):
                stick_table = prop
            elif isinstance(prop, StickRule):
                stick_rules.append(prop)
            elif isinstance(prop, list):
                # Handle mixed lists of servers and loops
                for item in prop:
                    if isinstance(item, Server):
                        servers.append(item)
                    elif isinstance(item, ForLoop):
                        server_loops.append(item)
                    elif isinstance(item, HttpRequestRule):
                        http_request_rules.append(item)
                    elif isinstance(item, HttpResponseRule):
                        http_response_rules.append(item)
                    elif isinstance(item, HttpAfterResponseRule):
                        http_after_response_rules.append(item)
                    elif isinstance(item, TcpRequestRule):
                        tcp_request_rules.append(item)
                    elif isinstance(item, TcpResponseRule):
                        tcp_response_rules.append(item)
                    elif isinstance(item, HttpCheckRule):
                        http_check_rules.append(item)
                    elif isinstance(item, TcpCheckRule):
                        tcp_check_rules.append(item)
                    elif isinstance(item, UseServerRule):
                        use_server_rules.append(item)
            elif isinstance(prop, ServerTemplate):
                server_templates.append(prop)
            elif isinstance(prop, HealthCheck):
                health_check = prop
            elif isinstance(prop, CompressionConfig):
                compression = prop
            elif isinstance(prop, list) and all(isinstance(x, HttpRequestRule) for x in prop):
                http_request_rules.extend(prop)
            elif isinstance(prop, list) and all(isinstance(x, HttpResponseRule) for x in prop):
                http_response_rules.extend(prop)
            elif isinstance(prop, list) and all(isinstance(x, HttpAfterResponseRule) for x in prop):
                http_after_response_rules.extend(prop)
            elif isinstance(prop, tuple):
                key, value = prop
                if key == "mode":
                    mode = Mode(value)
                elif key == "description":
                    description = value
                elif key == "disabled":
                    disabled = value
                elif key == "enabled":
                    enabled = value
                elif key == "id":
                    id = value
                elif key == "guid":
                    guid = value
                elif key == "balance":
                    balance = BalanceAlgorithm(value)
                elif key == "option":
                    if isinstance(value, list):
                        options.extend(value)
                    else:
                        options.append(value)
                elif key == "cookie":
                    cookie = value
                elif key == "timeout_server":
                    timeout_server = value
                elif key == "timeout_connect":
                    timeout_connect = value
                elif key == "timeout_check":
                    timeout_check = value
                elif key == "timeout_tunnel":
                    timeout_tunnel = value
                elif key == "timeout_server_fin":
                    timeout_server_fin = value
                elif key == "retries":
                    retries = value
                elif key == "maxconn":
                    maxconn = value
                elif key == "backlog":
                    backlog = value
                elif key == "max_keep_alive_queue":
                    max_keep_alive_queue = value
                elif key == "max_session_srv_conns":
                    max_session_srv_conns = value
                elif key == "log":
                    log.append(value)
                elif key == "log_tag":
                    log_tag = value
                elif key == "log_format":
                    log_format = value
                elif key == "error_log_format":
                    error_log_format = value
                elif key == "log_format_sd":
                    log_format_sd = value
                elif key == "errorfiles":
                    errorfiles = value
                elif key == "dispatch":
                    dispatch = value
                elif key == "use_fcgi_app":
                    use_fcgi_app = value
                elif key == "external_check_command":
                    external_check_command = value
                elif key == "external_check_path":
                    external_check_path = value
                elif key == "errorloc":
                    errorloc.update(value)
                elif key == "errorloc302":
                    errorloc302.update(value)
                elif key == "errorloc303":
                    errorloc303.update(value)
                elif key == "http_reuse":
                    http_reuse = value
                elif key == "http_send_name_header":
                    http_send_name_header = value
                elif key == "retry_on":
                    retry_on = value
                elif key == "source":
                    source = value
                elif key == "hash_type":
                    hash_type = value
                elif key == "hash_balance_factor":
                    hash_balance_factor = value
                elif key == "hash_preserve_affinity":
                    hash_preserve_affinity = value
                elif key == "load_server_state_from":
                    from ..ir.nodes import LoadServerStateFrom
                    load_server_state_from = LoadServerStateFrom(value)
                elif key == "server_state_file_name":
                    server_state_file_name = value
                elif key == "filters":
                    filters = value
                elif key == "srvtcpka_cnt":
                    srvtcpka_cnt = value
                elif key == "srvtcpka_idle":
                    srvtcpka_idle = value
                elif key == "srvtcpka_intvl":
                    srvtcpka_intvl = value
                elif key == "persist_rdp_cookie":
                    persist_rdp_cookie = value  # Empty string means use default "msts"

        # Build metadata with server loops if any
        metadata = {}
        if server_loops:
            metadata["server_loops"] = server_loops

        return Backend(
            name=name,
            description=description,
            disabled=disabled,
            enabled=enabled,
            id=id,
            guid=guid,
            mode=mode,
            balance=balance,
            servers=servers,
            server_templates=server_templates,
            default_server=default_server,
            health_check=health_check,
            acls=acls,
            filters=filters,
            options=options,
            http_request_rules=http_request_rules,
            http_response_rules=http_response_rules,
            http_after_response_rules=http_after_response_rules,
            tcp_request_rules=tcp_request_rules,
            tcp_response_rules=tcp_response_rules,
            compression=compression,
            cookie=cookie,
            stick_table=stick_table,
            stick_rules=stick_rules,
            timeout_server=timeout_server,
            timeout_connect=timeout_connect,
            timeout_check=timeout_check,
            timeout_tunnel=timeout_tunnel,
            timeout_server_fin=timeout_server_fin,
            retries=retries,
            maxconn=maxconn,
            backlog=backlog,
            max_keep_alive_queue=max_keep_alive_queue,
            max_session_srv_conns=max_session_srv_conns,
            log=log,
            log_tag=log_tag,
            log_format=log_format,
            error_log_format=error_log_format,
            log_format_sd=log_format_sd,
            redirect_rules=redirect_rules,
            error_files=error_files,
            http_errors=http_errors,
            errorloc=errorloc,
            errorloc302=errorloc302,
            errorloc303=errorloc303,
            errorfiles=errorfiles,
            dispatch=dispatch,
            use_fcgi_app=use_fcgi_app,
            http_reuse=http_reuse,
            http_send_name_header=http_send_name_header,
            retry_on=retry_on,
            http_check_rules=http_check_rules,
            tcp_check_rules=tcp_check_rules,
            use_server_rules=use_server_rules,
            external_check_command=external_check_command,
            external_check_path=external_check_path,
            source=source,
            hash_type=hash_type,
            hash_balance_factor=hash_balance_factor,
            hash_preserve_affinity=hash_preserve_affinity,
            load_server_state_from=load_server_state_from,
            server_state_file_name=server_state_file_name,
            email_alert=email_alert,
            declare_captures=declare_captures,
            force_persist_rules=force_persist_rules,
            ignore_persist_rules=ignore_persist_rules,
            srvtcpka_cnt=srvtcpka_cnt,
            srvtcpka_idle=srvtcpka_idle,
            srvtcpka_intvl=srvtcpka_intvl,
            persist_rdp_cookie=persist_rdp_cookie,
            metadata=metadata,
        )

    def backend_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

    def backend_description(self, items: list[Any]) -> tuple[str, str]:
        """Transform description directive."""
        return ("description", str(items[0]))

    def backend_disabled(self, items: list[Any]) -> tuple[str, bool]:
        """Transform disabled directive."""
        return ("disabled", items[0])

    def backend_enabled(self, items: list[Any]) -> tuple[str, bool]:
        """Transform enabled directive."""
        return ("enabled", items[0])

    def backend_id(self, items: list[Any]) -> tuple[str, int]:
        """Transform id directive."""
        return ("id", items[0])

    def backend_guid(self, items: list[Any]) -> tuple[str, str]:
        """Transform guid directive (global unique identifier)."""
        return ("guid", str(items[0]))

    def backend_balance(self, items: list[Any]) -> tuple[str, str]:
        return ("balance", items[0])

    def backend_option(self, items: list[Any]) -> tuple[str, Any]:
        return ("option", items[0])

    def backend_cookie(self, items: list[Any]) -> tuple[str, str]:
        return ("cookie", items[0])

    def backend_health_check(self, items: list[Any]) -> HealthCheck:
        return cast("HealthCheck", items[0])

    def backend_servers(self, items: list[Any]) -> list[Server]:
        return cast("list[Server]", items[0])

    def backend_server_template(self, items: list[Any]) -> ServerTemplate:
        return cast("ServerTemplate", items[0])

    def backend_compression(self, items: list[Any]) -> CompressionConfig:
        return cast("CompressionConfig", items[0])

    def backend_http_request(self, items: list[Any]) -> list[HttpRequestRule]:
        return cast("list[HttpRequestRule]", items[0])

    def backend_http_response(self, items: list[Any]) -> list[HttpResponseRule]:
        return cast("list[HttpResponseRule]", items[0])

    def backend_http_after_response(self, items: list[Any]) -> list[HttpAfterResponseRule]:
        return cast("list[HttpAfterResponseRule]", items[0])

    def backend_timeout_server(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_server", str(items[0]))

    def backend_timeout_connect(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_connect", str(items[0]))

    def backend_timeout_check(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_check", str(items[0]))

    def backend_timeout_tunnel(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_tunnel", str(items[0]))

    def backend_timeout_server_fin(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_server_fin", str(items[0]))

    def backend_retries(self, items: list[Any]) -> tuple[str, int]:
        return ("retries", items[0])

    def backend_maxconn(self, items: list[Any]) -> tuple[str, int]:
        """Transform maxconn directive."""
        return ("maxconn", items[0])

    def backend_backlog(self, items: list[Any]) -> tuple[str, int]:
        """Transform backlog directive."""
        return ("backlog", items[0])

    def backend_max_keep_alive_queue(self, items: list[Any]) -> tuple[str, int]:
        """Transform max-keep-alive-queue directive."""
        return ("max_keep_alive_queue", items[0])

    def backend_max_session_srv_conns(self, items: list[Any]) -> tuple[str, int]:
        """Transform max-session-srv-conns directive."""
        return ("max_session_srv_conns", items[0])

    def backend_log(self, items: list[Any]) -> tuple[str, str]:
        """Transform log directive."""
        return ("log", str(items[0]))

    def backend_log_tag(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-tag directive."""
        return ("log_tag", str(items[0]))

    def backend_log_format(self, items: list[Any]) -> tuple[str, str]:
        return ("log_format", items[0])

    def backend_error_log_format(self, items: list[Any]) -> tuple[str, str]:
        """Transform error-log-format directive."""
        return ("error_log_format", str(items[0]))

    def backend_log_format_sd(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-format-sd directive (RFC 5424 structured data)."""
        return ("log_format_sd", str(items[0]))

    def backend_errorfiles(self, items: list[Any]) -> tuple[str, str]:
        """Transform errorfiles directive (directory for custom error files)."""
        return ("errorfiles", str(items[0]))

    def backend_dispatch(self, items: list[Any]) -> tuple[str, str]:
        """Transform dispatch directive (simple load balancing target)."""
        return ("dispatch", str(items[0]))

    def backend_use_fcgi_app(self, items: list[Any]) -> tuple[str, str]:
        """Transform use-fcgi-app directive (FastCGI application reference)."""
        return ("use_fcgi_app", str(items[0]))

    def backend_external_check_command(self, items: list[Any]) -> tuple[str, str]:
        """Transform external-check command directive."""
        return ("external_check_command", str(items[0]))

    def backend_external_check_path(self, items: list[Any]) -> tuple[str, str]:
        """Transform external-check path directive."""
        return ("external_check_path", str(items[0]))

    def backend_default_server(self, items: list[Any]) -> DefaultServer:
        """Handle default-server in backend."""
        return cast("DefaultServer", items[0])

    # ===== Default Server =====
    def default_server_directive(self, items: list[Any]) -> DefaultServer:
        """Transform default-server directive."""
        check = False
        check_interval = None
        rise = None
        fall = None
        weight = None
        maxconn = None
        ssl = False
        ssl_verify = None
        sni = None
        alpn = []
        send_proxy = False
        send_proxy_v2 = False
        slowstart = None
        check_ssl = False
        check_sni = None
        ssl_min_ver = None
        ssl_max_ver = None
        ca_file = None
        crt = None
        source = None
        options: dict[str, Any] = {}

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "check":
                    check = value
                elif key == "inter":
                    check_interval = value
                elif key == "rise":
                    rise = value
                elif key == "fall":
                    fall = value
                elif key == "weight":
                    weight = value
                elif key == "maxconn":
                    maxconn = value
                elif key == "ssl":
                    ssl = value
                elif key == "verify":
                    ssl_verify = value
                elif key == "sni":
                    sni = value
                elif key == "alpn":
                    alpn = value
                elif key == "send_proxy":
                    send_proxy = value
                elif key == "send_proxy_v2":
                    send_proxy_v2 = value
                elif key == "slowstart":
                    slowstart = value
                elif key == "check_ssl":
                    check_ssl = value
                elif key == "check_sni":
                    check_sni = value
                elif key == "ssl_min_ver":
                    ssl_min_ver = value
                elif key == "ssl_max_ver":
                    ssl_max_ver = value
                elif key == "ca_file":
                    ca_file = value
                elif key == "crt":
                    crt = value
                elif key == "source":
                    source = value

        return DefaultServer(
            check=check,
            check_interval=check_interval,
            rise=rise,
            fall=fall,
            weight=weight,
            maxconn=maxconn,
            ssl=ssl,
            ssl_verify=ssl_verify,
            sni=sni,
            alpn=alpn,
            send_proxy=send_proxy,
            send_proxy_v2=send_proxy_v2,
            slowstart=slowstart,
            check_ssl=check_ssl,
            check_sni=check_sni,
            ssl_min_ver=ssl_min_ver,
            ssl_max_ver=ssl_max_ver,
            ca_file=ca_file,
            crt=crt,
            source=source,
            options=options,
        )

    def ds_check(self, items: list[Any]) -> tuple[str, bool]:
        return ("check", items[0])

    def ds_inter(self, items: list[Any]) -> tuple[str, str]:
        return ("inter", items[0])

    def ds_rise(self, items: list[Any]) -> tuple[str, int]:
        return ("rise", items[0])

    def ds_fall(self, items: list[Any]) -> tuple[str, int]:
        return ("fall", items[0])

    def ds_weight(self, items: list[Any]) -> tuple[str, int]:
        return ("weight", items[0])

    def ds_maxconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxconn", items[0])

    def ds_ssl(self, items: list[Any]) -> tuple[str, bool]:
        return ("ssl", items[0])

    def ds_verify(self, items: list[Any]) -> tuple[str, str]:
        return ("verify", items[0])

    def ds_sni(self, items: list[Any]) -> tuple[str, str]:
        return ("sni", items[0])

    def ds_alpn(self, items: list[Any]) -> tuple[str, list[str]]:
        return ("alpn", items[0])

    def ds_send_proxy(self, items: list[Any]) -> tuple[str, bool]:
        return ("send_proxy", items[0])

    def ds_send_proxy_v2(self, items: list[Any]) -> tuple[str, bool]:
        return ("send_proxy_v2", items[0])

    def ds_slowstart(self, items: list[Any]) -> tuple[str, str]:
        return ("slowstart", items[0])

    def ds_check_ssl(self, items: list[Any]) -> tuple[str, bool]:
        return ("check_ssl", items[0])

    def ds_check_sni(self, items: list[Any]) -> tuple[str, str]:
        return ("check_sni", items[0])

    def ds_ssl_min_ver(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_min_ver", items[0])

    def ds_ssl_max_ver(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_max_ver", items[0])

    def ds_ca_file(self, items: list[Any]) -> tuple[str, str]:
        return ("ca_file", items[0])

    def ds_crt(self, items: list[Any]) -> tuple[str, str]:
        return ("crt", items[0])

    def ds_source(self, items: list[Any]) -> tuple[str, str]:
        return ("source", items[0])

    # ===== Listen Section =====
    def listen_section(self, items: list[Any]) -> Listen:
        name = str(items[0])
        properties = items[1:]

        binds = []
        mode = Mode.HTTP
        description = None
        disabled = False
        enabled = True
        id = None
        guid = None
        balance = BalanceAlgorithm.ROUNDROBIN
        servers = []
        server_loops = []
        acls = []
        filters = []
        http_request_rules = []
        http_response_rules = []
        http_after_response_rules = []
        tcp_request_rules = []
        tcp_response_rules = []
        quic_initial_rules = []
        options = []
        timeout_client = None
        timeout_server = None
        timeout_connect = None
        maxconn = None
        health_check = None
        load_server_state_from = None
        server_state_file_name = None
        log_tag = None
        log_format = None
        error_log_format = None
        log_format_sd = None
        log_steps = None
        http_errors = []
        email_alert = None
        declare_captures = []
        force_persist_rules = []
        ignore_persist_rules = []
        rate_limit_sessions = None
        persist_rdp_cookie = None

        for prop in properties:
            if isinstance(prop, Bind):
                binds.append(prop)
            elif isinstance(prop, ACL):
                acls.append(prop)
            elif isinstance(prop, list):
                if all(isinstance(x, ACL) for x in prop):
                    acls.extend(prop)
                elif all(isinstance(x, Server) for x in prop):
                    servers.extend(prop)
                else:
                    # Handle mixed lists
                    for item in prop:
                        if isinstance(item, Server):
                            servers.append(item)
                        elif isinstance(item, ForLoop):
                            server_loops.append(item)
                        elif isinstance(item, ACL):
                            acls.append(item)
                        elif isinstance(item, HttpRequestRule):
                            http_request_rules.append(item)
                        elif isinstance(item, HttpResponseRule):
                            http_response_rules.append(item)
                        elif isinstance(item, HttpAfterResponseRule):
                            http_after_response_rules.append(item)
                        elif isinstance(item, TcpRequestRule):
                            tcp_request_rules.append(item)
                        elif isinstance(item, TcpResponseRule):
                            tcp_response_rules.append(item)
                        elif isinstance(item, QuicInitialRule):
                            quic_initial_rules.append(item)
            elif isinstance(prop, Server):
                servers.append(prop)
            elif isinstance(prop, ForLoop):
                server_loops.append(prop)
            elif isinstance(prop, HealthCheck):
                health_check = prop
            elif isinstance(prop, HttpError):
                http_errors.append(prop)
            elif isinstance(prop, EmailAlert):
                email_alert = prop
            elif isinstance(prop, DeclareCapture):
                declare_captures.append(prop)
            elif isinstance(prop, ForcePersistRule):
                force_persist_rules.append(prop)
            elif isinstance(prop, IgnorePersistRule):
                ignore_persist_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, HttpAfterResponseRule) for x in prop):
                http_after_response_rules.extend(prop)
            elif isinstance(prop, list) and all(isinstance(x, TcpRequestRule) for x in prop):
                tcp_request_rules.extend(prop)
            elif isinstance(prop, list) and all(isinstance(x, TcpResponseRule) for x in prop):
                tcp_response_rules.extend(prop)
            elif isinstance(prop, list) and all(isinstance(x, QuicInitialRule) for x in prop):
                quic_initial_rules.extend(prop)
            elif isinstance(prop, tuple):
                key, value = prop
                if key == "mode":
                    mode = Mode(value)
                elif key == "description":
                    description = value
                elif key == "disabled":
                    disabled = value
                elif key == "enabled":
                    enabled = value
                elif key == "id":
                    id = value
                elif key == "guid":
                    guid = value
                elif key == "balance":
                    balance = BalanceAlgorithm(value)
                elif key == "option":
                    if isinstance(value, list):
                        options.extend(value)
                    else:
                        options.append(value)
                elif key == "timeout_client":
                    timeout_client = value
                elif key == "timeout_server":
                    timeout_server = value
                elif key == "timeout_connect":
                    timeout_connect = value
                elif key == "maxconn":
                    maxconn = value
                elif key == "load_server_state_from":
                    from ..ir.nodes import LoadServerStateFrom
                    load_server_state_from = LoadServerStateFrom(value)
                elif key == "server_state_file_name":
                    server_state_file_name = value
                elif key == "log_tag":
                    log_tag = value
                elif key == "log_format":
                    log_format = value
                elif key == "error_log_format":
                    error_log_format = value
                elif key == "log_format_sd":
                    log_format_sd = value
                elif key == "log_steps":
                    log_steps = value
                elif key == "rate_limit_sessions":
                    rate_limit_sessions = value
                elif key == "filters":
                    filters = value
                elif key == "persist_rdp_cookie":
                    persist_rdp_cookie = value  # Empty string means use default "msts"

        # Build metadata
        metadata: dict[str, Any] = {}
        if server_loops:
            metadata["server_loops"] = server_loops
        if timeout_client:
            metadata["timeout_client"] = timeout_client
        if timeout_server:
            metadata["timeout_server"] = timeout_server
        if timeout_connect:
            metadata["timeout_connect"] = timeout_connect
        if maxconn:
            metadata["maxconn"] = maxconn
        if health_check:
            metadata["health_check"] = health_check

        return Listen(
            name=name,
            description=description,
            disabled=disabled,
            enabled=enabled,
            id=id,
            guid=guid,
            binds=binds,
            mode=mode,
            balance=balance,
            servers=servers,
            acls=acls,
            filters=filters,
            http_request_rules=http_request_rules,
            http_response_rules=http_response_rules,
            http_after_response_rules=http_after_response_rules,
            tcp_request_rules=tcp_request_rules,
            tcp_response_rules=tcp_response_rules,
            quic_initial_rules=quic_initial_rules,
            options=options,
            load_server_state_from=load_server_state_from,
            server_state_file_name=server_state_file_name,
            log_tag=log_tag,
            log_format=log_format,
            error_log_format=error_log_format,
            log_format_sd=log_format_sd,
            log_steps=log_steps,
            http_errors=http_errors,
            email_alert=email_alert,
            declare_captures=declare_captures,
            force_persist_rules=force_persist_rules,
            ignore_persist_rules=ignore_persist_rules,
            rate_limit_sessions=rate_limit_sessions,
            persist_rdp_cookie=persist_rdp_cookie,
            metadata=metadata,
        )

    def listen_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

    def listen_description(self, items: list[Any]) -> tuple[str, str]:
        """Transform description directive."""
        return ("description", str(items[0]))

    def listen_disabled(self, items: list[Any]) -> tuple[str, bool]:
        """Transform disabled directive."""
        return ("disabled", items[0])

    def listen_enabled(self, items: list[Any]) -> tuple[str, bool]:
        """Transform enabled directive."""
        return ("enabled", items[0])

    def listen_id(self, items: list[Any]) -> tuple[str, int]:
        """Transform id directive."""
        return ("id", items[0])

    def listen_guid(self, items: list[Any]) -> tuple[str, str]:
        """Transform guid directive (global unique identifier)."""
        return ("guid", str(items[0]))

    def listen_balance(self, items: list[Any]) -> tuple[str, str]:
        return ("balance", items[0])

    def listen_option(self, items: list[Any]) -> tuple[str, Any]:
        return ("option", items[0])

    def listen_servers(self, items: list[Any]) -> list[Server]:
        return cast("list[Server]", items[0])

    def listen_health_check(self, items: list[Any]) -> HealthCheck:
        return cast("HealthCheck", items[0])

    def listen_timeout_client(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_client", str(items[0]))

    def listen_timeout_server(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_server", str(items[0]))

    def listen_timeout_connect(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_connect", str(items[0]))

    def listen_maxconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxconn", items[0])

    def listen_load_server_state_from(self, items: list[Any]) -> tuple[str, str]:
        """Transform load-server-state-from-file directive."""
        return ("load_server_state_from", str(items[0]))

    def listen_server_state_file_name(self, items: list[Any]) -> tuple[str, str]:
        """Transform server-state-file-name directive (use-backend-name or file path)."""
        return ("server_state_file_name", str(items[0]))

    def listen_log_tag(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-tag directive (tag for log messages)."""
        return ("log_tag", str(items[0]))

    def listen_log_format(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-format directive (custom log format string)."""
        return ("log_format", str(items[0]))

    def listen_error_log_format(self, items: list[Any]) -> tuple[str, str]:
        """Transform error-log-format directive (custom error log format string)."""
        return ("error_log_format", str(items[0]))

    def listen_log_format_sd(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-format-sd directive (structured data log format - RFC 5424)."""
        return ("log_format_sd", str(items[0]))

    def listen_log_steps(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-steps directive (logging steps for transaction processing)."""
        return ("log_steps", str(items[0]))

    def health_check_block(self, items: list[Any]) -> HealthCheck:
        method = "GET"
        uri = "/"
        expect_status = None
        expect_string = None
        expect_rstatus = None
        expect_rstring = None
        expect_negate = False
        headers = {}

        for item in items:
            if isinstance(item, tuple):
                # Handle 2-tuples (method, uri, headers) and 3-tuples (expect types)
                if len(item) == 2:
                    key, value = item
                    if key == "method":
                        method = value
                    elif key == "uri":
                        uri = value
                elif len(item) == 3:
                    # New format: (type, value, negate) from expect_* transformers
                    expect_type, expect_value, negate = item
                    if expect_type == "status":
                        expect_status = expect_value
                        expect_negate = negate
                    elif expect_type == "string":
                        expect_string = expect_value
                        expect_negate = negate
                    elif expect_type == "rstatus":
                        expect_rstatus = expect_value
                        expect_negate = negate
                    elif expect_type == "rstring":
                        expect_rstring = expect_value
                        expect_negate = negate
                    elif expect_type == "header":
                        # Header tuple: ("header", name, value)
                        headers[expect_value] = negate  # Using negate as third value
                    else:
                        # Unknown 3-tuple, try old logic
                        header_name = item[1]
                        header_value = item[2]
                        headers[header_name] = header_value

        return HealthCheck(
            method=method,
            uri=uri,
            expect_status=expect_status,
            expect_string=expect_string,
            expect_rstatus=expect_rstatus,
            expect_rstring=expect_rstring,
            expect_negate=expect_negate,
            headers=headers
        )

    def hc_method(self, items: list[Any]) -> tuple[str, str]:
        return ("method", items[0])

    def hc_uri(self, items: list[Any]) -> tuple[str, str]:
        return ("uri", items[0])

    def hc_expect(self, items: list[Any]) -> tuple[str, Any]:
        """Handle expect value (status, string, rstatus, rstring, negated)."""
        return cast("tuple[str, Any]", items[0])

    def hc_header(self, items: list[Any]) -> tuple[str, str, str]:
        return ("header", items[0][0], items[0][1])

    def expect_status(self, items: list[Any]) -> tuple[str, int, bool]:
        return ("status", items[0], False)

    def expect_string(self, items: list[Any]) -> tuple[str, str, bool]:
        return ("string", items[0], False)

    def expect_rstatus(self, items: list[Any]) -> tuple[str, str, bool]:
        return ("rstatus", items[0], False)

    def expect_rstring(self, items: list[Any]) -> tuple[str, str, bool]:
        return ("rstring", items[0], False)

    def expect_not_status(self, items: list[Any]) -> tuple[str, int, bool]:
        return ("status", items[0], True)

    def expect_not_string(self, items: list[Any]) -> tuple[str, str, bool]:
        return ("string", items[0], True)

    def expect_not_rstatus(self, items: list[Any]) -> tuple[str, str, bool]:
        return ("rstatus", items[0], True)

    def expect_not_rstring(self, items: list[Any]) -> tuple[str, str, bool]:
        return ("rstring", items[0], True)

    def header_definition(self, items: list[Any]) -> tuple[str, str]:
        return (items[0], items[1])

    def servers_block(self, items: list[Any]) -> list[Server | ForLoop]:
        """Return list of servers and/or for loops."""
        result = []
        for item in items:
            if isinstance(item, (Server, ForLoop)):
                result.append(item)
            elif isinstance(item, list):
                # Extend with list items (handles nested structures)
                result.extend(item)
        return result

    def server_definition(self, items: list[Any]) -> Server:
        name = str(items[0])
        properties = items[1:]

        address = ""
        port = 8080
        check = False
        check_interval = None
        rise = 2
        fall = 3
        weight = 1
        maxconn = None
        ssl = False
        ssl_verify = None
        sni = None
        alpn = []
        backup = False
        send_proxy = False
        send_proxy_v2 = False
        slowstart = None
        check_ssl = False
        check_sni = None
        ssl_min_ver = None
        ssl_max_ver = None
        ca_file = None
        crt = None
        source = None
        template_spreads = []
        options = {}  # Collect additional server options

        for prop in properties:
            if isinstance(prop, tuple):
                key, value = prop
                if key == "__template_spread__":
                    # Store template spread for later expansion
                    template_spreads.append(value)
                elif key == "address":
                    address = value
                elif key == "port":
                    port = value
                elif key == "check":
                    check = value
                elif key == "inter":
                    check_interval = value
                elif key == "rise":
                    rise = value
                elif key == "fall":
                    fall = value
                elif key == "weight":
                    weight = value
                elif key == "maxconn":
                    maxconn = value
                elif key == "ssl":
                    ssl = value
                elif key == "verify":
                    ssl_verify = value
                elif key == "sni":
                    sni = value
                elif key == "alpn":
                    alpn = value
                elif key == "backup":
                    backup = value
                elif key == "send_proxy":
                    send_proxy = value
                elif key == "send_proxy_v2":
                    send_proxy_v2 = value
                elif key == "slowstart":
                    slowstart = value
                elif key == "check_ssl":
                    check_ssl = value
                elif key == "check_sni":
                    check_sni = value
                elif key == "ssl_min_ver":
                    ssl_min_ver = value
                elif key == "ssl_max_ver":
                    ssl_max_ver = value
                elif key == "ca_file":
                    ca_file = value
                elif key == "crt":
                    crt = value
                elif key == "source":
                    source = value
                else:
                    # Collect all other options into the options dict
                    # Convert underscores to hyphens for HAProxy syntax
                    haproxy_key = key.replace("_", "-")
                    options[haproxy_key] = value

        # Build metadata with template spreads if any
        metadata = {}
        if template_spreads:
            metadata["template_spreads"] = template_spreads

        return Server(
            name=name,
            address=address,
            port=port,
            check=check,
            check_interval=check_interval,
            rise=rise,
            fall=fall,
            weight=weight,
            maxconn=maxconn,
            ssl=ssl,
            ssl_verify=ssl_verify,
            sni=sni,
            alpn=alpn,
            backup=backup,
            send_proxy=send_proxy,
            send_proxy_v2=send_proxy_v2,
            slowstart=slowstart,
            check_ssl=check_ssl,
            check_sni=check_sni,
            ssl_min_ver=ssl_min_ver,
            ssl_max_ver=ssl_max_ver,
            ca_file=ca_file,
            crt=crt,
            source=source,
            options=options,
            metadata=metadata,
        )

    def server_inline(self, items: list[Any]) -> Server:
        name = str(items[0])
        params = items[1:]

        properties = {}
        for param in params:
            if isinstance(param, tuple):
                properties[param[0]] = param[1]

        return Server(
            name=name,
            address=properties.get("address", ""),
            port=properties.get("port", 8080),
            check=properties.get("check", False),
            check_interval=properties.get("inter"),
            rise=properties.get("rise", 2),
            fall=properties.get("fall", 3),
            weight=properties.get("weight", 1),
            maxconn=properties.get("maxconn"),
            ssl=properties.get("ssl", False),
            ssl_verify=properties.get("verify"),
            backup=properties.get("backup", False),
        )

    def server_inline_param(self, items: list[Any]) -> tuple[str, Any]:
        return (str(items[0]), items[1])

    def server_address(self, items: list[Any]) -> tuple[str, str]:
        return ("address", items[0])

    def server_port(self, items: list[Any]) -> tuple[str, int | str]:
        # Port can be either a number or a string with variable interpolation
        value = items[0]
        if isinstance(value, str):
            # If it's a string, it may contain ${var} - return as-is for variable resolution
            return ("port", value)
        # Otherwise it's a number
        return ("port", int(value))

    def server_check(self, items: list[Any]) -> tuple[str, bool]:
        return ("check", items[0])

    def server_inter(self, items: list[Any]) -> tuple[str, str]:
        return ("inter", str(items[0]))

    def server_rise(self, items: list[Any]) -> tuple[str, int]:
        return ("rise", items[0])

    def server_fall(self, items: list[Any]) -> tuple[str, int]:
        return ("fall", items[0])

    def server_weight(self, items: list[Any]) -> tuple[str, int]:
        return ("weight", items[0])

    def server_maxconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxconn", items[0])

    def server_ssl(self, items: list[Any]) -> tuple[str, bool]:
        return ("ssl", items[0])

    def server_verify(self, items: list[Any]) -> tuple[str, str]:
        return ("verify", items[0])

    def server_sni(self, items: list[Any]) -> tuple[str, str]:
        return ("sni", items[0])

    def server_alpn(self, items: list[Any]) -> tuple[str, list[str]]:
        return ("alpn", items[0])

    def server_backup(self, items: list[Any]) -> tuple[str, bool]:
        return ("backup", items[0])

    def server_send_proxy(self, items: list[Any]) -> tuple[str, bool]:
        return ("send_proxy", items[0])

    def server_send_proxy_v2(self, items: list[Any]) -> tuple[str, bool]:
        return ("send_proxy_v2", items[0])

    def server_slowstart(self, items: list[Any]) -> tuple[str, str]:
        return ("slowstart", items[0])

    def server_check_ssl(self, items: list[Any]) -> tuple[str, bool]:
        return ("check_ssl", items[0])

    def server_check_sni(self, items: list[Any]) -> tuple[str, str]:
        return ("check_sni", items[0])

    def server_ssl_min_ver(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_min_ver", items[0])

    def server_ssl_max_ver(self, items: list[Any]) -> tuple[str, str]:
        return ("ssl_max_ver", items[0])

    def server_ca_file(self, items: list[Any]) -> tuple[str, str]:
        return ("ca_file", items[0])

    def server_crt(self, items: list[Any]) -> tuple[str, str]:
        return ("crt", items[0])

    def server_source(self, items: list[Any]) -> tuple[str, str]:
        return ("source", items[0])

    # New server options
    def server_id(self, items: list[Any]) -> tuple[str, int]:
        return ("id", items[0])

    def server_cookie(self, items: list[Any]) -> tuple[str, str]:
        return ("cookie", items[0])

    def server_disabled(self, items: list[Any]) -> tuple[str, bool]:
        return ("disabled", items[0])

    def server_enabled(self, items: list[Any]) -> tuple[str, bool]:
        return ("enabled", items[0])

    def server_minconn(self, items: list[Any]) -> tuple[str, int]:
        return ("minconn", items[0])

    def server_maxqueue(self, items: list[Any]) -> tuple[str, int]:
        return ("maxqueue", items[0])

    def server_init_addr(self, items: list[Any]) -> tuple[str, str]:
        return ("init_addr", items[0])

    def server_max_reuse(self, items: list[Any]) -> tuple[str, int]:
        return ("max_reuse", items[0])

    def server_pool_max_conn(self, items: list[Any]) -> tuple[str, int]:
        return ("pool_max_conn", items[0])

    def server_pool_purge_delay(self, items: list[Any]) -> tuple[str, str]:
        return ("pool_purge_delay", str(items[0]))

    def server_resolvers(self, items: list[Any]) -> tuple[str, str]:
        return ("resolvers", items[0])

    def server_resolve_prefer(self, items: list[Any]) -> tuple[str, str]:
        return ("resolve_prefer", items[0])

    def server_error_limit(self, items: list[Any]) -> tuple[str, int]:
        return ("error_limit", items[0])

    def server_observe(self, items: list[Any]) -> tuple[str, str]:
        return ("observe", items[0])

    def server_on_error(self, items: list[Any]) -> tuple[str, str]:
        return ("on_error", items[0])

    def server_on_marked_down(self, items: list[Any]) -> tuple[str, str]:
        return ("on_marked_down", items[0])

    def server_on_marked_up(self, items: list[Any]) -> tuple[str, str]:
        return ("on_marked_up", items[0])

    def server_proto(self, items: list[Any]) -> tuple[str, str]:
        return ("proto", items[0])

    def server_redir(self, items: list[Any]) -> tuple[str, str]:
        return ("redir", items[0])

    def server_tfo(self, items: list[Any]) -> tuple[str, bool]:
        return ("tfo", items[0])

    def server_track(self, items: list[Any]) -> tuple[str, str]:
        return ("track", items[0])

    def server_usesrc(self, items: list[Any]) -> tuple[str, str]:
        return ("usesrc", items[0])

    def server_namespace(self, items: list[Any]) -> tuple[str, str]:
        return ("namespace", items[0])

    def server_agent_check(self, items: list[Any]) -> tuple[str, bool]:
        return ("agent_check", items[0])

    def server_agent_port(self, items: list[Any]) -> tuple[str, int]:
        return ("agent_port", items[0])

    def server_agent_addr(self, items: list[Any]) -> tuple[str, str]:
        return ("agent_addr", items[0])

    def server_agent_inter(self, items: list[Any]) -> tuple[str, str]:
        return ("agent_inter", str(items[0]))

    def server_agent_send(self, items: list[Any]) -> tuple[str, str]:
        return ("agent_send", items[0])

    def server_check_proto(self, items: list[Any]) -> tuple[str, str]:
        return ("check_proto", items[0])

    def server_check_send_proxy(self, items: list[Any]) -> tuple[str, bool]:
        return ("check_send_proxy", items[0])

    def server_template_spread(self, items: list[Any]) -> tuple[str, str]:
        """Return template spread as metadata marker."""
        template_name = str(items[0])
        return ("__template_spread__", template_name)

    def server_template_block(self, items: list[Any]) -> ServerTemplate:
        name = str(items[0])
        range_vals = items[1]
        properties = items[2:]

        start, end = range_vals
        count = end - start + 1
        fqdn_pattern = f"{name}-{{id}}.example.com"

        # Build base server from properties
        server_props = {}
        for prop in properties:
            if isinstance(prop, tuple):
                server_props[prop[0]] = prop[1]

        base_server = Server(
            name=name,
            address=fqdn_pattern,
            port=server_props.get("port", 8080),
            check=server_props.get("check", False),
            check_interval=server_props.get("inter"),
            rise=server_props.get("rise", 2),
            fall=server_props.get("fall", 3),
            weight=server_props.get("weight", 1),
            maxconn=server_props.get("maxconn"),
        )

        return ServerTemplate(
            prefix=name,
            count=count,
            fqdn_pattern=fqdn_pattern,
            port=base_server.port,
            base_server=base_server,
        )

    def compression_block(self, items: list[Any]) -> CompressionConfig:
        algo = "gzip"
        types = []

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "algo":
                    algo = value
                elif key == "type":
                    types = value

        return CompressionConfig(algo=algo, types=types)

    def compression_algo(self, items: list[Any]) -> tuple[str, str]:
        return ("algo", items[0])

    def compression_type(self, items: list[Any]) -> tuple[str, list[str]]:
        return ("type", items[0])

    # ===== Filter Block =====
    def filters_block(self, items: list[Any]) -> list[Filter]:
        """Transform filters block containing list of filter objects."""
        return [item for item in items if isinstance(item, Filter)]

    def filter_item(self, items: list[Any]) -> Filter:
        """Transform individual filter object."""
        filter_type = ""
        name = None
        engine = None
        config = None
        default_limit = None
        default_period = None
        limit = None
        period = None
        key = None
        table = None
        parameters: dict[str, str] = {}

        for item in items:
            if isinstance(item, tuple):
                prop_key, value = item
                if prop_key == "type":
                    filter_type = value
                elif prop_key == "name":
                    name = value
                elif prop_key == "engine":
                    engine = value
                elif prop_key == "config":
                    config = value
                elif prop_key == "default_limit":
                    default_limit = value
                elif prop_key == "default_period":
                    default_period = value
                elif prop_key == "limit":
                    limit = value
                elif prop_key == "period":
                    period = value
                elif prop_key == "key":
                    key = value
                elif prop_key == "table":
                    table = value

        return Filter(
            filter_type=filter_type,
            name=name,
            engine=engine,
            config=config,
            default_limit=default_limit,
            default_period=default_period,
            limit=limit,
            period=period,
            key=key,
            table=table,
            parameters=parameters,
        )

    def filter_type(self, items: list[Any]) -> tuple[str, str]:
        return ("type", items[0])

    def filter_name(self, items: list[Any]) -> tuple[str, str]:
        return ("name", items[0])

    def filter_engine(self, items: list[Any]) -> tuple[str, str]:
        return ("engine", items[0])

    def filter_config(self, items: list[Any]) -> tuple[str, str]:
        return ("config", items[0])

    def filter_default_limit(self, items: list[Any]) -> tuple[str, str]:
        return ("default_limit", items[0])

    def filter_default_period(self, items: list[Any]) -> tuple[str, str]:
        return ("default_period", items[0])

    def filter_limit(self, items: list[Any]) -> tuple[str, str]:
        return ("limit", items[0])

    def filter_period(self, items: list[Any]) -> tuple[str, str]:
        return ("period", items[0])

    def filter_key(self, items: list[Any]) -> tuple[str, str]:
        return ("key", items[0])

    def filter_table(self, items: list[Any]) -> tuple[str, str]:
        return ("table", items[0])

    # Section-specific filter handlers
    def frontend_filters(self, items: list[Any]) -> tuple[str, list[Filter]]:
        """Transform frontend filters block."""
        filters = items[0] if items else []
        return ("filters", filters)

    def backend_filters(self, items: list[Any]) -> tuple[str, list[Filter]]:
        """Transform backend filters block."""
        filters = items[0] if items else []
        return ("filters", filters)

    def listen_filters(self, items: list[Any]) -> tuple[str, list[Filter]]:
        """Transform listen filters block."""
        filters = items[0] if items else []
        return ("filters", filters)

    # ===== ACL =====
    def acl_block(self, items: list[Any]) -> list[ACL]:
        """Transform ACL block containing multiple ACLs."""
        return [item for item in items if isinstance(item, ACL)]

    def acl_item(self, items: list[Any]) -> ACL:
        """Transform single ACL item: name criterion values..."""
        name = str(items[0])
        criterion = str(items[1]) if len(items) > 1 else ""
        values = [str(v) for v in items[2:]]
        return ACL(name=name, criterion=criterion, values=values)

    def acl_definition(self, items: list[Any]) -> ACL:
        name = str(items[0])

        # items[1] is the result of acl_criterion, which is a list
        if len(items) > 1 and isinstance(items[1], list):
            criterion_items = items[1]
            criterion = str(criterion_items[0]) if criterion_items else ""
            values = [str(v) for v in criterion_items[1:]]
        else:
            criterion = ""
            values = []

        return ACL(name=name, criterion=criterion, values=values)

    def acl_criterion(self, items: list[Any]) -> list[Any]:
        return items

    # ===== Template =====
    def template_property(self, items: list[Any]) -> tuple[str, Any]:
        """Transform template property to (key, value) tuple."""
        key = str(items[0])
        value = items[1] if len(items) > 1 else None
        return (key, value)

    def template_definition(self, items: list[Any]) -> Template:
        name = str(items[0])
        properties = {}

        for item in items[1:]:
            if isinstance(item, tuple):
                properties[item[0]] = item[1]

        return Template(name=name, parameters=properties, applies_to="server")

    def template_spread(self, items: list[Any]) -> str:
        return str(items[0])

    # ===== Variable =====
    def variable_declaration(self, items: list[Any]) -> Variable:
        name = str(items[0])
        value = items[1]
        return Variable(name=name, value=value)

    # ===== Import =====
    def import_statement(self, items: list[Any]) -> str:
        return f"import:{items[0]}"

    # ===== Control Flow =====
    def for_statement(self, items: list[Any]) -> ForLoop:
        var_name = str(items[0])
        iterable = items[1]
        body = items[2:]

        return ForLoop(variable=var_name, iterable=iterable, body=body)

    def for_iterable(self, items: list[Any]) -> Any:
        return items[0]

    def for_body(self, items: list[Any]) -> list[Any]:
        return items

    def range_expr(self, items: list[Any]) -> tuple[int, int]:
        return (items[0], items[1])

    # ===== Expressions =====
    def expression(self, items: list[Any]) -> Any:
        return items[0] if items else None

    def env_call(self, items: list[Any]) -> str:
        from ..transformers.variable_resolver import resolve_env_variable

        var_name = items[0]
        default = items[1] if len(items) > 1 else None

        return str(resolve_env_variable(var_name, default))

    # ===== Primitives =====
    def identifier(self, items: list[Token]) -> str:
        return str(items[0])

    # Enum value extractors - extract string from grammar alternatives
    def mode_value(self, items: list[Token]) -> str:
        """Extract mode string from grammar alternatives."""
        return str(items[0]) if items else "http"

    def balance_algo(self, items: list[Token]) -> str:
        """Extract balance algorithm string from grammar alternatives."""
        return str(items[0]) if items else "roundrobin"

    def log_facility(self, items: list[Token]) -> str:
        """Extract log facility string from grammar alternatives."""
        return str(items[0]) if items else "local0"

    def log_level(self, items: list[Token]) -> str:
        """Extract log level string from grammar alternatives."""
        return str(items[0]) if items else "info"

    def bind_address(self, items: list[Any]) -> str:
        """Extract bind address string."""
        return str(items[0]) if items else "*:80"

    def string(self, items: list[Token]) -> str:
        value = str(items[0])
        # Remove quotes if present
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        return value

    def number(self, items: list[Any]) -> int | float:
        return cast("int | float", items[0])

    def INT(self, token: Token) -> int:
        return int(token)

    def FLOAT(self, token: Token) -> float:
        return float(token)

    def boolean(self, items: list[Token]) -> bool:
        # Handle multiple boolean representations: true/false, yes/no, on/off, 1/0
        if items:
            value = str(items[0]).lower()
            return value in ("true", "yes", "on", "1")
        return False

    def BOOLEAN(self, token: Token) -> str:
        """Pass through BOOLEAN token value."""
        return str(token)

    def duration(self, items: list[Any]) -> str:
        return f"{items[0]}{items[1]}"

    def string_array(self, items: list[Any]) -> list[str]:
        return items[0] if items else []

    def string_list(self, items: list[Any]) -> list[str]:
        return items

    def identifier_array(self, items: list[Any]) -> list[str]:
        return items[0] if items else []

    def identifier_list(self, items: list[Any]) -> list[str]:
        return items

    def array(self, items: list[Any]) -> list[Any]:
        return items[0] if items else []

    def value_list(self, items: list[Any]) -> list[Any]:
        return items

    def object(self, items: list[Any]) -> dict[str, Any]:
        if not items:
            return {}
        return dict(items[0])

    def object_pair_list(self, items: list[Any]) -> list[tuple[str, Any]]:
        return items

    def object_pair(self, items: list[Any]) -> tuple[str, Any]:
        return (str(items[0]), items[1])

    def LUA_CODE(self, token: Token) -> str:
        return str(token).strip()

    # ===== Stick Table Support =====
    def stick_table_block(self, items: list[Any]) -> StickTable:
        """Transform stick-table block."""
        table_type = "ip"
        size = 100000
        expire = None
        nopurge = False
        peers = None
        store = []

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "type":
                    table_type = value
                elif key == "size":
                    size = int(value)
                elif key == "expire":
                    expire = value
                elif key == "nopurge":
                    nopurge = value
                elif key == "peers":
                    peers = value
                elif key == "store":
                    store = value if isinstance(value, list) else [value]

        return StickTable(
            type=table_type,
            size=size,
            expire=expire,
            nopurge=nopurge,
            peers=peers,
            store=store,
        )

    def stick_table_type(self, items: list[Token]) -> str:
        """Extract stick-table type from grammar alternatives."""
        if items:
            # Extract the token value and convert to lowercase string
            return str(items[0]).strip('"').lower()
        return "ip"

    def stick_table_type_prop(self, items: list[Any]) -> tuple[str, str]:
        # items[0] should be the result of stick_table_type transformer
        return ("type", str(items[0]))

    def stick_table_size(self, items: list[Any]) -> tuple[str, int]:
        return ("size", int(items[0]))

    def stick_table_expire(self, items: list[Any]) -> tuple[str, str]:
        return ("expire", str(items[0]))

    def stick_table_nopurge(self, items: list[Any]) -> tuple[str, bool]:
        return ("nopurge", bool(items[0]))

    def stick_table_peers(self, items: list[Any]) -> tuple[str, str]:
        return ("peers", str(items[0]))

    def stick_table_store(self, items: list[Any]) -> tuple[str, list[str]]:
        return ("store", items[0] if isinstance(items[0], list) else [str(items[0])])

    def function_arg(self, items: list[Any]) -> str:
        """Transform a single function argument."""
        return str(items[0]) if items else ""

    def function_args(self, items: list[Any]) -> str:
        """Transform function arguments to comma-separated string."""
        if not items:
            return ""
        # Join all arguments with commas
        return ",".join(str(item) for item in items)

    def function_call(self, items: list[Any]) -> str:
        """Transform function call pattern like hdr(X-User-ID)."""
        func_name = str(items[0])
        args = str(items[1]) if len(items) > 1 else ""
        return f"{func_name}({args})"

    def pattern(self, items: list[Any]) -> str:
        """Extract pattern value (string or identifier)."""
        return str(items[0]) if items else ""

    def stick_rule(self, items: list[Any]) -> StickRule:
        """Transform stick rule (stick on/match/store)."""
        rule_type_item = items[0]
        pattern_value = items[1] if len(items) > 1 else ""
        condition = None

        # Extract condition if present (from if_condition)
        if len(items) > 2:
            condition_item = items[2]
            if isinstance(condition_item, tuple) and condition_item[0] == "condition":
                condition = condition_item[1]
            else:
                condition = str(condition_item)

        # Determine rule type
        if isinstance(rule_type_item, tuple):
            rule_type = rule_type_item[0]
        else:
            rule_type = "on"  # default

        return StickRule(
            rule_type=rule_type,
            pattern=pattern_value,
            table=None,  # Can be enhanced to parse table reference
            condition=condition,
        )

    def stick_on(self, items: list[Any]) -> tuple[str, str]:
        return ("on", "")

    def stick_match(self, items: list[Any]) -> tuple[str, str]:
        return ("match", "")

    def stick_store_request(self, items: list[Any]) -> tuple[str, str]:
        return ("store-request", "")

    def stick_store_response(self, items: list[Any]) -> tuple[str, str]:
        return ("store-response", "")

    # ===== TCP Request/Response Rules =====
    def tcp_request_block(self, items: list[Any]) -> list[TcpRequestRule]:
        """Transform tcp-request block."""
        return items

    def tcp_request_type(self, items: list[Token]) -> str:
        """Extract tcp-request type from grammar alternatives."""
        if items:
            # Items contains a Token, extract its value
            value = str(items[0])
            # Remove any quotes and return lowercase
            return value.strip('"').lower()
        return "connection"

    def tcp_request_rule(self, items: list[Any]) -> TcpRequestRule:
        """Transform individual tcp-request rule."""
        rule_type = items[0]
        action = str(items[1]) if len(items) > 1 else ""
        condition = None
        parameters: dict[str, Any] = {}

        # Parse remaining items for parameters and condition
        for item in items[2:]:
            if isinstance(item, tuple):
                # Check if this is an if_condition tuple
                if item[0] == "condition":
                    condition = item[1]
            elif isinstance(item, str):
                # This is a tcp_action_param (duration or value)
                # Store it in parameters with a generic key
                if "params" not in parameters:
                    parameters["params"] = []
                parameters["params"].append(item)

        return TcpRequestRule(
            rule_type=rule_type,
            action=action,
            condition=condition,
            parameters=parameters,
        )

    def tcp_action_param(self, items: list[Any]) -> str:
        """Transform tcp action parameter (duration or value)."""
        return str(items[0]) if items else ""

    def tcp_response_block(self, items: list[Any]) -> list[TcpResponseRule]:
        """Transform tcp-response block."""
        return items

    def tcp_response_type(self, items: list[Token]) -> str:
        """Extract tcp-response type from grammar alternatives."""
        return str(items[0]) if items else "content"

    def tcp_response_rule(self, items: list[Any]) -> TcpResponseRule:
        """Transform individual tcp-response rule."""
        rule_type = items[0]
        action = str(items[1]) if len(items) > 1 else ""
        condition = None
        parameters: dict[str, Any] = {}

        for item in items[2:]:
            if isinstance(item, tuple):
                # Check if this is an if_condition tuple
                if item[0] == "condition":
                    condition = item[1]
            elif isinstance(item, str):
                # This is a tcp_action_param (duration or value)
                if "params" not in parameters:
                    parameters["params"] = []
                parameters["params"].append(item)

        return TcpResponseRule(
            rule_type=rule_type,
            action=action,
            condition=condition,
            parameters=parameters,
        )

    def tcp_rule_param(self, items: list[Any]) -> tuple[str, Any]:
        """Transform tcp rule parameter."""
        return (str(items[0]), items[1])

    def tcp_rule_value(self, items: list[Any]) -> Any:
        """Transform tcp rule value."""
        return items[0]

    # ===== QUIC Initial Rules =====
    def quic_initial_block(self, items: list[Any]) -> list[QuicInitialRule]:
        """Transform quic_initial block (list of rules)."""
        return items

    def quic_initial_rule(self, items: list[Any]) -> QuicInitialRule:
        """Transform individual quic_initial rule object."""
        action = ""
        condition = None
        parameters: dict[str, Any] = {}

        # Process all property tuples
        for item in items:
            if isinstance(item, tuple):
                prop_name, prop_value = item
                if prop_name == "action":
                    action = str(prop_value)
                elif prop_name == "condition":
                    condition = str(prop_value)
                elif prop_name == "track_key":
                    parameters["track_key"] = str(prop_value)
                elif prop_name == "var_name":
                    parameters["var_name"] = str(prop_value)
                elif prop_name == "var_value":
                    parameters["var_value"] = str(prop_value)

        return QuicInitialRule(
            action=action,
            condition=condition,
            parameters=parameters,
        )

    def quic_rule_action(self, items: list[Any]) -> tuple[str, str]:
        """Extract action property."""
        return ("action", str(items[0]) if items else "")

    def quic_rule_condition(self, items: list[Any]) -> tuple[str, str]:
        """Extract condition property."""
        return ("condition", str(items[0]) if items else "")

    def quic_rule_track_key(self, items: list[Any]) -> tuple[str, str]:
        """Extract track_key property."""
        return ("track_key", str(items[0]) if items else "")

    def quic_rule_var_name(self, items: list[Any]) -> tuple[str, str]:
        """Extract var_name property."""
        return ("var_name", str(items[0]) if items else "")

    def quic_rule_var_value(self, items: list[Any]) -> tuple[str, str]:
        """Extract var_value property."""
        return ("var_value", str(items[0]) if items else "")

    def defaults_quic_initial(self, items: list[Any]) -> list[QuicInitialRule]:
        """Transform quic_initial in defaults."""
        return items[0] if items else []

    def frontend_quic_initial(self, items: list[Any]) -> list[QuicInitialRule]:
        """Transform quic_initial in frontend."""
        return items[0] if items else []

    def listen_quic_initial(self, items: list[Any]) -> list[QuicInitialRule]:
        """Transform quic_initial in listen."""
        return items[0] if items else []

    # ===== Backend ACL Support =====
    def backend_acl(self, items: list[Any]) -> ACL:
        """Transform ACL in backend."""
        return cast("ACL", items[0])

    def backend_tcp_request(self, items: list[Any]) -> list[TcpRequestRule]:
        """Transform tcp-request in backend."""
        return items[0] if items else []

    def backend_tcp_response(self, items: list[Any]) -> list[TcpResponseRule]:
        """Transform tcp-response in backend."""
        return items[0] if items else []

    def backend_stick_table(self, items: list[Any]) -> StickTable:
        """Transform stick-table in backend."""
        return cast("StickTable", items[0]) if items else cast("StickTable", None)

    def backend_stick_rule(self, items: list[Any]) -> StickRule:
        """Transform stick rule in backend."""
        return cast("StickRule", items[0]) if items else cast("StickRule", None)
