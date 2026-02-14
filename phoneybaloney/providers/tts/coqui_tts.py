"""Coqui TTS provider — free, neural quality offline voices."""
import tempfile
from pathlib import Path

from phoneybaloney.providers.base import BaseTTS

try:
    from TTS.api import TTS as TTS_CLASS
except ImportError:
    TTS_CLASS = None


class CoquiTTS(BaseTTS):
    """TTS provider using Coqui TTS (neural voices)."""

    def initialize(self, config: dict) -> None:
        self.model_name = config.get("model", "tts_models/en/ljspeech/tacotron2-DDC")
        self.tts = None
        if TTS_CLASS is not None:
            self.tts = TTS_CLASS(model_name=self.model_name)

    def synthesize(self, text: str, voice: str) -> bytes:
        if self.tts is None:
            raise RuntimeError("Coqui TTS not installed. Install with: pip install TTS")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        self.tts.tts_to_file(text=text, file_path=tmp_path)
        audio_data = Path(tmp_path).read_bytes()
        Path(tmp_path).unlink(missing_ok=True)
        return audio_data

    def list_voices(self) -> list[dict]:
        if TTS_CLASS is None:
            return []
        try:
            models = TTS_CLASS().list_models()
            return [{"id": m, "name": m} for m in models if "en" in m]
        except Exception:
            return []

    def validate(self) -> tuple[bool, str]:
        if TTS_CLASS is None:
            return False, "Coqui TTS not installed. Install with: pip install TTS"
        try:
            if self.tts is not None:
                return True, f"Coqui TTS ready, model: {self.model_name}"
            return False, "Coqui TTS model not loaded"
        except Exception as e:
            return False, f"Coqui TTS validation failed: {e}"
