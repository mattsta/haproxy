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
    DefaultsConfig,
    DefaultServer,
    ErrorFile,
    ForLoop,
    Frontend,
    GlobalConfig,
    HealthCheck,
    HttpCheckRule,
    HttpRequestRule,
    HttpResponseRule,
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
        master_worker = None
        mworker_max_reloads = None
        node = None
        description = None
        hard_stop_after = None
        external_check = None

        # Connection limits
        maxconn = 2000
        maxconnrate = None
        maxsslrate = None
        maxsessrate = None
        maxpipes = None

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

        # HTTP Client Configuration (Phase 4B Part 1)
        httpclient_resolvers_disabled = None
        httpclient_resolvers_id = None
        httpclient_resolvers_prefer = None
        httpclient_retries = None
        httpclient_ssl_verify = None
        httpclient_ssl_ca_file = None

        # Platform-Specific Options (Phase 4B Part 1)
        noepoll = None
        nokqueue = None
        nopoll = None
        nosplice = None
        nogetaddrinfo = None
        noreuseport = None
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
                elif key == "setenv":
                    env_vars[value[0]] = value[1]
                elif key == "presetenv":
                    env_vars[value[0]] = value[1]
                elif key == "resetenv":
                    reset_env_vars.append(value)
                elif key == "unsetenv":
                    unset_env_vars.append(value)
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
                            else:
                                # tune_quic_retry_threshold → tune.quic.retry-threshold
                                # tune_quic_max_frame_loss → tune.quic.max-frame-loss
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
            master_worker=master_worker,
            mworker_max_reloads=mworker_max_reloads,
            node=node,
            description=description,
            hard_stop_after=hard_stop_after,
            external_check=external_check,
            # Connection limits
            maxconn=maxconn,
            maxconnrate=maxconnrate,
            maxsslrate=maxsslrate,
            maxsessrate=maxsessrate,
            maxpipes=maxpipes,
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
            # HTTP Client Configuration (Phase 4B Part 1)
            httpclient_resolvers_disabled=httpclient_resolvers_disabled,
            httpclient_resolvers_id=httpclient_resolvers_id,
            httpclient_resolvers_prefer=httpclient_resolvers_prefer,
            httpclient_retries=httpclient_retries,
            httpclient_ssl_verify=httpclient_ssl_verify,
            httpclient_ssl_ca_file=httpclient_ssl_ca_file,
            # Platform-Specific Options (Phase 4B Part 1)
            noepoll=noepoll,
            nokqueue=nokqueue,
            nopoll=nopoll,
            nosplice=nosplice,
            nogetaddrinfo=nogetaddrinfo,
            noreuseport=noreuseport,
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

    def global_maxsslconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxsslconn", items[0])

    def global_ulimit_n(self, items: list[Any]) -> tuple[str, int]:
        return ("ulimit_n", items[0])

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

    # Phase 2 - HTTP/2 tuning directives
    def global_tune_h2_be_glitches_threshold(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_be_glitches_threshold", items[0])

    def global_tune_h2_be_initial_window_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_be_initial_window_size", items[0])

    def global_tune_h2_be_max_concurrent_streams(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_be_max_concurrent_streams", items[0])

    def global_tune_h2_fe_glitches_threshold(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_glitches_threshold", items[0])

    def global_tune_h2_fe_initial_window_size(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_initial_window_size", items[0])

    def global_tune_h2_fe_max_concurrent_streams(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_max_concurrent_streams", items[0])

    def global_tune_h2_fe_max_total_streams(self, items: list[Any]) -> tuple[str, int]:
        return ("tune_h2_fe_max_total_streams", items[0])

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
        enable = True
        uri = "/stats"
        auth = None

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "enable":
                    enable = value
                elif key == "uri":
                    uri = value
                elif key == "auth":
                    auth = value

        return StatsConfig(enable=enable, uri=uri, auth=auth)

    def stats_enable(self, items: list[Any]) -> tuple[str, bool]:
        return ("enable", items[0])

    def stats_uri(self, items: list[Any]) -> tuple[str, str]:
        return ("uri", items[0])

    def stats_auth(self, items: list[Any]) -> tuple[str, str]:
        return ("auth", items[0])

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
                elif key == "errorloc":
                    code, url = value
                    errorloc[code] = url
                elif key == "errorloc302":
                    code, url = value
                    errorloc302[code] = url
                elif key == "errorloc303":
                    code, url = value
                    errorloc303[code] = url
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
        )

    def defaults_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

    def defaults_retries(self, items: list[Any]) -> tuple[str, int]:
        return ("retries", items[0])

    def defaults_log(self, items: list[Any]) -> tuple[str, str]:
        return ("log", items[0])

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
        binds = []
        acls = []
        http_request_rules = []
        http_response_rules = []
        tcp_request_rules = []
        tcp_response_rules = []
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
        log = []
        log_tag = None
        log_format = None
        stats_config = None
        capture_request_headers = []
        capture_response_headers = []
        redirect_rules = []
        error_files = []

        for prop in properties:
            if isinstance(prop, Bind):
                binds.append(prop)
            elif isinstance(prop, ACL):
                acls.append(prop)
            elif isinstance(prop, RedirectRule):
                redirect_rules.append(prop)
            elif isinstance(prop, ErrorFile):
                error_files.append(prop)
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
            elif isinstance(prop, TcpRequestRule):
                tcp_request_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, TcpRequestRule) for x in prop):
                tcp_request_rules.extend(prop)
            elif isinstance(prop, TcpResponseRule):
                tcp_response_rules.append(prop)
            elif isinstance(prop, list) and all(isinstance(x, TcpResponseRule) for x in prop):
                tcp_response_rules.extend(prop)
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
                elif key == "log":
                    log.append(value)
                elif key == "log_tag":
                    log_tag = value
                elif key == "log_format":
                    log_format = value
                elif key == "capture_request_header":
                    capture_request_headers.append(value)
                elif key == "capture_response_header":
                    capture_response_headers.append(value)

        return Frontend(
            name=name,
            mode=mode,
            binds=binds,
            acls=acls,
            http_request_rules=http_request_rules,
            http_response_rules=http_response_rules,
            tcp_request_rules=tcp_request_rules,
            tcp_response_rules=tcp_response_rules,
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
            log=log,
            log_tag=log_tag,
            log_format=log_format,
            stats_config=stats_config,
            capture_request_headers=capture_request_headers,
            capture_response_headers=capture_response_headers,
            redirect_rules=redirect_rules,
            error_files=error_files,
        )

    def frontend_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

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

    def frontend_log(self, items: list[Any]) -> tuple[str, str]:
        """Transform log directive."""
        return ("log", str(items[0]))

    def frontend_log_tag(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-tag directive."""
        return ("log_tag", str(items[0]))

    def frontend_log_format(self, items: list[Any]) -> tuple[str, str]:
        return ("log_format", items[0])

    def frontend_stats(self, items: list[Any]) -> StatsConfig:
        """Transform stats block."""
        return cast(StatsConfig, items[0])

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

    def stats_enable(self, items: list[Any]) -> tuple[str, bool]:
        """Transform stats enable."""
        return ("enable", True)

    def stats_uri(self, items: list[Any]) -> tuple[str, str]:
        """Transform stats uri."""
        return ("uri", str(items[0]))

    def stats_realm(self, items: list[Any]) -> tuple[str, str]:
        """Transform stats realm."""
        return ("realm", str(items[0]))

    def stats_auth(self, items: list[Any]) -> tuple[str, str]:
        """Transform stats auth."""
        return ("auth", str(items[0]))

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

    def errorfile_directive(self, items: list[Any]) -> ErrorFile:
        """Transform errorfile directive."""
        code = int(items[0])
        file = str(items[1])
        return ErrorFile(code=code, file=file)

    # ===== HTTP Reuse =====
    def http_reuse_mode(self, items: list[Token]) -> str:
        """Extract http-reuse mode string from grammar alternatives."""
        return str(items[0]) if items else "safe"

    def backend_http_reuse(self, items: list[Any]) -> tuple[str, str]:
        return ("http_reuse", items[0])

    def backend_source(self, items: list[Any]) -> tuple[str, str]:
        return ("source", str(items[0]))

    def backend_hash_type(self, items: list[Any]) -> tuple[str, str]:
        """Transform hash-type directive."""
        hash_spec = items[0]  # Result from hash_type_spec
        return ("hash_type", hash_spec)

    def backend_hash_balance_factor(self, items: list[Any]) -> tuple[str, int]:
        """Transform hash-balance-factor directive."""
        return ("hash_balance_factor", int(items[0]))

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
        return items[0]  # http_check_block already returns a list

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
        headers = {}

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
        opts = {"ssl": False, "sni": None, "alpn": None}
        if not items:
            return opts

        # Items will be tokens from the inlined rule: may contain sni and alpn strings
        for i, item in enumerate(items):
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

    # ===== tcp-check Block =====
    def backend_tcp_check(self, items: list[Any]) -> list[TcpCheckRule]:
        """Backend tcp-check block returns list of rules."""
        return items[0]  # tcp_check_block already returns a list

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
        balance = BalanceAlgorithm.ROUNDROBIN
        servers = []
        server_templates = []
        server_loops = []  # Collect for loops
        default_server = None
        health_check = None
        acls = []
        options = []
        http_request_rules = []
        http_response_rules = []
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
        log = []
        log_tag = None
        log_format = None
        redirect_rules = []
        error_files = []
        http_reuse = None
        http_check_rules = []
        tcp_check_rules = []
        use_server_rules = []
        source = None
        hash_type = None
        hash_balance_factor = None

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
            elif isinstance(prop, tuple):
                key, value = prop
                if key == "mode":
                    mode = Mode(value)
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
                elif key == "log":
                    log.append(value)
                elif key == "log_tag":
                    log_tag = value
                elif key == "log_format":
                    log_format = value
                elif key == "http_reuse":
                    http_reuse = value
                elif key == "source":
                    source = value
                elif key == "hash_type":
                    hash_type = value
                elif key == "hash_balance_factor":
                    hash_balance_factor = value

        # Build metadata with server loops if any
        metadata = {}
        if server_loops:
            metadata["server_loops"] = server_loops

        return Backend(
            name=name,
            mode=mode,
            balance=balance,
            servers=servers,
            server_templates=server_templates,
            default_server=default_server,
            health_check=health_check,
            acls=acls,
            options=options,
            http_request_rules=http_request_rules,
            http_response_rules=http_response_rules,
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
            log=log,
            log_tag=log_tag,
            log_format=log_format,
            redirect_rules=redirect_rules,
            error_files=error_files,
            http_reuse=http_reuse,
            http_check_rules=http_check_rules,
            tcp_check_rules=tcp_check_rules,
            use_server_rules=use_server_rules,
            source=source,
            hash_type=hash_type,
            hash_balance_factor=hash_balance_factor,
            metadata=metadata,
        )

    def backend_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

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

    def backend_log(self, items: list[Any]) -> tuple[str, str]:
        """Transform log directive."""
        return ("log", str(items[0]))

    def backend_log_tag(self, items: list[Any]) -> tuple[str, str]:
        """Transform log-tag directive."""
        return ("log_tag", str(items[0]))

    def backend_log_format(self, items: list[Any]) -> tuple[str, str]:
        return ("log_format", items[0])

    def backend_default_server(self, items: list[Any]) -> DefaultServer:
        """Handle default-server in backend."""
        return cast(DefaultServer, items[0])

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
        balance = BalanceAlgorithm.ROUNDROBIN
        servers = []
        server_loops = []
        acls = []
        options = []
        timeout_client = None
        timeout_server = None
        timeout_connect = None
        maxconn = None
        health_check = None

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
            elif isinstance(prop, Server):
                servers.append(prop)
            elif isinstance(prop, ForLoop):
                server_loops.append(prop)
            elif isinstance(prop, HealthCheck):
                health_check = prop
            elif isinstance(prop, tuple):
                key, value = prop
                if key == "mode":
                    mode = Mode(value)
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
            binds=binds,
            mode=mode,
            balance=balance,
            servers=servers,
            acls=acls,
            options=options,
            metadata=metadata,
        )

    def listen_mode(self, items: list[Any]) -> tuple[str, str]:
        return ("mode", items[0])

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

        return resolve_env_variable(var_name, default)

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

    # ===== Backend ACL Support =====
    def backend_acl(self, items: list[Any]) -> ACL:
        """Transform ACL in backend."""
        return cast(ACL, items[0])

    def backend_tcp_request(self, items: list[Any]) -> list[TcpRequestRule]:
        """Transform tcp-request in backend."""
        return items[0] if items else []

    def backend_tcp_response(self, items: list[Any]) -> list[TcpResponseRule]:
        """Transform tcp-response in backend."""
        return items[0] if items else []

    def backend_stick_table(self, items: list[Any]) -> StickTable:
        """Transform stick-table in backend."""
        return cast(StickTable, items[0]) if items else cast(StickTable, None)

    def backend_stick_rule(self, items: list[Any]) -> StickRule:
        """Transform stick rule in backend."""
        return cast(StickRule, items[0]) if items else cast(StickRule, None)
