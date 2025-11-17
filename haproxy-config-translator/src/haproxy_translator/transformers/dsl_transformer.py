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
    ForLoop,
    Frontend,
    GlobalConfig,
    HealthCheck,
    HttpRequestRule,
    HttpResponseRule,
    Listen,
    LogFacility,
    LogLevel,
    LogTarget,
    LuaScript,
    Mode,
    Server,
    ServerTemplate,
    StatsConfig,
    StickRule,
    StickTable,
    TcpRequestRule,
    TcpResponseRule,
    Template,
    UseBackendRule,
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
            variables=self.variables,
            templates=self.templates,
            imports=imports,
        )

    # ===== Global Section =====
    def global_section(self, items: list[Any]) -> GlobalConfig:
        """Transform global section."""
        daemon = True
        maxconn = 2000
        user = None
        group = None
        chroot = None
        pidfile = None
        log_targets = []
        lua_scripts = []
        stats = None

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "daemon":
                    daemon = value
                elif key == "maxconn":
                    maxconn = value
                elif key == "user":
                    user = value
                elif key == "group":
                    group = value
                elif key == "chroot":
                    chroot = value
                elif key == "pidfile":
                    pidfile = value
            elif isinstance(item, LogTarget):
                log_targets.append(item)
            elif isinstance(item, list) and all(isinstance(x, LuaScript) for x in item):
                lua_scripts.extend(item)
            elif isinstance(item, StatsConfig):
                stats = item

        return GlobalConfig(
            daemon=daemon,
            maxconn=maxconn,
            user=user,
            group=group,
            chroot=chroot,
            pidfile=pidfile,
            log_targets=log_targets,
            lua_scripts=lua_scripts,
            stats=stats,
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

        return DefaultsConfig(
            mode=mode,
            retries=retries,
            timeout_connect=timeout_connect,
            timeout_client=timeout_client,
            timeout_server=timeout_server,
            timeout_check=timeout_check,
            timeout_http_request=timeout_http_request,
            timeout_http_keep_alive=timeout_http_keep_alive,
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
        monitor_uri = None
        maxconn = None

        for prop in properties:
            if isinstance(prop, Bind):
                binds.append(prop)
            elif isinstance(prop, ACL):
                acls.append(prop)
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
                elif key == "monitor_uri":
                    monitor_uri = value
                elif key == "maxconn":
                    maxconn = value

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
            monitor_uri=monitor_uri,
            maxconn=maxconn,
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

    def frontend_monitor_uri(self, items: list[Any]) -> tuple[str, str]:
        return ("monitor_uri", str(items[0]))

    def frontend_maxconn(self, items: list[Any]) -> tuple[str, int]:
        return ("maxconn", items[0])

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

    def http_rule(self, items: list[Any]) -> HttpRequestRule:
        action = str(items[0])
        parameters = {}
        condition = None

        for item in items[1:]:
            if isinstance(item, tuple):
                if item[0] == "condition":
                    condition = item[1]
                else:
                    parameters[item[0]] = item[1]
            elif isinstance(item, str):
                # Positional value
                if "header" not in parameters:
                    parameters["header"] = item
                else:
                    parameters["value"] = item

        return HttpRequestRule(action=action, parameters=parameters, condition=condition)

    def action_expr(self, items: list[Any]) -> str:
        return cast("str", items[0])
        # Collect parameters

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
        retries = None

        for prop in properties:
            if isinstance(prop, Server):
                servers.append(prop)
            elif isinstance(prop, ForLoop):
                server_loops.append(prop)
            elif isinstance(prop, ACL):
                acls.append(prop)
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
                elif key == "retries":
                    retries = value

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
            retries=retries,
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

    def backend_timeout_server(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_server", str(items[0]))

    def backend_timeout_connect(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_connect", str(items[0]))

    def backend_timeout_check(self, items: list[Any]) -> tuple[str, str]:
        return ("timeout_check", str(items[0]))

    def backend_retries(self, items: list[Any]) -> tuple[str, int]:
        return ("retries", items[0])

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
        headers = {}

        for item in items:
            if isinstance(item, tuple):
                key, value = item
                if key == "method":
                    method = value
                elif key == "uri":
                    uri = value
                elif key == "expect_status":
                    expect_status = value
                elif key.startswith("header_"):
                    header_name = item[1]
                    header_value = item[2]
                    headers[header_name] = header_value

        return HealthCheck(method=method, uri=uri, expect_status=expect_status, headers=headers)

    def hc_method(self, items: list[Any]) -> tuple[str, str]:
        return ("method", items[0])

    def hc_uri(self, items: list[Any]) -> tuple[str, str]:
        return ("uri", items[0])

    def hc_expect(self, items: list[Any]) -> tuple[str, int]:
        return ("expect_status", items[0])

    def hc_header(self, items: list[Any]) -> tuple[str, str, str]:
        return ("header", items[0][0], items[0][1])

    def expect_value(self, items: list[Any]) -> int:
        return cast("int", items[0])

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
        template_spreads = []

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
        var_name = items[0]
        default = items[1] if len(items) > 1 else ""
        import os

        return os.environ.get(var_name, default)

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
        return str(items[0]) if items else "ip"

    def stick_table_type_prop(self, items: list[Any]) -> tuple[str, str]:
        return ("type", items[0])

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
        parameters = {}

        # Parse remaining items for condition (grammar only supports if_condition, no params)
        for item in items[2:]:
            if isinstance(item, tuple):
                # Check if this is an if_condition tuple
                if item[0] == "condition":
                    condition = item[1]

        return TcpRequestRule(
            rule_type=rule_type,
            action=action,
            condition=condition,
            parameters=parameters,
        )

    def if_condition(self, items: list[Any]) -> tuple[str, str]:
        """Transform if condition to a tuple marking it as a condition."""
        condition = str(items[0]) if items else ""
        return ("condition", condition)

    def condition_expr(self, items: list[Any]) -> str:
        """Extract condition expression (ACL name or expression)."""
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
        parameters = {}

        for item in items[2:]:
            if isinstance(item, tuple):
                # Check if this is an if_condition tuple
                if item[0] == "condition":
                    condition = item[1]
                else:
                    key, value = item
                    parameters[key] = value
            elif isinstance(item, str):
                condition = item

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
        return items[0] if items and isinstance(items[0], ACL) else items[0]

    def backend_tcp_request(self, items: list[Any]) -> list[TcpRequestRule]:
        """Transform tcp-request in backend."""
        return items[0] if items else []

    def backend_tcp_response(self, items: list[Any]) -> list[TcpResponseRule]:
        """Transform tcp-response in backend."""
        return items[0] if items else []

    def backend_stick_table(self, items: list[Any]) -> StickTable:
        """Transform stick-table in backend."""
        return items[0] if items else None

    def backend_stick_rule(self, items: list[Any]) -> StickRule:
        """Transform stick rule in backend."""
        return items[0] if items else None
