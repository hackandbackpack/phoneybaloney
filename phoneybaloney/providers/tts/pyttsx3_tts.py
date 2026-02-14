"""pyttsx3 TTS provider — free, offline system voices."""
import tempfile
from pathlib import Path

import pyttsx3

from phoneybaloney.providers.base import BaseTTS


class Pyttsx3TTS(BaseTTS):
    """TTS provider using pyttsx3 (system voices)."""

    def initialize(self, config: dict) -> None:
        self.engine = pyttsx3.init()
        self.rate = config.get("rate", 175)
        self.engine.setProperty("rate", self.rate)
        self.voice_map = config.get("voice_map", {})

    def synthesize(self, text: str, voice: str) -> bytes:
        voice_id = self.voice_map.get(voice, "")
        if voice_id:
            self.engine.setProperty("voice", voice_id)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        self.engine.save_to_file(text, tmp_path)
        self.engine.runAndWait()

        audio_data = Path(tmp_path).read_bytes()
        Path(tmp_path).unlink(missing_ok=True)
        return audio_data

    def list_voices(self) -> list[dict]:
        voices = self.engine.getProperty("voices")
        return [
            {"id": v.id, "name": v.name, "gender": getattr(v, "gender", "unknown")}
            for v in voices
        ]

    def validate(self) -> tuple[bool, str]:
        try:
            voices = self.engine.getProperty("voices")
            if voices:
                return True, f"pyttsx3 ready, {len(voices)} voice(s) available"
            return False, "No system voices found"
        except Exception as e:
            return False, f"pyttsx3 validation failed: {e}"
