from google import genai
from google.genai import types
from shinigami.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = genai.Client(api_key=api_key)

    async def generate(self, prompt: str, system: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return response.text
