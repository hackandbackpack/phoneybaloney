"""Ollama LLM provider — free, local inference."""
import requests
from phoneybaloney.providers.base import BaseLLM


class OllamaLLM(BaseLLM):
    """LLM provider using locally-running Ollama."""

    def initialize(self, config: dict) -> None:
        self.model = config.get("model", "llama3")
        self.url = config.get("url", "http://localhost:11434")

    def generate_response(self, messages: list[dict]) -> str:
        response = requests.post(
            f"{self.url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def validate(self) -> tuple[bool, str]:
        try:
            response = requests.get(f"{self.url}/api/tags")
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            # Check if model (with or without tag) is available
            model_found = any(
                self.model in name or name.startswith(self.model)
                for name in models
            )
            if model_found:
                return True, f"Ollama connected, model '{self.model}' available"
            return False, f"Ollama running but model '{self.model}' not found. Run: ollama pull {self.model}"
        except Exception as e:
            return False, f"Ollama not reachable at {self.url}. Is it running? Error: {e}"
