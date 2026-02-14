"""Anthropic Claude LLM provider."""
import anthropic
from phoneybaloney.providers.base import BaseLLM


class ClaudeLLM(BaseLLM):
    """LLM provider using Anthropic's Claude models."""

    def initialize(self, config: dict) -> None:
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "claude-sonnet-4-5-20250929")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_response(self, messages: list[dict]) -> str:
        system_prompt = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=filtered_messages,
        )
        return response.content[0].text

    def validate(self) -> tuple[bool, str]:
        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True, f"Claude connected, using model '{self.model}'"
        except Exception as e:
            return False, f"Claude validation failed: {e}"
