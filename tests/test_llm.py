import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from shinigami.llm.base import LLMProvider
from shinigami.llm.claude import ClaudeProvider
from shinigami.llm.openai_provider import OpenAIProvider
from shinigami.llm import get_provider
from shinigami.config import Settings


def test_llm_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


def test_get_provider_claude():
    settings = Settings(provider="claude")
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        provider = get_provider(settings)
        assert isinstance(provider, ClaudeProvider)


def test_get_provider_openai():
    settings = Settings(provider="openai")
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        provider = get_provider(settings)
        assert isinstance(provider, OpenAIProvider)


def test_get_provider_unknown():
    settings = Settings(provider="gemini")
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider(settings)


@pytest.mark.asyncio
async def test_claude_provider_generate():
    with patch("shinigami.llm.claude.anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="generated code")]
        )
        provider = ClaudeProvider(model="claude-sonnet-4-6", api_key="test")
        result = await provider.generate("write code", "you are a dev")
        assert result == "generated code"


@pytest.mark.asyncio
async def test_openai_provider_generate():
    with patch("shinigami.llm.openai_provider.openai") as mock_openai:
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="generated code"))]
        )
        provider = OpenAIProvider(model="gpt-4o", api_key="test")
        result = await provider.generate("write code", "you are a dev")
        assert result == "generated code"
