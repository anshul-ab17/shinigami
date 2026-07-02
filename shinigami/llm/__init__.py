import os
from shinigami.config import Settings
from shinigami.llm.base import LLMProvider
from shinigami.llm.claude import ClaudeProvider
from shinigami.llm.openai_provider import OpenAIProvider
from shinigami.llm.gemini import GeminiProvider


def get_provider(settings: Settings) -> LLMProvider:
    if settings.provider == "claude":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        return ClaudeProvider(model=settings.claude_model, api_key=api_key)
    elif settings.provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        return OpenAIProvider(model=settings.openai_model, api_key=api_key)
    elif settings.provider == "gemini":
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        return GeminiProvider(model=settings.gemini_model, api_key=api_key)
    raise ValueError(f"Unknown provider: {settings.provider}")
