import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from shinigami.config import load_settings
from shinigami.models import load_spec, list_specs
from shinigami.llm import get_provider
from shinigami.generator import Generator

app = typer.Typer(name="shinigami", help="Backend API code generation agent")
console = Console()


@app.command()
def generate(
    name: str = typer.Argument(help="Project name (e.g. taskflow)"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM provider (claude/openai)"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Generate a full backend API project."""
    settings = load_settings(config)
    if provider:
        settings.provider = provider

    try:
        spec = load_spec(name, settings.specs_dir)
    except FileNotFoundError:
        console.print(f"[red]Error: spec '{name}' not found[/]")
        raise typer.Exit(1)

    try:
        llm = get_provider(settings)
    except Exception as e:
        console.print(f"[red]Error initializing LLM provider: {e}[/]")
        raise typer.Exit(1)

    gen = Generator(settings=settings, provider=llm)
    output = asyncio.run(gen.generate(spec))
    console.print(f"\n[bold green]Done! Project at: {output}[/]")


@app.command(name="list")
def list_projects(
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
):
    """List all available project specs."""
    settings = load_settings(config)
    specs = list_specs(settings.specs_dir)

    table = Table(title="Available Projects")
    table.add_column("#", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Stack", style="yellow")

    for i, spec in enumerate(specs, 1):
        table.add_row(str(i), spec.display_name, spec.category, f"{spec.stack.language}/{spec.stack.framework}")

    console.print(table)


@app.command()
def info(
    name: str = typer.Argument(help="Project name"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
):
    """Show details about a project spec."""
    settings = load_settings(config)
    try:
        spec = load_spec(name, settings.specs_dir)
    except FileNotFoundError:
        console.print(f"[red]Error: spec '{name}' not found[/]")
        raise typer.Exit(1)

    console.print(f"[bold]{spec.display_name}[/] — {spec.description}")
    console.print(f"Category: {spec.category}")
    console.print(f"Stack: {spec.stack.language} / {spec.stack.framework} / {spec.stack.database}")
    console.print(f"Models: {', '.join(spec.models)}")
    console.print(f"Routes: {len(spec.api_routes)} groups")
    for r in spec.api_routes:
        console.print(f"  {r.prefix}: {', '.join(r.endpoints)}")
