"""ElevenLabs TTS provider — premium cloud voices."""
import requests

from phoneybaloney.providers.base import BaseTTS

API_BASE = "https://api.elevenlabs.io/v1"


class ElevenLabsTTS(BaseTTS):
    """TTS provider using ElevenLabs API."""

    def initialize(self, config: dict) -> None:
        self.api_key = config.get("api_key", "")
        self.voice_map = config.get("voice_map", {})
        self.model_id = config.get("model_id", "eleven_monolingual_v1")

    def synthesize(self, text: str, voice: str) -> bytes:
        voice_id = self.voice_map.get(voice, voice)
        response = requests.post(
            f"{API_BASE}/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": self.model_id,
            },
        )
        response.raise_for_status()
        return response.content

    def list_voices(self) -> list[dict]:
        try:
            response = requests.get(
                f"{API_BASE}/voices",
                headers={"xi-api-key": self.api_key},
            )
            response.raise_for_status()
            voices = response.json().get("voices", [])
            return [
                {
                    "id": v["voice_id"],
                    "name": v["name"],
                    "gender": v.get("labels", {}).get("gender", "unknown"),
                }
                for v in voices
            ]
        except Exception:
            return []

    def validate(self) -> tuple[bool, str]:
        try:
            response = requests.get(
                f"{API_BASE}/voices",
                headers={"xi-api-key": self.api_key},
            )
            response.raise_for_status()
            voices = response.json().get("voices", [])
            return True, f"ElevenLabs connected, {len(voices)} voices available"
        except Exception as e:
            return False, f"ElevenLabs validation failed: {e}"
