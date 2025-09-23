import pytest
from pathlib import Path
from unittest.mock import AsyncMock
from shinigami.generator import Generator
from shinigami.config import Settings
from shinigami.models import ProjectSpec, StackConfig, RouteGroup


def make_spec() -> ProjectSpec:
    return ProjectSpec(
        name="testapp",
        display_name="TestApp",
        category="real-world",
        folder="1.testapp",
        description="A test app",
        stack=StackConfig(language="typescript", framework="express", database="postgresql", orm="prisma", auth="jwt"),
        features=["auth"],
        models=["User"],
        api_routes=[RouteGroup(prefix="/auth", endpoints=["login"])],
    )


@pytest.mark.asyncio
async def test_generator_creates_output_dir(tmp_path):
    settings = Settings(output_dir=tmp_path / "backend")
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// generated code"
    gen = Generator(settings=settings, provider=mock_provider)
    spec = make_spec()
    output = await gen.generate(spec)
    assert output.exists()
    assert (output / "Dockerfile").exists()
    assert (output / "README.md").exists()


@pytest.mark.asyncio
async def test_generator_calls_llm_for_models(tmp_path):
    settings = Settings(output_dir=tmp_path / "backend")
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// generated code"
    gen = Generator(settings=settings, provider=mock_provider)
    spec = make_spec()
    await gen.generate(spec)
    assert mock_provider.generate.call_count >= 1
    calls = [str(c) for c in mock_provider.generate.call_args_list]
    any_models_call = any("User" in str(c) for c in mock_provider.generate.call_args_list)
    assert any_models_call


@pytest.mark.asyncio
async def test_generator_resumes(tmp_path):
    settings = Settings(output_dir=tmp_path / "backend")
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// generated code"
    gen = Generator(settings=settings, provider=mock_provider)
    spec = make_spec()
    await gen.generate(spec)
    first_call_count = mock_provider.generate.call_count
    # Second run should skip already-written files
    mock_provider.reset_mock()
    gen2 = Generator(settings=settings, provider=mock_provider)
    await gen2.generate(spec)
    assert mock_provider.generate.call_count < first_call_count
