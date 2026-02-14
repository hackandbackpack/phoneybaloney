import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.tts.google_tts import GoogleTTS


class TestGoogleTTS:
    def test_initialize(self):
        tts = GoogleTTS()
        tts.initialize({"api_key": "test-key"})
        assert tts.api_key == "test-key"

    @patch("phoneybaloney.providers.tts.google_tts.requests")
    def test_synthesize_returns_bytes(self, mock_requests):
        import base64
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "audioContent": base64.b64encode(b"audio_data").decode()
        }
        mock_requests.post.return_value = mock_response

        tts = GoogleTTS()
        tts.initialize({"api_key": "test-key", "voice_map": {"female_default": "en-US-Journey-F"}})
        result = tts.synthesize("hello", "female_default")
        assert result == b"audio_data"

    @patch("phoneybaloney.providers.tts.google_tts.requests")
    def test_list_voices(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "voices": [
                {"name": "en-US-Journey-F", "ssmlGender": "FEMALE", "languageCodes": ["en-US"]},
            ]
        }
        mock_requests.get.return_value = mock_response

        tts = GoogleTTS()
        tts.initialize({"api_key": "test-key"})
        voices = tts.list_voices()
        assert len(voices) >= 1

    @patch("phoneybaloney.providers.tts.google_tts.requests")
    def test_validate_success(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"voices": [{"name": "test"}]}
        mock_requests.get.return_value = mock_response

        tts = GoogleTTS()
        tts.initialize({"api_key": "test-key"})
        success, msg = tts.validate()
        assert success is True

    @patch("phoneybaloney.providers.tts.google_tts.requests")
    def test_validate_bad_key(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = Exception("Forbidden")
        mock_requests.get.return_value = mock_response

        tts = GoogleTTS()
        tts.initialize({"api_key": "bad-key"})
        success, msg = tts.validate()
        assert success is False
