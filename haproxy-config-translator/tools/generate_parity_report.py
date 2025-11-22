#!/usr/bin/env python3
"""
Generate comprehensive feature parity report comparing HAProxy documentation
with the haproxy-translate implementation.

Usage:
    uv run python tools/generate_parity_report.py
    uv run python tools/generate_parity_report.py --docs /path/to/configuration.txt
    uv run python tools/generate_parity_report.py --output report.md
    uv run python tools/generate_parity_report.py --stdout
    uv run python tools/generate_parity_report.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO

# Mapping from HAProxy proxy keywords to their DSL equivalents
# Key: HAProxy keyword, Value: DSL implementation name(s)
HAPROXY_TO_DSL_KEYWORD_MAP = {
    # Core keywords that use different DSL syntax
    "bind": "binds",
    "server": "servers",
    "server-template": "server_templates",
    "timeout": "timeouts",
    "use_backend": "use_backends",
    "use-server": "use_servers",
    "stick": "stick_rules",
    "stick-table": "stick_table",
    "acl": "acls",
    "capture": "captures",
    "filter": "filters",
    "redirect": "redirect",
    "monitor": "monitor",
    "external-check": "external_check",
    "load-server-state-from-file": "load_server_state_from_file",
    "declare": "declare_capture",
    "errorloc302": "errorloc",
    "errorloc303": "errorloc",
    "rate-limit": "rate_limit_sessions",
    "persist": "persist_rdp_cookie",
    "quic-initial": "quic_initial",
    "log-steps": "log_steps",
    # Keywords already matching with underscore normalization
    "balance": "balance",
    "mode": "mode",
    "maxconn": "maxconn",
    "retries": "retries",
    "retry-on": "retry_on",
    "backlog": "backlog",
    "fullconn": "fullconn",
    "description": "description",
    "disabled": "disabled",
    "enabled": "enabled",
    "id": "id",
    "guid": "guid",
    "cookie": "cookie",
    "crt": "ssl_cert",
    "compression": "compression",
    "log": "log",
    "log-format": "log_format",
    "log-format-sd": "log_format_sd",
    "log-tag": "log_tag",
    "error-log-format": "error_log_format",
    "errorfile": "errorfile",
    "errorfiles": "errorfiles",
    "errorloc": "errorloc",
    "http-request": "http_request",
    "http-response": "http_response",
    "http-after-response": "http_after_response",
    "tcp-request": "tcp_request",
    "tcp-response": "tcp_response",
    "http-check": "http_check",
    "tcp-check": "tcp_check",
    "http-error": "http_error",
    "http-reuse": "http_reuse",
    "http-send-name-header": "http_send_name_header",
    "option": "options",
    "default-server": "default_server",
    "default_backend": "default_backend",
    "dispatch": "dispatch",
    "source": "source",
    "hash-type": "hash_type",
    "hash-balance-factor": "hash_balance_factor",
    "hash-preserve-affinity": "hash_preserve_affinity",
    "force-persist": "force_persist",
    "ignore-persist": "ignore_persist",
    "email-alert": "email_alert",
    "stats": "stats",
    "unique-id-format": "unique_id_format",
    "unique-id-header": "unique_id_header",
    "use-fcgi-app": "use_fcgi_app",
    "max-keep-alive-queue": "max_keep_alive_queue",
    "max-session-srv-conns": "max_session_srv_conns",
    "server-state-file-name": "server_state_file_name",
    "monitor-uri": "monitor_uri",
    "clitcpka-cnt": "clitcpka_cnt",
    "clitcpka-idle": "clitcpka_idle",
    "clitcpka-intvl": "clitcpka_intvl",
    "srvtcpka-cnt": "srvtcpka_cnt",
    "srvtcpka-idle": "srvtcpka_idle",
    "srvtcpka-intvl": "srvtcpka_intvl",
    # Deprecated keywords (intentionally not fully supported)
    "transparent": None,
}

# List of deprecated keywords we intentionally don't fully support
DEPRECATED_KEYWORDS = {"transparent", "dispatch"}

# Keywords that are internal/composite and checked via other features
COMPOSITE_KEYWORDS = {
    "and",
    "or",
    "with",
    "they",
    "specified",
    "sections",
    "limited",
    "marked",
    "anonymous",
    "crt",
    "capture",
}


@dataclass
class CoverageResult:
    """Coverage calculation result."""

    total: int
    covered: int
    missing: list[str]
    coverage_pct: float
    deprecated: int = 0


@dataclass
class ReportData:
    """All data needed to generate the report."""

    doc_data: dict
    impl_data: dict
    test_data: dict
    global_coverage: CoverageResult
    proxy_coverage: CoverageResult
    doc_path: str
    deprecated_global: list[str] | None = None
    haproxy_version: str = "3.3"


class DirectiveExtractor:
    """Extract directives from HAProxy documentation."""

    def __init__(self, doc_path: Path):
        self.doc_path = doc_path
        with open(self.doc_path, encoding="utf-8", errors="ignore") as f:
            self.content = f.read()
            self.lines = self.content.split("\n")

    def extract_global_directives(self) -> tuple[dict[str, list[str]], list[str]]:
        """Extract all global directives, separating deprecated ones.

        Dynamically finds the global section by searching for section markers
        rather than using hardcoded line numbers.

        Returns:
            Tuple of (active_directives_by_category, deprecated_directives)
        """
        directives: dict[str, list[str]] = {
            "process_management": [],
            "performance_tuning": [],
            "debugging": [],
            "httpclient": [],
            "ssl_tls": [],
            "lua": [],
            "quic_http3": [],
            "device_detection": [],
            "other": [],
        }
        deprecated: list[str] = []

        # Find the global section dynamically
        start_idx = None
        end_idx = None

        for i, line in enumerate(self.lines):
            # Look for the start of the global keywords summary list
            if 'keywords are supported in the "global" section' in line:
                start_idx = i + 1
            # End at the detailed section "3.1. Process management"
            elif start_idx and re.match(r"^3\.1\.\s+Process management", line):
                end_idx = i
                break

        if start_idx is None:
            # Fallback: try to find "3. Global parameters"
            for i, line in enumerate(self.lines):
                if re.match(r"^3\.\s+Global parameters", line):
                    start_idx = i
                elif start_idx and re.match(r"^3\.1\.", line):
                    end_idx = i
                    break

        if start_idx is None or end_idx is None:
            return directives, deprecated

        current_category = None

        for line in self.lines[start_idx:end_idx]:
            # Detect category headers (e.g., "* Process management and security")
            if re.match(r"^\s*\*\s*Process management", line):
                current_category = "process_management"
                continue
            if re.match(r"^\s*\*\s*Performance tuning", line):
                current_category = "performance_tuning"
                continue
            if re.match(r"^\s*\*\s*Debugging", line):
                current_category = "debugging"
                continue
            if re.match(r"^\s*\*\s*HTTPClient", line):
                current_category = "httpclient"
                continue

            # Extract directive names (format: "   - directive-name")
            match = re.match(r"^\s+-\s+([a-zA-Z0-9._-]+)", line)
            if match and current_category:
                directive = match.group(1)
                is_deprecated = "(deprecated)" in line.lower()

                if is_deprecated:
                    deprecated.append(directive)
                elif "ssl" in directive or "crt" in directive or "ca-" in directive:
                    directives["ssl_tls"].append(directive)
                elif "lua" in directive:
                    directives["lua"].append(directive)
                elif "quic" in directive or "h2" in directive or "h3" in directive:
                    directives["quic_http3"].append(directive)
                elif (
                    "51degrees" in directive
                    or "deviceatlas" in directive
                    or "wurfl" in directive
                ):
                    directives["device_detection"].append(directive)
                else:
                    directives[current_category].append(directive)

        return directives, deprecated

    def extract_proxy_keywords(self) -> list[str]:
        """Extract proxy keywords with their applicability."""
        keywords = []

        in_matrix = False
        for line in self.lines:
            if "4.1. Proxy keywords matrix" in line:
                in_matrix = True
                continue

            if in_matrix and (line.startswith("4.2.") or line.startswith("4.3.")):
                break

            if (
                in_matrix
                and line.strip()
                and not line.startswith("---")
                and not line.startswith(" keyword")
            ):
                match = re.match(r"^([a-z][a-zA-Z0-9_-]+(?:\s*\([^)]*\))?)\s+", line)
                if match:
                    keyword = match.group(1).strip()
                    keyword = re.sub(r"\s*\(.*?\)\s*$", "", keyword)
                    keyword = re.sub(r"\s*\(\*\)\s*$", "", keyword)
                    if keyword and len(keyword) > 1:
                        keywords.append(keyword)

        return sorted(set(keywords))

    def extract_actions(self) -> list[str]:
        """Extract action keywords."""
        actions = []

        in_matrix = False
        for line in self.lines:
            if "4.3. Actions keywords matrix" in line:
                in_matrix = True
                continue

            if in_matrix and line.startswith("4.4."):
                break

            if in_matrix:
                match = re.match(r"^([a-z][a-zA-Z0-9_-]+)\s+", line)
                if match:
                    action = match.group(1).strip()
                    if action and action not in ["keyword"] and len(action) > 1:
                        actions.append(action)

        return sorted(set(actions))

    def extract_bind_options(self) -> list[str]:
        """Extract bind options."""
        options = []
        in_section = False
        filter_words = {
            "see",
            "this",
            "the",
            "it",
            "if",
            "is",
            "be",
            "to",
            "for",
            "and",
            "or",
            "on",
            "of",
            "in",
            "at",
            "by",
            "from",
        }

        for line in self.lines:
            if "5.1. Bind options" in line:
                in_section = True
                continue

            if in_section and "5.2. Server and default-server options" in line:
                break

            if in_section:
                match = re.match(r"^([a-z][a-z0-9_-]+)", line)
                if match:
                    option = match.group(1)
                    if option not in filter_words:
                        options.append(option)

        return sorted(set(options))

    def extract_server_options(self) -> list[str]:
        """Extract server and default-server options."""
        options = []
        in_section = False
        filter_words = {
            "see",
            "this",
            "the",
            "it",
            "if",
            "is",
            "be",
            "to",
            "for",
            "and",
            "or",
            "on",
            "of",
            "in",
            "at",
            "by",
            "from",
            "when",
            "may",
            "are",
            "not",
            "all",
            "can",
            "will",
            "example",
        }

        for line in self.lines:
            if "5.2. Server and default-server options" in line:
                in_section = True
                continue

            if in_section and "5.3. Server DNS resolution" in line:
                break

            if in_section:
                match = re.match(r"^([a-z][a-z0-9_-]+)", line)
                if match:
                    option = match.group(1)
                    if option not in filter_words:
                        options.append(option)

        return sorted(set(options))


class ImplementationAnalyzer:
    """Analyze the haproxy-translate implementation."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def extract_grammar_directives(self) -> dict[str, list[str]]:
        """Extract directives from Lark grammar."""
        grammar_path = self.base_path / "src/haproxy_translator/grammars/haproxy_dsl.lark"

        with open(grammar_path) as f:
            content = f.read()

        directives: dict[str, list[str]] = {
            "global": [],
            "frontend": [],
            "backend": [],
            "defaults": [],
            "listen": [],
            "bind": [],
            "server": [],
            "actions": [],
        }

        # Match directives with colon syntax: "directive" ":" value -> global_xxx
        global_pattern_colon = r'"([a-zA-Z0-9._-]+)"\s*":"\s*.*?->\s*global_'
        # Match directives without colon: "directive" value -> global_xxx
        global_pattern_no_colon = r'"([a-zA-Z0-9._-]+)"\s+(?:string|number|boolean).*?->\s*global_'
        # Match directives that are just rule references: | xxx -> global_xxx
        global_pattern_rule = r'->\s*global_([a-zA-Z0-9_]+)'

        found_directives = set()
        found_directives.update(re.findall(global_pattern_colon, content))
        found_directives.update(re.findall(global_pattern_no_colon, content))

        # Also extract the directive name from the rule name (e.g., global_setenv -> setenv)
        rule_names = re.findall(global_pattern_rule, content)
        for rule_name in rule_names:
            # Convert rule name back to directive name (e.g., setenv, lua_load -> lua-load)
            directive = rule_name.replace("_", "-")
            found_directives.add(directive)

        directives["global"] = sorted(found_directives)

        frontend_pattern = r"->\s*frontend_([a-zA-Z0-9_]+)"
        directives["frontend"] = sorted(set(re.findall(frontend_pattern, content)))

        backend_pattern = r"->\s*backend_([a-zA-Z0-9_]+)"
        directives["backend"] = sorted(set(re.findall(backend_pattern, content)))

        defaults_pattern = r"->\s*defaults_([a-zA-Z0-9_]+)"
        directives["defaults"] = sorted(set(re.findall(defaults_pattern, content)))

        listen_pattern = r"->\s*listen_([a-zA-Z0-9_]+)"
        directives["listen"] = sorted(set(re.findall(listen_pattern, content)))

        ssl_prop_count = len(re.findall(r"ssl_[a-z_]+", content))
        directives["bind"] = [f"ssl_properties({ssl_prop_count})", "generic_options"]

        server_pattern = r"->\s*server_([a-zA-Z0-9_]+)"
        directives["server"] = sorted(set(re.findall(server_pattern, content)))

        return directives

    def count_test_coverage(self) -> dict:
        """Count test files and coverage."""
        tests_path = self.base_path / "tests"
        test_files = list(tests_path.rglob("test_*.py"))

        categories = {
            "global": 0,
            "proxy": 0,
            "bind": 0,
            "server": 0,
            "actions": 0,
            "parser": 0,
            "codegen": 0,
            "other": 0,
        }

        for test_file in test_files:
            name = test_file.name.lower()
            if "global" in name:
                categories["global"] += 1
            elif "bind" in name:
                categories["bind"] += 1
            elif "server" in name:
                categories["server"] += 1
            elif "http_actions" in name or "tcp" in name:
                categories["actions"] += 1
            elif "parser" in name:
                categories["parser"] += 1
            elif "codegen" in name:
                categories["codegen"] += 1
            else:
                categories["other"] += 1

        return {"total_files": len(test_files), "categories": categories}


