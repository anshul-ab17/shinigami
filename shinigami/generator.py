from pathlib import Path
from rich.console import Console
from shinigami.config import Settings
from shinigami.models import ProjectSpec
from shinigami.scaffolder import Scaffolder
from shinigami.llm.base import LLMProvider
from shinigami.writer import Writer
from shinigami.prompts import (
    build_system_prompt,
    build_models_prompt,
    build_routes_prompt,
    build_middleware_prompt,
    build_tests_prompt,
)

console = Console()

# Maps language to file paths for generated code
FILE_TARGETS = {
    "typescript": {
        "models": "prisma/schema.prisma",
        "middleware": "src/middleware/index.ts",
        "tests": "tests/api.test.ts",
        "route_template": "src/routes{prefix}.ts",
    },
    "python": {
        "models": "src/models.py",
        "middleware": "src/middleware.py",
        "tests": "tests/test_api.py",
        "route_template": "src/routes{prefix}.py",
    },
    "go": {
        "models": "internal/models/models.go",
        "middleware": "internal/middleware/middleware.go",
        "tests": "tests/api_test.go",
        "route_template": "internal/handlers{prefix}.go",
    },
    "rust": {
        "models": "src/models.rs",
        "middleware": "src/middleware.rs",
        "tests": "tests/api_test.rs",
        "route_template": "src/handlers{prefix}.rs",
    },
    "cpp": {
        "models": "models/models.h",
        "middleware": "middleware/middleware.h",
        "tests": "tests/api_test.cc",
        "route_template": "controllers{prefix}.cc",
    },
}


class Generator:
    def __init__(self, settings: Settings, provider: LLMProvider):
        self.settings = settings
        self.provider = provider
        self.scaffolder = Scaffolder(settings.templates_dir)

    async def generate(self, spec: ProjectSpec) -> Path:
        output_dir = self.settings.output_dir / spec.category / spec.folder
        writer = Writer(output_dir)
        targets = FILE_TARGETS.get(spec.stack.language.lower(), FILE_TARGETS["python"])
        system = build_system_prompt(spec)

        # Step 1: Scaffold (idempotent — Jinja templates always overwrite)
        console.print(f"[bold blue]Scaffolding {spec.display_name}...[/]")
        self.scaffolder.scaffold(spec, output_dir)

        # Step 2: Generate models
        models_path = targets["models"]
        if not writer.is_written(models_path):
            console.print("[yellow]Generating models...[/]")
            code = await self.provider.generate(build_models_prompt(spec), system)
            writer.write_file(models_path, code)

        # Step 3: Generate routes (one file per prefix)
        for route in spec.api_routes:
            # ponytail: replace / with _ to keep filenames flat; nested prefixes like /auth/v2 → _auth_v2
            route_path = targets["route_template"].format(prefix=route.prefix.replace("/", "_"))
            if not writer.is_written(route_path):
                console.print(f"[yellow]Generating routes for {route.prefix}...[/]")
                code = await self.provider.generate(build_routes_prompt(spec, route), system)
                writer.write_file(route_path, code)

        # Step 4: Generate middleware
        mw_path = targets["middleware"]
        if not writer.is_written(mw_path):
            console.print("[yellow]Generating middleware...[/]")
            code = await self.provider.generate(build_middleware_prompt(spec), system)
            writer.write_file(mw_path, code)

        # Step 5: Generate tests
        test_path = targets["tests"]
        if not writer.is_written(test_path):
            console.print("[yellow]Generating tests...[/]")
            code = await self.provider.generate(build_tests_prompt(spec), system)
            writer.write_file(test_path, code)

        console.print(f"[bold green]✓ {spec.display_name} generated at {output_dir}[/]")
        return output_dir
