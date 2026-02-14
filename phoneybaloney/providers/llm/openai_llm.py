"""OpenAI LLM provider — GPT models via API."""
import openai
from phoneybaloney.providers.base import BaseLLM


class OpenAILLM(BaseLLM):
    """LLM provider using OpenAI's GPT models."""

    def initialize(self, config: dict) -> None:
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-4o")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_response(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content

    def validate(self) -> tuple[bool, str]:
        try:
            self.client.models.list()
            return True, f"OpenAI connected, using model '{self.model}'"
        except Exception as e:
            return False, f"OpenAI validation failed: {e}"
