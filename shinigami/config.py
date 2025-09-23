from pathlib import Path
from pydantic_settings import BaseSettings
import yaml


class Settings(BaseSettings):
    provider: str = "claude"
    claude_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    output_dir: Path = Path("../backend")
    specs_dir: Path = Path(__file__).parent / "specs"
    templates_dir: Path = Path(__file__).parent / "templates"

    model_config = {"env_prefix": "SHINIGAMI_"}


def load_settings(config_path: Path | None = None) -> Settings:
    if config_path and config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        return Settings(**data)
    return Settings()