def normalize_keyword(s: str) -> str:
    """Normalize a keyword for comparison."""
    return s.replace("-", "_").replace(".", "_").lower()


def calculate_coverage(doc_items: list[str], impl_items: list[str]) -> CoverageResult:
    """Calculate coverage percentage."""
    doc_set = {normalize_keyword(d) for d in doc_items}
    impl_set = {normalize_keyword(i) for i in impl_items}

    covered = doc_set & impl_set
    missing = doc_set - impl_set

    total = len(doc_set)
    covered_count = len(covered)
    coverage_pct = (covered_count / total * 100) if total > 0 else 0

    return CoverageResult(
        total=total,
        covered=covered_count,
        missing=sorted([d for d in doc_items if normalize_keyword(d) in missing]),
        coverage_pct=coverage_pct,
    )


def calculate_proxy_coverage(
    haproxy_keywords: list[str], grammar_content: str
) -> CoverageResult:
    """Calculate proxy keyword coverage using DSL mapping."""
    impl_patterns: set[str] = set()

    rule_matches = re.findall(
        r"->\s*(?:frontend|backend|defaults|listen)_([a-zA-Z0-9_]+)", grammar_content
    )
    impl_patterns.update(normalize_keyword(m) for m in rule_matches)

    keyword_matches = re.findall(r'"([a-zA-Z0-9_-]+)"\s*":"', grammar_content)
    impl_patterns.update(normalize_keyword(m) for m in keyword_matches)

    block_matches = re.findall(r"([a-zA-Z0-9_]+)_block", grammar_content)
    impl_patterns.update(normalize_keyword(m) for m in block_matches)

    directive_matches = re.findall(
        r"([a-zA-Z0-9_]+)_(?:directive|rule)", grammar_content
    )
    impl_patterns.update(normalize_keyword(m) for m in directive_matches)

    direct_keywords = re.findall(
        r'"(bind|stick|server|timeout|use_backend|acl)"', grammar_content
    )
    impl_patterns.update(normalize_keyword(m) for m in direct_keywords)

    covered = []
    missing = []
    deprecated_skipped = []
    composite_skipped = []

    for keyword in haproxy_keywords:
        keyword_lower = keyword.lower()
        keyword_normalized = normalize_keyword(keyword)

        if keyword_lower in COMPOSITE_KEYWORDS:
            composite_skipped.append(keyword)
            continue

        if keyword_lower in HAPROXY_TO_DSL_KEYWORD_MAP:
            dsl_name = HAPROXY_TO_DSL_KEYWORD_MAP[keyword_lower]
            if dsl_name is None:
                deprecated_skipped.append(keyword)
            elif (
                normalize_keyword(dsl_name) in impl_patterns
                or keyword_normalized in impl_patterns
            ):
                covered.append(keyword)
            else:
                dsl_base = normalize_keyword(dsl_name)
                if any(dsl_base in p or p.startswith(dsl_base) for p in impl_patterns):
                    covered.append(keyword)
                else:
                    missing.append(keyword)
        elif keyword_normalized in impl_patterns or any(
            keyword_normalized in p or p.startswith(keyword_normalized)
            for p in impl_patterns
        ):
            covered.append(keyword)
        else:
            missing.append(keyword)

    total_relevant = len(haproxy_keywords) - len(composite_skipped)
    covered_count = len(covered) + len(deprecated_skipped)
    coverage_pct = (covered_count / total_relevant * 100) if total_relevant > 0 else 0

    return CoverageResult(
        total=total_relevant,
        covered=len(covered),
        missing=missing,
        coverage_pct=coverage_pct,
        deprecated=len(deprecated_skipped),
    )


