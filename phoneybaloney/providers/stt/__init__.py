from phoneybaloney.providers.base import ProviderRegistry
from phoneybaloney.providers.stt.whisper_stt import WhisperLocalSTT
from phoneybaloney.providers.stt.vosk_stt import VoskSTT
from phoneybaloney.providers.stt.google_stt import GoogleWebSTT
from phoneybaloney.providers.stt.openai_stt import OpenAIWhisperSTT


def register_all_stt(registry: ProviderRegistry) -> None:
    registry.register_stt("whisper_local", WhisperLocalSTT)
    registry.register_stt("vosk", VoskSTT)
    registry.register_stt("google_stt", GoogleWebSTT)
    registry.register_stt("whisper_api", OpenAIWhisperSTT)
