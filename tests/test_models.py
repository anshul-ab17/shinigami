from pathlib import Path
from shinigami.models import ProjectSpec, StackConfig, RouteGroup, load_spec, list_specs


SAMPLE_YAML = """
name: taskflow
display_name: TaskFlow
category: real-world
folder: "1.taskflow"
description: "Task and project management platform"

stack:
  language: typescript
  framework: express
  database: postgresql
  orm: prisma
  cache: redis
  auth: jwt

features:
  - user authentication
  - team management

models:
  - User
  - Team
  - Task

api_routes:
  - prefix: /auth
    endpoints: [register, login]
  - prefix: /tasks
    endpoints: [create, list, get]
"""


def test_project_spec_from_yaml(tmp_path):
    spec_dir = tmp_path / "real-world"
    spec_dir.mkdir()
    (spec_dir / "taskflow.yaml").write_text(SAMPLE_YAML)
    spec = load_spec("taskflow", tmp_path)
    assert spec.name == "taskflow"
    assert spec.display_name == "TaskFlow"
    assert spec.category == "real-world"
    assert spec.stack.language == "typescript"
    assert spec.stack.framework == "express"
    assert spec.stack.database == "postgresql"
    assert len(spec.api_routes) == 2
    assert spec.api_routes[0].prefix == "/auth"
    assert "register" in spec.api_routes[0].endpoints


def test_load_spec_not_found(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        load_spec("nonexistent", tmp_path)


def test_list_specs(tmp_path):
    for cat in ["real-world", "trading"]:
        d = tmp_path / cat
        d.mkdir()
        (d / "test.yaml").write_text(SAMPLE_YAML)
    specs = list_specs(tmp_path)
    assert len(specs) == 2
