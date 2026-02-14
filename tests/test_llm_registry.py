from phoneybaloney.providers.llm import register_all_llm
from phoneybaloney.providers.base import ProviderRegistry


def test_all_llm_providers_registered():
    registry = ProviderRegistry()
    register_all_llm(registry)
    providers = registry.list_llm_providers()
    assert "ollama" in providers
    assert "openai" in providers
    assert "claude" in providers
