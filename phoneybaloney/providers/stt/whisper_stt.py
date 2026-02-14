"""Whisper local STT provider — free, offline transcription."""
import tempfile
from pathlib import Path

import speech_recognition as sr

from phoneybaloney.providers.base import BaseSTT

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    whisper = None
    WHISPER_AVAILABLE = False


class WhisperLocalSTT(BaseSTT):
    """STT provider using OpenAI Whisper (local inference)."""

    def initialize(self, config: dict) -> None:
        self.model_name = config.get("model", "base")
        self.model = None
        if WHISPER_AVAILABLE:
            try:
                self.model = whisper.load_model(self.model_name)
            except Exception:
                pass

    def listen(self, timeout: int = 15) -> str | None:
        if self.model is None:
            return None

        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=timeout)
        except Exception:
            return None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.get_wav_data())
            tmp_path = tmp.name

        try:
            result = self.model.transcribe(tmp_path)
            return result.get("text", "").strip() or None
        except Exception:
            return None
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def validate(self) -> tuple[bool, str]:
        if not WHISPER_AVAILABLE:
            return False, "Whisper not installed. Install with: pip install openai-whisper"
        if self.model is not None:
            return True, f"Whisper ready, model: {self.model_name}"
        return False, f"Whisper model '{self.model_name}' failed to load"
