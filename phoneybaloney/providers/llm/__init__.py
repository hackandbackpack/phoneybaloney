from phoneybaloney.providers.base import ProviderRegistry
from phoneybaloney.providers.llm.ollama import OllamaLLM
from phoneybaloney.providers.llm.openai_llm import OpenAILLM
from phoneybaloney.providers.llm.claude_llm import ClaudeLLM


def register_all_llm(registry: ProviderRegistry) -> None:
    registry.register_llm("ollama", OllamaLLM)
    registry.register_llm("openai", OpenAILLM)
    registry.register_llm("claude", ClaudeLLM)
