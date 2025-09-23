import pytest
from pathlib import Path
from unittest.mock import AsyncMock
from shinigami.config import Settings
from shinigami.models import load_spec
from shinigami.generator import Generator


SPECS_DIR = Path(__file__).parent.parent / "shinigami" / "specs"


@pytest.mark.asyncio
async def test_full_pipeline_taskflow(tmp_path):
    """End-to-end: load real spec, scaffold, mock LLM, write files."""
    settings = Settings(
        output_dir=tmp_path,
        specs_dir=SPECS_DIR,
    )
    spec = load_spec("taskflow", SPECS_DIR)

    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// LLM-generated code placeholder"

    gen = Generator(settings=settings, provider=mock_provider)
    output = await gen.generate(spec)

    # Scaffolded files exist
    assert (output / "Dockerfile").exists()
    assert (output / "docker-compose.yaml").exists()
    assert (output / "README.md").exists()
    assert (output / "package.json").exists()
    assert (output / "tsconfig.json").exists()

    # LLM-generated files exist
    assert (output / "prisma" / "schema.prisma").exists()
    assert mock_provider.generate.call_count >= 3  # models + routes + middleware + tests

    # README contains project name
    readme = (output / "README.md").read_text()
    assert "TaskFlow" in readme


@pytest.mark.asyncio
async def test_full_pipeline_corepay_node(tmp_path):
    settings = Settings(output_dir=tmp_path, specs_dir=SPECS_DIR)
    spec = load_spec("corepay", SPECS_DIR)
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// generated"
    gen = Generator(settings=settings, provider=mock_provider)
    output = await gen.generate(spec)
    assert (output / "package.json").exists()


@pytest.mark.asyncio
async def test_full_pipeline_votesphere_go(tmp_path):
    settings = Settings(output_dir=tmp_path, specs_dir=SPECS_DIR)
    spec = load_spec("votesphere", SPECS_DIR)
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// generated"
    gen = Generator(settings=settings, provider=mock_provider)
    output = await gen.generate(spec)
    assert (output / "go.mod").exists()


@pytest.mark.asyncio
async def test_full_pipeline_kaido_rust(tmp_path):
    settings = Settings(output_dir=tmp_path, specs_dir=SPECS_DIR)
    spec = load_spec("kaido", SPECS_DIR)
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// generated"
    gen = Generator(settings=settings, provider=mock_provider)
    output = await gen.generate(spec)
    assert (output / "Cargo.toml").exists()


@pytest.mark.asyncio
async def test_full_pipeline_coinforge_cpp(tmp_path):
    settings = Settings(output_dir=tmp_path, specs_dir=SPECS_DIR)
    spec = load_spec("coinforge", SPECS_DIR)
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "// generated"
    gen = Generator(settings=settings, provider=mock_provider)
    output = await gen.generate(spec)
    assert (output / "CMakeLists.txt").exists()
