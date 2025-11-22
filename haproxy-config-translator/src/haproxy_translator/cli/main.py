"""Command-line interface for HAProxy configuration translator."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .. import __version__
from ..codegen.haproxy import HAProxyCodeGenerator
from ..lua.manager import LuaManager
from ..parsers import ParserRegistry
from ..utils.errors import TranslatorError

if TYPE_CHECKING:
    from ..validators.security import SecurityReport

console = Console()


@click.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "-f",
    "--format",
    type=str,
    help="Input format (dsl, yaml, hcl, auto). Default: auto-detect from extension",
)
@click.option("--validate", is_flag=True, help="Validate only, don't generate")
@click.option("--debug", is_flag=True, help="Show debug information")
@click.option("--watch", is_flag=True, help="Watch for changes and regenerate")
@click.option(
    "--lua-dir",
    type=click.Path(path_type=Path),
    help="Output directory for Lua scripts (default: same as output)",
)
@click.option("--list-formats", is_flag=True, help="List available input formats")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("--security-check", is_flag=True, help="Run security validation and show report")
@click.version_option(version=__version__, prog_name="haconf")
def cli(
    config_file: Path,
    output: Path | None,
    format: str | None,
    validate: bool,
    debug: bool,
    watch: bool,
    lua_dir: Path | None,
    list_formats: bool,
    verbose: bool,
    security_check: bool,
) -> None:
    """
    haconf - HAProxy Configuration Translator.

    Translate modern configuration formats (DSL, YAML, HCL) to native HAProxy format.

    \b
    Examples:
        haconf config.hap -o haproxy.cfg
        haconf config.yaml --format yaml --validate
        haconf config.hap -o haproxy.cfg --watch
    """
    if list_formats:
        _list_formats()
        return

    try:
        if watch:
            _watch_mode(config_file, output, format, lua_dir, verbose)
        else:
            _translate_once(
                config_file, output, format, validate, debug, lua_dir, verbose, security_check
            )

    except TranslatorError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if debug:
            console.print_exception()
        sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if debug:
            console.print_exception()
        sys.exit(1)


def _translate_once(
    config_file: Path,
    output: Path | None,
    format: str | None,
    validate: bool,
    debug: bool,
    lua_dir: Path | None,
    verbose: bool,
    security_check: bool = False,
) -> None:
    """Translate configuration once."""
    if verbose:
        console.print(f"[dim]Reading config from:[/dim] {config_file}")

    # Get parser
    try:
        if format:
            parser = ParserRegistry.get_parser(format_name=format)
        else:
            parser = ParserRegistry.get_parser(filepath=config_file)

        if verbose:
            console.print(f"[dim]Using parser:[/dim] {parser.format_name}")

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        _list_formats()
        sys.exit(1)

    # Parse configuration
    with console.status("[bold green]Parsing configuration...", spinner="dots"):
        ir = parser.parse_file(config_file)

    if verbose:
        console.print(
            f"[dim]Parsed successfully:[/dim] {len(ir.frontends)} frontends, "
            f"{len(ir.backends)} backends"
        )

    if debug:
        console.print("\n[bold]IR Debug Info:[/bold]")
        console.print(f"  Frontends: {[f.name for f in ir.frontends]}")
        console.print(f"  Backends: {[b.name for b in ir.backends]}")
        console.print(f"  Variables: {list(ir.variables.keys())}")
        console.print(f"  Templates: {list(ir.templates.keys())}")

    # Run security validation if requested
    if security_check:
        from ..validators.security import SecurityValidator

        with console.status("[bold green]Running security checks...", spinner="dots"):
            security_validator = SecurityValidator(ir)
            report = security_validator.validate()

        _display_security_report(report)

        if not report.passed:
            sys.exit(2)  # Exit with code 2 for security issues

    if validate:
        console.print("[bold green]✓[/bold green] Configuration is valid")
        return

    # Extract Lua scripts
    if lua_dir:
        lua_output_dir = lua_dir
    elif output:
        lua_output_dir = output.parent
    else:
        lua_output_dir = Path.cwd()

    lua_manager = LuaManager(lua_output_dir)

    with console.status("[bold green]Extracting Lua scripts...", spinner="dots"):
        ir = lua_manager.extract_lua_scripts(ir)

    if verbose and lua_manager.script_map:
        console.print("[dim]Extracted Lua scripts:[/dim]")
        for name, path in lua_manager.get_script_paths().items():
            console.print(f"  - {name}: {path}")

    # Generate HAProxy configuration
    with console.status("[bold green]Generating HAProxy config...", spinner="dots"):
        generator = HAProxyCodeGenerator()
        config = generator.generate(ir, output_path=output)

    # Output
    if output:
        console.print(f"[bold green]✓[/bold green] Configuration written to: [cyan]{output}[/cyan]")
        if lua_manager.script_map:
            console.print(
                f"[bold green]✓[/bold green] Lua scripts written to: [cyan]{lua_output_dir / 'lua'}[/cyan]"
            )
    else:
        # Print to stdout with syntax highlighting
        syntax = Syntax(config, "nginx", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="Generated HAProxy Configuration", border_style="green"))


def _watch_mode(
    config_file: Path,
    output: Path | None,
    format: str | None,
    lua_dir: Path | None,
    verbose: bool,
) -> None:
    """Watch for file changes and regenerate."""
    try:
        from watchdog.events import (
            DirModifiedEvent,
            FileModifiedEvent,
            FileSystemEventHandler,
        )
        from watchdog.observers import Observer
    except ImportError:
        console.print(
            "[bold red]Error:[/bold red] Watch mode requires 'watchdog' package. "
            "Install with: pip install watchdog"
        )
        sys.exit(1)

    class ConfigFileHandler(FileSystemEventHandler):
        def __init__(self, file_to_watch: Path):
            self.file_to_watch = file_to_watch.resolve()
            self.last_modified: float = 0.0

        def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
            if event.src_path == str(self.file_to_watch):
                # Debounce rapid modifications
                import time

                current_time = time.time()
                if current_time - self.last_modified < 1:
                    return
                self.last_modified = current_time

                console.print("\n[dim]File changed, regenerating...[/dim]")
                try:
                    _translate_once(config_file, output, format, False, False, lua_dir, verbose)
                except Exception as e:
                    console.print(f"[bold red]Error:[/bold red] {e}")

    console.print(f"[bold green]Watching[/bold green] {config_file} for changes...")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    # Initial generation
    _translate_once(config_file, output, format, False, False, lua_dir, verbose)

    # Setup file watcher
    event_handler = ConfigFileHandler(config_file)
    observer = Observer()
    observer.schedule(event_handler, str(config_file.parent), recursive=False)
    observer.start()

    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopping watcher...[/dim]")
        observer.stop()
        observer.join()


def _display_security_report(report: SecurityReport) -> None:
    """Display security validation report."""
    from rich.table import Table

    from ..validators.security import SecurityLevel

    # Define colors for each level
    level_colors = {
        SecurityLevel.CRITICAL: "bold red",
        SecurityLevel.HIGH: "red",
        SecurityLevel.MEDIUM: "yellow",
        SecurityLevel.LOW: "cyan",
        SecurityLevel.INFO: "dim",
    }

    if not report.issues:
        console.print("\n[bold green]Security Check Passed[/bold green]")
        console.print("[dim]No security issues found.[/dim]\n")
        return

    # Count issues by level
    counts: dict[SecurityLevel, int] = {}
    for issue in report.issues:
        counts[issue.level] = counts.get(issue.level, 0) + 1

    # Print summary
    console.print("\n[bold]Security Check Report[/bold]")
    summary_parts = []
    for level in [
        SecurityLevel.CRITICAL,
        SecurityLevel.HIGH,
        SecurityLevel.MEDIUM,
        SecurityLevel.LOW,
        SecurityLevel.INFO,
    ]:
        if level in counts:
            color = level_colors[level]
            summary_parts.append(f"[{color}]{level.value}: {counts[level]}[/{color}]")
    console.print("  " + " | ".join(summary_parts))

    # Create detailed table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Level", width=10)
    table.add_column("Location", width=30)
    table.add_column("Issue", width=40)
    table.add_column("Recommendation", width=40)

    for issue in sorted(report.issues, key=lambda x: list(SecurityLevel).index(x.level)):
        color = level_colors[issue.level]
        table.add_row(
            f"[{color}]{issue.level.value}[/{color}]",
            issue.location,
            issue.message,
            issue.recommendation,
        )

    console.print(table)

    if report.passed:
        console.print("\n[bold green]Security Check Passed[/bold green] (warnings only)\n")
    else:
        console.print("\n[bold red]Security Check Failed[/bold red] (critical/high issues found)\n")


def _list_formats() -> None:
    """List available input formats."""
    console.print("\n[bold]Available Input Formats:[/bold]\n")

    formats = ParserRegistry.list_formats()

    for format_name in formats:
        parser = ParserRegistry.get_parser(format_name=format_name)
        exts = parser.file_extensions
        ext_str = ", ".join(exts)
        console.print(f"  • [cyan]{format_name:8s}[/cyan] {ext_str}")

    console.print()


if __name__ == "__main__":
    cli()
