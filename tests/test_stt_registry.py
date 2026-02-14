from phoneybaloney.providers.stt import register_all_stt
from phoneybaloney.providers.base import ProviderRegistry


def test_all_stt_providers_registered():
    registry = ProviderRegistry()
    register_all_stt(registry)
    providers = registry.list_stt_providers()
    assert "whisper_local" in providers
    assert "vosk" in providers
    assert "google_stt" in providers
    assert "whisper_api" in providers
