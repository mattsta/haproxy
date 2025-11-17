"""Command-line interface for HAProxy configuration translator."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

from ..parsers import ParserRegistry
from ..codegen.haproxy import HAProxyCodeGenerator
from ..lua.manager import LuaManager
from ..utils.errors import TranslatorError
from .. import __version__

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
@click.version_option(version=__version__, prog_name="haproxy-translate")
def cli(
    config_file: Path,
    output: Optional[Path],
    format: Optional[str],
    validate: bool,
    debug: bool,
    watch: bool,
    lua_dir: Optional[Path],
    list_formats: bool,
    verbose: bool,
) -> None:
    """
    HAProxy Configuration Translator.

    Translate modern configuration formats (DSL, YAML, HCL) to native HAProxy format.

    \b
    Examples:
        haproxy-translate config.hap -o haproxy.cfg
        haproxy-translate config.yaml --format yaml --validate
        haproxy-translate config.hap -o haproxy.cfg --watch
    """
    if list_formats:
        _list_formats()
        return

    try:
        if watch:
            _watch_mode(config_file, output, format, lua_dir, verbose)
        else:
            _translate_once(config_file, output, format, validate, debug, lua_dir, verbose)

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
    output: Optional[Path],
    format: Optional[str],
    validate: bool,
    debug: bool,
    lua_dir: Optional[Path],
    verbose: bool,
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
        console.print(f"[dim]Extracted Lua scripts:[/dim]")
        for name, path in lua_manager.get_script_paths().items():
            console.print(f"  - {name}: {path}")

    # Generate HAProxy configuration
    with console.status("[bold green]Generating HAProxy config...", spinner="dots"):
        generator = HAProxyCodeGenerator()
        config = generator.generate(ir, output_path=output)

    # Output
    if output:
        console.print(
            f"[bold green]✓[/bold green] Configuration written to: [cyan]{output}[/cyan]"
        )
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
    output: Optional[Path],
    format: Optional[str],
    lua_dir: Optional[Path],
    verbose: bool,
) -> None:
    """Watch for file changes and regenerate."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler, FileModifiedEvent
    except ImportError:
        console.print(
            "[bold red]Error:[/bold red] Watch mode requires 'watchdog' package. "
            "Install with: pip install watchdog"
        )
        sys.exit(1)

    class ConfigFileHandler(FileSystemEventHandler):
        def __init__(self, file_to_watch: Path):
            self.file_to_watch = file_to_watch.resolve()
            self.last_modified = 0

        def on_modified(self, event: FileModifiedEvent) -> None:
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


def _list_formats() -> None:
    """List available input formats."""
    console.print("\n[bold]Available Input Formats:[/bold]\n")

    formats = ParserRegistry.list_formats()
    extensions = ParserRegistry.list_extensions()

    for format_name in formats:
        parser = ParserRegistry.get_parser(format_name=format_name)
        exts = parser.file_extensions
        ext_str = ", ".join(exts)
        console.print(f"  • [cyan]{format_name:8s}[/cyan] {ext_str}")

    console.print()


if __name__ == "__main__":
    cli()
