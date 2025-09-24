import asyncio
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from shinigami.config import load_settings
from shinigami.models import ProjectSpec, StackConfig, RouteGroup, load_spec, list_specs
from shinigami.llm import get_provider
from shinigami.generator import Generator

app = typer.Typer(name="shinigami", help="Backend API code generation agent")
console = Console()

FRAMEWORK_MAP = {
    "typescript": ["Express", "Express + Prisma"],
    "python": ["FastAPI", "FastAPI + SQLAlchemy"],
    "go": ["Gin", "Gin/Fiber"],
    "rust": ["Actix-web", "Actix-web + SQLx"],
    "cpp": ["Drogon"],
}

ORM_MAP = {
    "Express + Prisma": "prisma",
    "FastAPI + SQLAlchemy": "sqlalchemy",
    "Actix-web + SQLx": "sqlx",
}


@app.command()
def create(
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output path for spec YAML"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Interactively create a new project spec."""
    console.print("[bold cyan]Shinigami — Create New Project[/]\n")

    # Basic info
    name = Prompt.ask("[bold]Project name[/] (lowercase slug)").strip().lower().replace(" ", "-")
    display_name = Prompt.ask("[bold]Display name[/]", default=name.title().replace("-", ""))
    description = Prompt.ask("[bold]Description[/]")
    category = Prompt.ask("[bold]Category[/]", choices=["real-world", "trading", "agentic", "custom"], default="real-world")
    folder = Prompt.ask("[bold]Folder name[/]", default=f"1.{name}")

    # Stack
    console.print("\n[bold yellow]Stack Configuration[/]")
    language = Prompt.ask("[bold]Language[/]", choices=["typescript", "python", "go", "rust", "cpp"], default="typescript")

    frameworks = FRAMEWORK_MAP[language]
    if len(frameworks) == 1:
        framework = frameworks[0]
        console.print(f"  Framework: {framework}")
    else:
        framework = Prompt.ask("[bold]Framework[/]", choices=frameworks, default=frameworks[0])

    database = Prompt.ask("[bold]Database[/]", choices=["postgresql", "mongodb"], default="postgresql")
    cache = "redis" if Confirm.ask("[bold]Need Redis cache?[/]", default=False) else None
    auth = None
    auth_choice = Prompt.ask("[bold]Auth type[/]", choices=["jwt", "oauth", "none"], default="jwt")
    if auth_choice != "none":
        auth = auth_choice

    orm = ORM_MAP.get(framework)

    stack = StackConfig(language=language, framework=framework, database=database, orm=orm, cache=cache, auth=auth)

    # Features
    console.print("\n[bold yellow]Features[/]")
    console.print("  Enter features one per line. Empty line to finish.")
    features: list[str] = []
    while True:
        feat = Prompt.ask(f"  Feature {len(features) + 1}", default="")
        if not feat:
            if not features:
                console.print("  [red]Need at least one feature[/]")
                continue
            break
        features.append(feat)

    # Models
    console.print("\n[bold yellow]Models[/]")
    console.print("  Enter model names one per line. Empty line to finish.")
    models: list[str] = []
    while True:
        model = Prompt.ask(f"  Model {len(models) + 1}", default="")
        if not model:
            if not models:
                console.print("  [red]Need at least one model[/]")
                continue
            break
        models.append(model)

    # Routes
    console.print("\n[bold yellow]API Routes[/]")
    console.print("  Define route groups. Empty prefix to finish.")
    api_routes: list[RouteGroup] = []
    while True:
        prefix = Prompt.ask(f"  Route prefix {len(api_routes) + 1} (e.g. /auth)", default="")
        if not prefix:
            if not api_routes:
                console.print("  [red]Need at least one route group[/]")
                continue
            break
        if not prefix.startswith("/"):
            prefix = f"/{prefix}"
        endpoints_str = Prompt.ask("    Endpoints (comma-separated)")
        endpoints = [e.strip() for e in endpoints_str.split(",") if e.strip()]
        if endpoints:
            api_routes.append(RouteGroup(prefix=prefix, endpoints=endpoints))

    # Build spec
    spec = ProjectSpec(
        name=name,
        display_name=display_name,
        category=category,
        folder=folder,
        description=description,
        stack=stack,
        features=features,
        models=models,
        api_routes=api_routes,
    )

    # Preview
    console.print("\n[bold green]Preview:[/]")
    console.print(f"  {spec.display_name} — {spec.description}")
    console.print(f"  Stack: {spec.stack.language}/{spec.stack.framework}/{spec.stack.database}")
    console.print(f"  Models: {', '.join(spec.models)}")
    console.print(f"  Routes: {len(spec.api_routes)} groups")
    for r in spec.api_routes:
        console.print(f"    {r.prefix}: {', '.join(r.endpoints)}")

    if not Confirm.ask("\n[bold]Save this spec?[/]", default=True):
        console.print("[yellow]Cancelled.[/]")
        raise typer.Exit(0)

    # Save
    spec_data = spec.model_dump(exclude_none=True)
    if output:
        out_path = output
    else:
        settings = load_settings(config)
        cat_dir = settings.specs_dir / spec.category
        cat_dir.mkdir(parents=True, exist_ok=True)
        out_path = cat_dir / f"{spec.name}.yaml"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[bold green]✓ Spec saved to {out_path}[/]")

    if Confirm.ask("[bold]Generate project now?[/]", default=False):
        try:
            settings = load_settings(config)
            llm = get_provider(settings)
            gen = Generator(settings=settings, provider=llm)
            result = asyncio.run(gen.generate(spec))
            console.print(f"\n[bold green]Done! Project at: {result}[/]")
        except Exception as e:
            console.print(f"[red]Generation failed: {e}[/]")
            console.print(f"Spec saved — run [cyan]shinigami generate {spec.name}[/] later.")


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
