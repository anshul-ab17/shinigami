import openai
from shinigami.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    async def generate(self, prompt: str, system: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
