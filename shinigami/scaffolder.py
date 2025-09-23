from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from shinigami.models import ProjectSpec


class Scaffolder:
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            keep_trailing_newline=True,
        )

    def scaffold(self, spec: ProjectSpec, output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []
        created.extend(self._render_dir("common", spec, output_dir))
        stack_dir = self._stack_template_dir(spec)
        if stack_dir:
            created.extend(self._render_dir(stack_dir, spec, output_dir))
        return created

    def _render_dir(self, template_subdir: str, spec: ProjectSpec, output_dir: Path) -> list[Path]:
        created: list[Path] = []
        tpl_dir = self.templates_dir / template_subdir
        if not tpl_dir.exists():
            return created
        for tpl_file in tpl_dir.rglob("*.j2"):
            rel = tpl_file.relative_to(tpl_dir)
            out_path = output_dir / str(rel).removesuffix(".j2")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            tpl_name = f"{template_subdir}/{rel.as_posix()}"
            template = self.env.get_template(tpl_name)
            out_path.write_text(template.render(spec=spec))
            created.append(out_path)
        return created

    def _stack_template_dir(self, spec: ProjectSpec) -> str | None:
        mapping = {
            "express": "node-express",
            "fastapi": "python-fastapi",
            "gin": "go",
            "fiber": "go",
            "gin/fiber": "go",
            "actix-web": "rust-actix",
            "drogon": "cpp-drogon",
        }
        framework = spec.stack.framework.split(" + ")[0].lower()
        return mapping.get(framework)
