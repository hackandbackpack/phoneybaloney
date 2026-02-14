"""Vosk STT provider — free, lightweight offline transcription."""
import json
from pathlib import Path

import speech_recognition as sr

from phoneybaloney.providers.base import BaseSTT

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False


class VoskSTT(BaseSTT):
    """STT provider using Vosk (lightweight offline)."""

    def initialize(self, config: dict) -> None:
        self.model_path = config.get("model_path", "")
        self.model = None
        if VOSK_AVAILABLE and self.model_path and Path(self.model_path).exists():
            try:
                self.model = Model(self.model_path)
            except Exception:
                pass

    def listen(self, timeout: int = 15) -> str | None:
        if self.model is None:
            return None

        recognizer = sr.Recognizer()
        try:
            with sr.Microphone(sample_rate=16000) as source:
                audio = recognizer.listen(source, timeout=timeout)
        except Exception:
            return None

        rec = KaldiRecognizer(self.model, 16000)
        rec.AcceptWaveform(audio.get_raw_data(convert_rate=16000, convert_width=2))
        result = json.loads(rec.FinalResult())
        text = result.get("text", "").strip()
        return text or None

    def validate(self) -> tuple[bool, str]:
        if not VOSK_AVAILABLE:
            return False, "Vosk not installed. Install with: pip install vosk"
        if not self.model_path or not Path(self.model_path).exists():
            return False, "Vosk model path not set or doesn't exist"
        if not Path(self.model_path).is_dir():
            return False, f"Vosk model path is not a directory: {self.model_path}"
        return True, f"Vosk ready, model: {self.model_path}"
