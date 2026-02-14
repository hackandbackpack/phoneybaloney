import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from phoneybaloney.providers.tts.pyttsx3_tts import Pyttsx3TTS


class TestPyttsx3TTS:
    @patch("phoneybaloney.providers.tts.pyttsx3_tts.pyttsx3")
    def test_initialize(self, mock_pyttsx3):
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        tts = Pyttsx3TTS()
        tts.initialize({"rate": 200})
        mock_engine.setProperty.assert_called_with("rate", 200)

    @patch("phoneybaloney.providers.tts.pyttsx3_tts.pyttsx3")
    def test_synthesize_returns_bytes(self, mock_pyttsx3):
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        # Mock save_to_file to write fake audio data
        def fake_save(text, filename):
            with open(filename, "wb") as f:
                f.write(b"RIFF" + b"\x00" * 100)
        mock_engine.save_to_file.side_effect = fake_save

        tts = Pyttsx3TTS()
        tts.initialize({})
        result = tts.synthesize("hello", "female")
        assert isinstance(result, bytes)

    @patch("phoneybaloney.providers.tts.pyttsx3_tts.pyttsx3")
    def test_list_voices(self, mock_pyttsx3):
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.id = "voice1"
        mock_voice.name = "Test Voice"
        mock_engine.getProperty.return_value = [mock_voice]
        mock_pyttsx3.init.return_value = mock_engine

        tts = Pyttsx3TTS()
        tts.initialize({})
        voices = tts.list_voices()
        assert len(voices) >= 1
        assert voices[0]["id"] == "voice1"
        assert voices[0]["name"] == "Test Voice"

    @patch("phoneybaloney.providers.tts.pyttsx3_tts.pyttsx3")
    def test_validate_success(self, mock_pyttsx3):
        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_engine.getProperty.return_value = [mock_voice]
        mock_pyttsx3.init.return_value = mock_engine

        tts = Pyttsx3TTS()
        tts.initialize({})
        success, msg = tts.validate()
        assert success is True

    @patch("phoneybaloney.providers.tts.pyttsx3_tts.pyttsx3")
    def test_validate_no_voices(self, mock_pyttsx3):
        mock_engine = MagicMock()
        mock_engine.getProperty.return_value = []
        mock_pyttsx3.init.return_value = mock_engine

        tts = Pyttsx3TTS()
        tts.initialize({})
        success, msg = tts.validate()
        assert success is False
