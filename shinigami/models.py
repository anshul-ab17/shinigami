from pathlib import Path
from pydantic import BaseModel
import yaml


class StackConfig(BaseModel):
    language: str
    framework: str
    database: str
    orm: str | None = None
    cache: str | None = None
    auth: str | None = None


class RouteGroup(BaseModel):
    prefix: str
    endpoints: list[str]


class ProjectSpec(BaseModel):
    name: str
    display_name: str
    category: str
    folder: str
    description: str
    stack: StackConfig
    features: list[str]
    models: list[str]
    api_routes: list[RouteGroup]


def load_spec(name: str, specs_dir: Path) -> ProjectSpec:
    for category_dir in specs_dir.iterdir():
        if not category_dir.is_dir():
            continue
        spec_file = category_dir / f"{name}.yaml"
        if spec_file.exists():
            with open(spec_file) as f:
                data = yaml.safe_load(f)
            return ProjectSpec(**data)
    raise FileNotFoundError(f"Spec '{name}' not found in {specs_dir}")


def list_specs(specs_dir: Path) -> list[ProjectSpec]:
    specs = []
    for category_dir in sorted(specs_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        for spec_file in sorted(category_dir.glob("*.yaml")):
            with open(spec_file) as f:
                data = yaml.safe_load(f)
            specs.append(ProjectSpec(**data))
    return specs
