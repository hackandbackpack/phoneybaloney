from phoneybaloney.providers.base import ProviderRegistry
from phoneybaloney.providers.tts.pyttsx3_tts import Pyttsx3TTS
from phoneybaloney.providers.tts.coqui_tts import CoquiTTS
from phoneybaloney.providers.tts.google_tts import GoogleTTS
from phoneybaloney.providers.tts.elevenlabs_tts import ElevenLabsTTS


def register_all_tts(registry: ProviderRegistry) -> None:
    registry.register_tts("pyttsx3", Pyttsx3TTS)
    registry.register_tts("coqui", CoquiTTS)
    registry.register_tts("google_tts", GoogleTTS)
    registry.register_tts("elevenlabs", ElevenLabsTTS)
