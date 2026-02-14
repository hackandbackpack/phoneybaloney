"""Google Web Speech STT provider — free, cloud-based."""
import speech_recognition as sr

from phoneybaloney.providers.base import BaseSTT


class GoogleWebSTT(BaseSTT):
    """STT provider using Google Web Speech API (via SpeechRecognition)."""

    def initialize(self, config: dict) -> None:
        self.recognizer = sr.Recognizer()

    def listen(self, timeout: int = 15) -> str | None:
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=timeout)
            text = self.recognizer.recognize_google(audio)
            return text.strip() or None
        except Exception:
            return None

    def validate(self) -> tuple[bool, str]:
        try:
            mics = sr.Microphone.list_microphone_names()
            if mics:
                return True, f"Google Web Speech ready, {len(mics)} microphone(s) detected"
            return False, "No microphones detected"
        except Exception as e:
            return False, f"Google Web Speech validation failed: {e}"
