"""Optional OpenAI Responses adapter; never called unless the AI feature flag is enabled."""
from openai import OpenAI


class OpenAITextGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.client = OpenAI(api_key=api_key, timeout=15.0, max_retries=1)
        self.model = model

    def generate(self, instructions: str, user_text: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_text,
            max_output_tokens=400,
            store=False,
        )
        return response.output_text
