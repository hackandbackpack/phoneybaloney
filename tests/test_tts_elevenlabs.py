import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.tts.elevenlabs_tts import ElevenLabsTTS


class TestElevenLabsTTS:
    def test_initialize(self):
        tts = ElevenLabsTTS()
        tts.initialize({"api_key": "test-key"})
        assert tts.api_key == "test-key"

    @patch("phoneybaloney.providers.tts.elevenlabs_tts.requests")
    def test_synthesize_returns_bytes(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio_data"
        mock_requests.post.return_value = mock_response

        tts = ElevenLabsTTS()
        tts.initialize({"api_key": "test-key", "voice_map": {"female_default": "voice-id-123"}})
        result = tts.synthesize("hello", "female_default")
        assert result == b"audio_data"

    @patch("phoneybaloney.providers.tts.elevenlabs_tts.requests")
    def test_list_voices(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "voices": [
                {"voice_id": "abc123", "name": "Rachel", "labels": {"gender": "female"}},
            ]
        }
        mock_requests.get.return_value = mock_response

        tts = ElevenLabsTTS()
        tts.initialize({"api_key": "test-key"})
        voices = tts.list_voices()
        assert len(voices) >= 1
        assert voices[0]["id"] == "abc123"

    @patch("phoneybaloney.providers.tts.elevenlabs_tts.requests")
    def test_validate_success(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"voices": [{"voice_id": "abc"}]}
        mock_requests.get.return_value = mock_response

        tts = ElevenLabsTTS()
        tts.initialize({"api_key": "test-key"})
        success, msg = tts.validate()
        assert success is True

    @patch("phoneybaloney.providers.tts.elevenlabs_tts.requests")
    def test_validate_bad_key(self, mock_requests):
        mock_requests.get.side_effect = Exception("Unauthorized")

        tts = ElevenLabsTTS()
        tts.initialize({"api_key": "bad"})
        success, msg = tts.validate()
        assert success is False
