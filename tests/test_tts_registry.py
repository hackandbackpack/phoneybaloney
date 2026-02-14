from phoneybaloney.providers.tts import register_all_tts
from phoneybaloney.providers.base import ProviderRegistry


def test_all_tts_providers_registered():
    registry = ProviderRegistry()
    register_all_tts(registry)
    providers = registry.list_tts_providers()
    assert "pyttsx3" in providers
    assert "coqui" in providers
    assert "google_tts" in providers
    assert "elevenlabs" in providers