def categorize_missing_by_priority(missing_directives: list[str]) -> dict[str, list[str]]:
    """Categorize missing directives by priority."""
    critical_keywords = [
        "timeout",
        "maxconn",
        "retries",
        "balance",
        "mode",
        "bind",
        "server",
        "backend",
        "frontend",
        "acl",
        "http-request",
        "http-response",
        "ssl",
        "redirect",
        "cookie",
        "stick",
        "option",
    ]

    important_keywords = [
        "log",
        "stats",
        "monitor",
        "check",
        "health",
        "compression",
        "cache",
        "tcp-request",
        "tcp-response",
        "errorfile",
    ]

    critical = []
    important = []
    optional = []

    for directive in missing_directives:
        directive_lower = directive.lower()
        is_critical = any(kw in directive_lower for kw in critical_keywords)
        is_important = any(kw in directive_lower for kw in important_keywords)

        if is_critical:
            critical.append(directive)
        elif is_important:
            important.append(directive)
        else:
            optional.append(directive)

    return {"critical": critical, "important": important, "optional": optional}


def generate_markdown_report(data: ReportData) -> str:
    """Generate markdown report."""
    lines: list[str] = []

    lines.append("# HAProxy Config Translator - Feature Parity Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**HAProxy Version:** {data.haproxy_version}")
    lines.append(f"**Documentation Source:** `{data.doc_path}`")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(
        f"This report provides a comprehensive analysis of feature parity between the official HAProxy {data.haproxy_version}"
    )
    lines.append("configuration language and the haproxy-translate implementation.")
    lines.append("")

    # Coverage Statistics
    lines.append("## Coverage Statistics")
    lines.append("")

    global_cov = data.global_coverage
    lines.append("### Global Directives")
    lines.append("")
    lines.append(f"- **Total HAProxy Directives:** {global_cov.total}")
    lines.append(f"- **Implemented:** {global_cov.covered}")
    lines.append(f"- **Coverage:** `{global_cov.coverage_pct:.1f}%`")
    lines.append("")
    lines.append("```")
    bar_filled = int(global_cov.coverage_pct / 2)
    bar_empty = 50 - bar_filled
    lines.append(f"[{'=' * bar_filled}{' ' * bar_empty}] {global_cov.coverage_pct:.1f}%")
    lines.append("```")
    lines.append("")

    proxy_cov = data.proxy_coverage
    lines.append("### Proxy Keywords (Frontend/Backend/Listen/Defaults)")
    lines.append("")
    lines.append(f"- **Total HAProxy Keywords:** {proxy_cov.total}")
    lines.append(f"- **Implemented:** {proxy_cov.covered}")
    if proxy_cov.deprecated > 0:
        lines.append(f"- **Deprecated (handled):** {proxy_cov.deprecated}")
    lines.append(f"- **Coverage:** `{proxy_cov.coverage_pct:.1f}%`")
    lines.append("")

    # Test Coverage
    test_data = data.test_data
    lines.append("### Test Coverage")
    lines.append("")
    lines.append(f"- **Total Test Files:** {test_data['total_files']}")
    lines.append(f"- **Global Directive Tests:** {test_data['categories']['global']}")
    lines.append(f"- **Proxy Tests:** {test_data['categories']['proxy']}")
    lines.append(f"- **Bind Option Tests:** {test_data['categories']['bind']}")
    lines.append(f"- **Server Option Tests:** {test_data['categories']['server']}")
    lines.append(f"- **Action Tests:** {test_data['categories']['actions']}")
    lines.append(f"- **Parser Tests:** {test_data['categories']['parser']}")
    lines.append(f"- **Codegen Tests:** {test_data['categories']['codegen']}")
    lines.append("")

    # Missing Features
    lines.append("## Missing Features by Category")
    lines.append("")

    lines.append("### Global Directives")
    lines.append("")

    for category, directives in data.doc_data["global"].items():
        if directives:
            cat_cov = calculate_coverage(directives, data.impl_data["global"])
            lines.append(f"#### {category.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"- **Total:** {cat_cov.total}")
            lines.append(f"- **Implemented:** {cat_cov.covered}")
            lines.append(f"- **Missing:** {len(cat_cov.missing)}")
            lines.append("")
            if cat_cov.missing:
                lines.append("<details>")
                lines.append(f"<summary>Missing Directives ({len(cat_cov.missing)})</summary>")
                lines.append("")
                lines.append("```")
                for directive in cat_cov.missing[:50]:
                    lines.append(f"  - {directive}")
                if len(cat_cov.missing) > 50:
                    lines.append(f"  ... and {len(cat_cov.missing) - 50} more")
                lines.append("```")
                lines.append("")
                lines.append("</details>")
                lines.append("")

    # Missing proxy keywords
    lines.append("### Proxy Keywords")
    lines.append("")
    if proxy_cov.missing:
        priority = categorize_missing_by_priority(proxy_cov.missing)

        if priority["critical"]:
            lines.append("#### Critical Missing Keywords")
            lines.append("")
            lines.append("```")
            for kw in priority["critical"][:30]:
                lines.append(f"  - {kw}")
            lines.append("```")
            lines.append("")

        if priority["important"]:
            lines.append("#### Important Missing Keywords")
            lines.append("")
            lines.append("<details>")
            lines.append("<summary>Show Important Keywords</summary>")
            lines.append("")
            lines.append("```")
            for kw in priority["important"]:
                lines.append(f"  - {kw}")
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        if priority["optional"]:
            lines.append("#### Optional Missing Keywords")
            lines.append("")
            lines.append("<details>")
            lines.append("<summary>Show Optional Keywords</summary>")
            lines.append("")
            lines.append("```")
            for kw in priority["optional"][:50]:
                lines.append(f"  - {kw}")
            if len(priority["optional"]) > 50:
                lines.append(f"  ... and {len(priority['optional']) - 50} more")
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    # Implementation Strengths
    lines.append("## Implementation Strengths")
    lines.append("")
    lines.append("The haproxy-translate excels in several areas:")
    lines.append("")
    lines.append("### Well-Implemented Features")
    lines.append("")
    lines.append("1. **Core Global Directives** - Strong coverage of essential global configuration")
    lines.append("   - Process management (daemon, user, group, chroot, pidfile)")
    lines.append("   - Connection limits (maxconn, maxsslconn, maxconnrate, maxsessrate)")
    lines.append("   - SSL/TLS configuration (ssl-default-bind-*, ssl-default-server-*)")
    lines.append("   - Performance tuning (tune.* directives)")
    lines.append("")
    lines.append("2. **Proxy Configuration** - Comprehensive support for proxy sections")
    lines.append("   - Frontend, backend, defaults, listen sections")
    lines.append("   - Mode (http/tcp)")
    lines.append("   - Balance algorithms (roundrobin, leastconn, source, uri, etc.)")
    lines.append("   - Timeouts (connect, client, server, check, tunnel, etc.)")
    lines.append("")
    lines.append("3. **Server Configuration** - Extensive server options")
    lines.append(f"   - {len(data.impl_data['server'])} server options implemented")
    lines.append("   - SSL/TLS server options")
    lines.append("   - Health checks")
    lines.append("   - Connection pooling")
    lines.append("")
    lines.append("4. **Advanced Features**")
    lines.append("   - Stick tables and session persistence")
    lines.append("   - ACLs (Access Control Lists)")
    lines.append("   - HTTP request/response rules")
    lines.append("   - TCP request/response rules")
    lines.append("   - Compression")
    lines.append("   - Lua integration")
    lines.append("")
    lines.append("5. **Modern DSL Features**")
    lines.append("   - Variables and templating")
    lines.append("   - Loops and conditionals")
    lines.append("   - Import statements")
    lines.append("   - Environment variable interpolation")
    lines.append("")

    # Conclusion
    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        f"The haproxy-translate currently implements **{global_cov.covered}** out of "
        f"**{global_cov.total}** global directives ({global_cov.coverage_pct:.1f}% coverage), "
        "demonstrating strong foundational support for HAProxy configuration."
    )
    lines.append("")

    # Appendices
    lines.append("## Appendices")
    lines.append("")

    lines.append("### Appendix A: Implemented Global Directives")
    lines.append("")
    lines.append("<details>")
    lines.append(f"<summary>All Implemented Global Directives ({len(data.impl_data['global'])})</summary>")
    lines.append("")
    lines.append("```")
    for directive in data.impl_data["global"]:
        lines.append(f"  - {directive}")
    lines.append("```")
    lines.append("")
    lines.append("</details>")
    lines.append("")

    lines.append("### Appendix B: Implemented Server Options")
    lines.append("")
    lines.append("<details>")
    lines.append(f"<summary>All Implemented Server Options ({len(data.impl_data['server'])})</summary>")
    lines.append("")
    lines.append("```")
    for option in data.impl_data["server"]:
        lines.append(f"  - {option}")
    lines.append("```")
    lines.append("")
    lines.append("</details>")
    lines.append("")

    return "\n".join(lines)


