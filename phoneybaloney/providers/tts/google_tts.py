"""Google Cloud TTS provider — mid-tier cloud voices."""
import base64

import requests

from phoneybaloney.providers.base import BaseTTS

API_BASE = "https://texttospeech.googleapis.com/v1"


class GoogleTTS(BaseTTS):
    """TTS provider using Google Cloud Text-to-Speech API."""

    def initialize(self, config: dict) -> None:
        self.api_key = config.get("api_key", "")
        self.voice_map = config.get("voice_map", {})
        self.language_code = config.get("language_code", "en-US")

    def synthesize(self, text: str, voice: str) -> bytes:
        voice_name = self.voice_map.get(voice, voice)
        response = requests.post(
            f"{API_BASE}/text:synthesize",
            headers={"X-Goog-Api-Key": self.api_key},
            json={
                "input": {"text": text},
                "voice": {"languageCode": self.language_code, "name": voice_name},
                "audioConfig": {"audioEncoding": "LINEAR16"},
            },
        )
        response.raise_for_status()
        return base64.b64decode(response.json()["audioContent"])

    def list_voices(self) -> list[dict]:
        try:
            response = requests.get(
                f"{API_BASE}/voices",
                params={"key": self.api_key},
            )
            response.raise_for_status()
            voices = response.json().get("voices", [])
            return [
                {
                    "id": v["name"],
                    "name": v["name"],
                    "gender": v.get("ssmlGender", "unknown"),
                    "language": v.get("languageCodes", ["unknown"])[0],
                }
                for v in voices
            ]
        except Exception:
            return []

    def validate(self) -> tuple[bool, str]:
        try:
            response = requests.get(
                f"{API_BASE}/voices",
                params={"key": self.api_key},
            )
            response.raise_for_status()
            voices = response.json().get("voices", [])
            return True, f"Google TTS connected, {len(voices)} voices available"
        except Exception as e:
            return False, f"Google TTS validation failed: {e}"
