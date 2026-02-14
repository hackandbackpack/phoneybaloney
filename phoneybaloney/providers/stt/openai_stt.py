"""OpenAI Whisper API STT provider — paid, high accuracy cloud transcription."""
import io
import tempfile
from pathlib import Path

import openai
import speech_recognition as sr

from phoneybaloney.providers.base import BaseSTT


class OpenAIWhisperSTT(BaseSTT):
    """STT provider using OpenAI's Whisper API."""

    def initialize(self, config: dict) -> None:
        self.api_key = config.get("api_key", "")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.recognizer = sr.Recognizer()

    def listen(self, timeout: int = 15) -> str | None:
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=timeout)
        except Exception:
            return None

        wav_data = audio.get_wav_data()
        audio_file = io.BytesIO(wav_data)
        audio_file.name = "recording.wav"

        try:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            return transcript.text.strip() or None
        except Exception:
            return None

    def validate(self) -> tuple[bool, str]:
        try:
            self.client.models.list()
            return True, "OpenAI Whisper API connected"
        except Exception as e:
            return False, f"OpenAI Whisper API validation failed: {e}"
