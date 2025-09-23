from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock

from shinigami.cli import app

runner = CliRunner()


def test_cli_list(tmp_path):
    with patch("shinigami.cli.load_settings") as mock_settings:
        with patch("shinigami.cli.list_specs") as mock_list:
            mock_settings.return_value = MagicMock(specs_dir=tmp_path)
            spec = MagicMock()
            spec.display_name = "TaskFlow"
            spec.category = "SaaS"
            spec.stack.language = "python"
            spec.stack.framework = "fastapi"
            mock_list.return_value = [spec]
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "TaskFlow" in result.output


def test_cli_list_empty(tmp_path):
    with patch("shinigami.cli.load_settings") as mock_settings:
        with patch("shinigami.cli.list_specs") as mock_list:
            mock_settings.return_value = MagicMock(specs_dir=tmp_path)
            mock_list.return_value = []
            result = runner.invoke(app, ["list"])
            assert result.exit_code == 0


def test_cli_info_found():
    with patch("shinigami.cli.load_settings") as mock_settings:
        with patch("shinigami.cli.load_spec") as mock_load:
            mock_settings.return_value = MagicMock()
            spec = MagicMock()
            spec.display_name = "TaskFlow"
            spec.description = "Task manager"
            spec.category = "SaaS"
            spec.stack.language = "python"
            spec.stack.framework = "fastapi"
            spec.stack.database = "postgres"
            spec.models = ["User", "Task"]
            spec.api_routes = []
            mock_load.return_value = spec
            result = runner.invoke(app, ["info", "taskflow"])
            assert result.exit_code == 0
            assert "TaskFlow" in result.output


def test_cli_info_not_found():
    with patch("shinigami.cli.load_settings") as mock_settings:
        with patch("shinigami.cli.load_spec", side_effect=FileNotFoundError("not found")):
            mock_settings.return_value = MagicMock()
            result = runner.invoke(app, ["info", "nonexistent"])
            assert result.exit_code != 0 or "not found" in result.output.lower() or "error" in result.output.lower()


def test_cli_generate_missing_api_key():
    with patch("shinigami.cli.load_settings") as mock_settings:
        mock_settings.return_value = MagicMock(provider="claude")
        with patch("shinigami.cli.load_spec") as mock_load:
            mock_load.return_value = MagicMock()
            with patch("shinigami.cli.get_provider", side_effect=Exception("No API key")):
                result = runner.invoke(app, ["generate", "taskflow"])
                assert result.exit_code != 0 or "error" in result.output.lower()


def test_cli_generate_success():
    with patch("shinigami.cli.load_settings") as mock_settings:
        with patch("shinigami.cli.load_spec") as mock_load:
            with patch("shinigami.cli.get_provider") as mock_provider:
                with patch("shinigami.cli.Generator") as mock_gen_cls:
                    mock_settings.return_value = MagicMock(provider="claude")
                    mock_load.return_value = MagicMock()
                    mock_provider.return_value = MagicMock()
                    mock_gen = MagicMock()
                    mock_gen.generate = AsyncMock(return_value=Path("/tmp/output"))
                    mock_gen_cls.return_value = mock_gen
                    result = runner.invoke(app, ["generate", "taskflow"])
                    assert result.exit_code == 0
                    assert "Done" in result.output


def test_cli_generate_spec_not_found():
    with patch("shinigami.cli.load_settings") as mock_settings:
        with patch("shinigami.cli.load_spec", side_effect=FileNotFoundError("not found")):
            mock_settings.return_value = MagicMock(provider="claude")
            result = runner.invoke(app, ["generate", "nonexistent"])
            assert result.exit_code != 0 or "error" in result.output.lower()


def test_cli_generate_provider_override():
    with patch("shinigami.cli.load_settings") as mock_settings:
        with patch("shinigami.cli.load_spec") as mock_load:
            with patch("shinigami.cli.get_provider") as mock_provider:
                with patch("shinigami.cli.Generator") as mock_gen_cls:
                    settings = MagicMock(provider="claude")
                    mock_settings.return_value = settings
                    mock_load.return_value = MagicMock()
                    mock_provider.return_value = MagicMock()
                    mock_gen = MagicMock()
                    mock_gen.generate = AsyncMock(return_value=Path("/tmp/output"))
                    mock_gen_cls.return_value = mock_gen
                    runner.invoke(app, ["generate", "taskflow", "--provider", "openai"])
                    assert settings.provider == "openai"
