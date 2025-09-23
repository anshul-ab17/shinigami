import anthropic
from shinigami.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    async def generate(self, prompt: str, system: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
