import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.stt.openai_stt import OpenAIWhisperSTT


class TestOpenAIWhisperSTT:
    def test_initialize(self):
        stt = OpenAIWhisperSTT()
        stt.initialize({"api_key": "sk-test"})
        assert stt.api_key == "sk-test"

    @patch("phoneybaloney.providers.stt.openai_stt.openai")
    @patch("phoneybaloney.providers.stt.openai_stt.sr")
    def test_listen_returns_text(self, mock_sr, mock_openai):
        mock_recognizer = MagicMock()
        mock_audio = MagicMock()
        mock_audio.get_wav_data.return_value = b"wav_data"
        mock_recognizer.listen.return_value = mock_audio
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value.__enter__ = MagicMock()
        mock_sr.Microphone.return_value.__exit__ = MagicMock()

        mock_transcript = MagicMock()
        mock_transcript.text = "hello from whisper"
        mock_openai.OpenAI.return_value.audio.transcriptions.create.return_value = mock_transcript

        stt = OpenAIWhisperSTT()
        stt.initialize({"api_key": "sk-test"})
        stt.recognizer = mock_recognizer
        result = stt.listen(15)
        assert result == "hello from whisper"

    @patch("phoneybaloney.providers.stt.openai_stt.openai")
    def test_validate_success(self, mock_openai):
        mock_openai.OpenAI.return_value.models.list.return_value = MagicMock()

        stt = OpenAIWhisperSTT()
        stt.initialize({"api_key": "sk-test"})
        success, msg = stt.validate()
        assert success is True

    @patch("phoneybaloney.providers.stt.openai_stt.openai")
    def test_validate_bad_key(self, mock_openai):
        mock_openai.OpenAI.return_value.models.list.side_effect = Exception("Invalid key")

        stt = OpenAIWhisperSTT()
        stt.initialize({"api_key": "bad"})
        success, msg = stt.validate()
        assert success is False
