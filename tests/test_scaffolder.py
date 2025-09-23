from pathlib import Path
from shinigami.scaffolder import Scaffolder
from shinigami.models import ProjectSpec, StackConfig, RouteGroup


def make_spec(**overrides) -> ProjectSpec:
    defaults = dict(
        name="testproject",
        display_name="TestProject",
        category="real-world",
        folder="1.testproject",
        description="A test project",
        stack=StackConfig(language="typescript", framework="express", database="postgresql"),
        features=["auth", "crud"],
        models=["User", "Item"],
        api_routes=[RouteGroup(prefix="/auth", endpoints=["login", "register"])],
    )
    defaults.update(overrides)
    return ProjectSpec(**defaults)


def test_scaffold_creates_common_files(tmp_path):
    templates_dir = Path(__file__).parent.parent / "shinigami" / "templates"
    scaffolder = Scaffolder(templates_dir)
    spec = make_spec()
    output = tmp_path / "real-world" / "1.testproject"
    created = scaffolder.scaffold(spec, output)
    assert (output / "Dockerfile").exists()
    assert (output / "docker-compose.yaml").exists()
    assert (output / ".gitignore").exists()
    assert (output / ".env.example").exists()
    assert (output / "README.md").exists()
    assert len(created) >= 5


def test_scaffold_readme_contains_project_name(tmp_path):
    templates_dir = Path(__file__).parent.parent / "shinigami" / "templates"
    scaffolder = Scaffolder(templates_dir)
    spec = make_spec()
    output = tmp_path / "out"
    scaffolder.scaffold(spec, output)
    readme = (output / "README.md").read_text()
    assert "TestProject" in readme


def test_scaffold_node_express(tmp_path):
    templates_dir = Path(__file__).parent.parent / "shinigami" / "templates"
    scaffolder = Scaffolder(templates_dir)
    spec = make_spec(stack=StackConfig(language="typescript", framework="express", database="postgresql", orm="prisma"))
    output = tmp_path / "out"
    scaffolder.scaffold(spec, output)
    assert (output / "package.json").exists()
    assert (output / "tsconfig.json").exists()
    assert (output / "src" / "app.ts").exists()
    pkg = (output / "package.json").read_text()
    assert "express" in pkg


def test_scaffold_python_fastapi(tmp_path):
    templates_dir = Path(__file__).parent.parent / "shinigami" / "templates"
    scaffolder = Scaffolder(templates_dir)
    spec = make_spec(stack=StackConfig(language="python", framework="fastapi", database="postgresql"))
    output = tmp_path / "out"
    scaffolder.scaffold(spec, output)
    assert (output / "pyproject.toml").exists()
    assert (output / "src" / "main.py").exists()


def test_scaffold_go(tmp_path):
    templates_dir = Path(__file__).parent.parent / "shinigami" / "templates"
    scaffolder = Scaffolder(templates_dir)
    spec = make_spec(stack=StackConfig(language="go", framework="gin/fiber", database="postgresql"))
    output = tmp_path / "out"
    scaffolder.scaffold(spec, output)
    assert (output / "go.mod").exists()
    assert (output / "cmd" / "server.go").exists()


def test_scaffold_rust(tmp_path):
    templates_dir = Path(__file__).parent.parent / "shinigami" / "templates"
    scaffolder = Scaffolder(templates_dir)
    spec = make_spec(stack=StackConfig(language="rust", framework="actix-web", database="postgresql"))
    output = tmp_path / "out"
    scaffolder.scaffold(spec, output)
    assert (output / "Cargo.toml").exists()
    assert (output / "src" / "main.rs").exists()


def test_scaffold_cpp(tmp_path):
    templates_dir = Path(__file__).parent.parent / "shinigami" / "templates"
    scaffolder = Scaffolder(templates_dir)
    spec = make_spec(stack=StackConfig(language="cpp", framework="drogon", database="postgresql"))
    output = tmp_path / "out"
    scaffolder.scaffold(spec, output)
    assert (output / "CMakeLists.txt").exists()
    assert (output / "main.cc").exists()
