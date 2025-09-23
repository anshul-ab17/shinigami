from shinigami.prompts import (
    build_system_prompt,
    build_models_prompt,
    build_routes_prompt,
    build_middleware_prompt,
    build_tests_prompt,
)
from shinigami.models import ProjectSpec, StackConfig, RouteGroup


def make_spec() -> ProjectSpec:
    return ProjectSpec(
        name="taskflow",
        display_name="TaskFlow",
        category="real-world",
        folder="1.taskflow",
        description="Task management platform",
        stack=StackConfig(language="typescript", framework="express", database="postgresql", orm="prisma", auth="jwt"),
        features=["auth", "task crud"],
        models=["User", "Task"],
        api_routes=[RouteGroup(prefix="/auth", endpoints=["register", "login"])],
    )


def test_system_prompt_contains_stack():
    prompt = build_system_prompt(make_spec())
    assert "typescript" in prompt.lower()
    assert "express" in prompt.lower()
    assert "prisma" in prompt.lower()


def test_models_prompt_contains_model_names():
    prompt = build_models_prompt(make_spec())
    assert "User" in prompt
    assert "Task" in prompt


def test_routes_prompt_contains_endpoints():
    spec = make_spec()
    prompt = build_routes_prompt(spec, spec.api_routes[0])
    assert "/auth" in prompt
    assert "register" in prompt
    assert "login" in prompt


def test_middleware_prompt_contains_auth():
    prompt = build_middleware_prompt(make_spec())
    assert "jwt" in prompt.lower() or "auth" in prompt.lower()


def test_tests_prompt_mentions_testing():
    prompt = build_tests_prompt(make_spec())
    assert "test" in prompt.lower()
