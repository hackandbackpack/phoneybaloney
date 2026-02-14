import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.stt.google_stt import GoogleWebSTT


class TestGoogleWebSTT:
    def test_initialize(self):
        stt = GoogleWebSTT()
        stt.initialize({})
        assert stt.recognizer is not None

    @patch("phoneybaloney.providers.stt.google_stt.sr")
    def test_listen_returns_text(self, mock_sr):
        mock_recognizer = MagicMock()
        mock_audio = MagicMock()
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_google.return_value = "hello world"
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value.__enter__ = MagicMock()
        mock_sr.Microphone.return_value.__exit__ = MagicMock()

        stt = GoogleWebSTT()
        stt.initialize({})
        stt.recognizer = mock_recognizer
        result = stt.listen(15)
        assert result == "hello world"

    @patch("phoneybaloney.providers.stt.google_stt.sr")
    def test_listen_returns_none_on_failure(self, mock_sr):
        mock_recognizer = MagicMock()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.UnknownValueError = Exception
        mock_recognizer.listen.side_effect = Exception("No speech")
        mock_sr.Microphone.return_value.__enter__ = MagicMock()
        mock_sr.Microphone.return_value.__exit__ = MagicMock()

        stt = GoogleWebSTT()
        stt.initialize({})
        stt.recognizer = mock_recognizer
        result = stt.listen(15)
        assert result is None

    @patch("phoneybaloney.providers.stt.google_stt.sr")
    def test_validate_success(self, mock_sr):
        mock_sr.Microphone.list_microphone_names.return_value = ["Mic 1"]

        stt = GoogleWebSTT()
        stt.initialize({})
        success, msg = stt.validate()
        assert success is True

    @patch("phoneybaloney.providers.stt.google_stt.sr")
    def test_validate_no_mic(self, mock_sr):
        mock_sr.Microphone.list_microphone_names.return_value = []

        stt = GoogleWebSTT()
        stt.initialize({})
        success, msg = stt.validate()
        assert success is False
