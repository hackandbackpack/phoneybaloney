import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.stt.whisper_stt import WhisperLocalSTT


class TestWhisperLocalSTT:
    def test_initialize_stores_config(self):
        stt = WhisperLocalSTT()
        stt.initialize({"model": "base"})
        assert stt.model_name == "base"

    def test_initialize_defaults(self):
        stt = WhisperLocalSTT()
        stt.initialize({})
        assert stt.model_name == "base"

    @patch("phoneybaloney.providers.stt.whisper_stt.WHISPER_AVAILABLE", True)
    @patch("phoneybaloney.providers.stt.whisper_stt.whisper")
    def test_validate_success(self, mock_whisper):
        mock_whisper.load_model.return_value = MagicMock()
        stt = WhisperLocalSTT()
        stt.initialize({"model": "base"})
        stt.model = MagicMock()
        success, msg = stt.validate()
        assert success is True

    @patch("phoneybaloney.providers.stt.whisper_stt.WHISPER_AVAILABLE", False)
    def test_validate_not_installed(self):
        stt = WhisperLocalSTT()
        stt.initialize({})
        success, msg = stt.validate()
        assert success is False
        assert "not installed" in msg.lower()

    @patch("phoneybaloney.providers.stt.whisper_stt.WHISPER_AVAILABLE", True)
    @patch("phoneybaloney.providers.stt.whisper_stt.sr")
    @patch("phoneybaloney.providers.stt.whisper_stt.whisper")
    def test_listen_returns_text(self, mock_whisper, mock_sr):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "hello world"}
        mock_whisper.load_model.return_value = mock_model

        mock_recognizer = MagicMock()
        mock_audio = MagicMock()
        mock_audio.get_wav_data.return_value = b"wav_data"
        mock_recognizer.listen.return_value = mock_audio
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value.__enter__ = MagicMock()
        mock_sr.Microphone.return_value.__exit__ = MagicMock()

        stt = WhisperLocalSTT()
        stt.initialize({"model": "base"})
        stt.model = mock_model
        result = stt.listen(15)
        assert result == "hello world"