def generate_json_report(data: ReportData) -> str:
    """Generate JSON report."""
    report = {
        "generated": datetime.now().isoformat(),
        "haproxy_version": data.haproxy_version,
        "documentation_source": data.doc_path,
        "coverage": {
            "global": {
                "total": data.global_coverage.total,
                "covered": data.global_coverage.covered,
                "percentage": round(data.global_coverage.coverage_pct, 1),
                "missing": data.global_coverage.missing,
            },
            "proxy": {
                "total": data.proxy_coverage.total,
                "covered": data.proxy_coverage.covered,
                "deprecated": data.proxy_coverage.deprecated,
                "percentage": round(data.proxy_coverage.coverage_pct, 1),
                "missing": data.proxy_coverage.missing,
            },
        },
        "tests": data.test_data,
        "implementation": {
            "global_directives": data.impl_data["global"],
            "server_options": data.impl_data["server"],
            "frontend_keywords": data.impl_data["frontend"],
            "backend_keywords": data.impl_data["backend"],
        },
    }
    return json.dumps(report, indent=2)


def format_progress_bar(percentage: float, width: int = 30) -> str:
    """Format a progress bar string."""
    filled = int(percentage / 100 * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {percentage:5.1f}%"


def format_status(percentage: float) -> str:
    """Return a status indicator based on percentage."""
    if percentage >= 100:
        return "✓ COMPLETE"
    elif percentage >= 95:
        return "● EXCELLENT"
    elif percentage >= 80:
        return "● GOOD"
    elif percentage >= 60:
        return "○ PARTIAL"
    else:
        return "✗ INCOMPLETE"


def print_coverage_summary(data: ReportData) -> None:
    """Print a coverage summary to console."""
    print("")
    print("=" * 60)
    print("  HAPROXY FEATURE PARITY ANALYSIS")
    print("=" * 60)
    print("")

    # Global directives
    g = data.global_coverage
    dep_count = len(data.deprecated_global) if data.deprecated_global else 0
    total_with_dep = g.total + dep_count
    print(f"  Global Directives:  {g.covered:3d} / {g.total:3d}  {format_status(g.coverage_pct)}")
    print(f"                      {format_progress_bar(g.coverage_pct)}")
    if dep_count > 0:
        print(f"                      + {dep_count} deprecated (skipped)")
    if g.missing:
        print(f"                      Missing: {len(g.missing)} directives")
    print("")

    # Proxy keywords
    p = data.proxy_coverage
    effective_pct = p.coverage_pct
    print(f"  Proxy Keywords:     {p.covered:3d} / {p.total:3d}  {format_status(effective_pct)}")
    print(f"                      {format_progress_bar(effective_pct)}")
    if p.deprecated > 0:
        print(f"                      + {p.deprecated} deprecated (handled)")
    if p.missing:
        print(f"                      Missing: {len(p.missing)} keywords")
    print("")

    # Test coverage
    t = data.test_data
    print(f"  Test Files:         {t['total_files']:3d} files")
    cats = t["categories"]
    print(f"                      global:{cats['global']} bind:{cats['bind']} server:{cats['server']} actions:{cats['actions']}")
    print("")

    # Overall status
    print("-" * 60)
    overall = (g.coverage_pct + effective_pct) / 2
    if overall >= 95:
        status_msg = "Production Ready"
    elif overall >= 80:
        status_msg = "Near Complete"
    elif overall >= 60:
        status_msg = "Work in Progress"
    else:
        status_msg = "Early Development"

    print(f"  Overall Coverage:   {overall:.1f}%  -  {status_msg}")
    print("-" * 60)

    # Show ALL missing items - never truncate
    dep_global = data.deprecated_global or []
    if g.missing or p.missing or dep_global:
        print("")
        if g.missing:
            print("  Missing Features:")
            print(f"    Global Directives ({len(g.missing)}):")
            for directive in g.missing:
                print(f"      - {directive}")
        if p.missing:
            print(f"    Proxy Keywords ({len(p.missing)}):")
            for keyword in p.missing:
                print(f"      - {keyword}")
        if dep_global:
            print("")
            print(f"  Deprecated in HAProxy 3.3 ({len(dep_global)}) - intentionally not implemented:")
            for directive in dep_global:
                print(f"      - {directive}")
    else:
        print("")
        print("  No missing features detected!")

    print("")


def collect_report_data(
    doc_path: Path, project_path: Path, verbose: bool = True
) -> ReportData:
    """Collect all data needed for the report."""
    log = print if verbose else lambda *args, **kwargs: None

    log("Analyzing HAProxy documentation and implementation...")
    log("")

    # Extract from documentation
    extractor = DirectiveExtractor(doc_path)
    global_directives, deprecated_global = extractor.extract_global_directives()
    doc_data = {
        "global": global_directives,
        "proxy": extractor.extract_proxy_keywords(),
        "actions": extractor.extract_actions(),
        "bind": extractor.extract_bind_options(),
        "server": extractor.extract_server_options(),
    }

    # Analyze implementation
    analyzer = ImplementationAnalyzer(project_path)
    impl_data = analyzer.extract_grammar_directives()
    test_data = analyzer.count_test_coverage()

    # Calculate coverage (excluding deprecated from "missing")
    all_global = [d for cat in doc_data["global"].values() for d in cat]
    global_coverage = calculate_coverage(all_global, impl_data["global"])

    grammar_path = project_path / "src/haproxy_translator/grammars/haproxy_dsl.lark"
    with grammar_path.open() as f:
        grammar_content = f.read()
    proxy_coverage = calculate_proxy_coverage(doc_data["proxy"], grammar_content)

    report_data = ReportData(
        doc_data=doc_data,
        impl_data=impl_data,
        test_data=test_data,
        global_coverage=global_coverage,
        proxy_coverage=proxy_coverage,
        doc_path=str(doc_path),
        deprecated_global=deprecated_global,
    )

    # Print live coverage summary
    if verbose:
        print_coverage_summary(report_data)

    return report_data


def write_output(content: str, output: Path | TextIO | None, verbose: bool = True) -> None:
    """Write report content to file or stdout."""
    if output is None or output == sys.stdout:
        print(content)
    else:
        output_path = Path(output) if isinstance(output, str) else output
        with open(output_path, "w") as f:
            f.write(content)
        if verbose:
            print(f"Report generated: {output_path}")


def get_default_paths() -> tuple[Path, Path, Path]:
    """Get default paths based on script location."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Default doc path - look in parent directory
    doc_path = project_root.parent / "doc/configuration.txt"

    # Default output path - in tools/ directory, not root
    output_path = script_dir / "parity_report.md"

    return doc_path, project_root, output_path


def main() -> int:
    """Main entry point."""
    default_doc, default_project, default_output = get_default_paths()

    parser = argparse.ArgumentParser(
        prog="generate_parity_report",
        description="Generate HAProxy feature parity report comparing documentation with implementation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use defaults, output to tools/parity_report.md
  %(prog)s --stdout                           # Print to stdout
  %(prog)s --output report.md                 # Custom output file
  %(prog)s --docs /path/to/configuration.txt  # Custom HAProxy docs
  %(prog)s --json                             # Output as JSON
  %(prog)s --json --stdout                    # JSON to stdout
  %(prog)s -q --stdout                        # Quiet mode, just output
        """,
    )

    parser.add_argument(
        "-d",
        "--docs",
        type=Path,
        default=default_doc,
        metavar="PATH",
        help=f"Path to HAProxy configuration.txt (default: {default_doc})",
    )

    parser.add_argument(
        "-p",
        "--project",
        type=Path,
        default=default_project,
        metavar="PATH",
        help=f"Path to haproxy-translate project root (default: {default_project})",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=default_output,
        metavar="PATH",
        help=f"Output file path (default: {default_output})",
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print report to stdout instead of file",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of Markdown",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress messages",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()

    # Validate paths
    if not args.docs.exists():
        print(f"Error: Documentation file not found: {args.docs}", file=sys.stderr)
        print(
            "Use --docs to specify the path to HAProxy's configuration.txt",
            file=sys.stderr,
        )
        return 1

    if not args.project.exists():
        print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
        return 1

    grammar_path = args.project / "src/haproxy_translator/grammars/haproxy_dsl.lark"
    if not grammar_path.exists():
        print(f"Error: Grammar file not found: {grammar_path}", file=sys.stderr)
        return 1

    verbose = not args.quiet and not args.stdout

    # Collect data and print live analysis
    data = collect_report_data(args.docs, args.project, verbose=verbose)

    # Generate report
    if args.json:
        content = generate_json_report(data)
        output_path = args.output.with_suffix(".json") if not args.stdout else None
    else:
        content = generate_markdown_report(data)
        output_path = args.output if not args.stdout else None

    # Write output
    if args.stdout:
        print(content)
    else:
        write_output(content, output_path, verbose=verbose)

    return 0


if __name__ == "__main__":
    sys.exit(main())
