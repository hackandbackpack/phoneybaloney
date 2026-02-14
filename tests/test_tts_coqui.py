import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.tts.coqui_tts import CoquiTTS


class TestCoquiTTS:
    @patch("phoneybaloney.providers.tts.coqui_tts.TTS_CLASS", create=True)
    def test_initialize(self, mock_tts_cls):
        tts = CoquiTTS()
        tts.initialize({"model": "tts_models/en/ljspeech/tacotron2-DDC"})
        assert tts.model_name == "tts_models/en/ljspeech/tacotron2-DDC"

    @patch("phoneybaloney.providers.tts.coqui_tts.TTS_CLASS", create=True)
    def test_synthesize_returns_bytes(self, mock_tts_cls):
        mock_instance = MagicMock()
        mock_tts_cls.return_value = mock_instance
        mock_instance.tts_to_file.return_value = None

        tts = CoquiTTS()
        tts.initialize({"model": "tts_models/en/ljspeech/tacotron2-DDC"})
        # Mock file reading
        with patch("phoneybaloney.providers.tts.coqui_tts.Path") as mock_path:
            mock_path.return_value.read_bytes.return_value = b"audio_data"
            mock_path.return_value.unlink = MagicMock()
            result = tts.synthesize("hello", "female")
        assert isinstance(result, bytes)

    @patch("phoneybaloney.providers.tts.coqui_tts.TTS_CLASS", create=True)
    def test_validate_success(self, mock_tts_cls):
        mock_tts_cls.return_value = MagicMock()
        tts = CoquiTTS()
        tts.initialize({"model": "tts_models/en/ljspeech/tacotron2-DDC"})
        success, msg = tts.validate()
        assert success is True

    @patch("phoneybaloney.providers.tts.coqui_tts.TTS_CLASS", None)
    def test_validate_not_installed(self):
        tts = CoquiTTS()
        tts.initialize({})
        success, msg = tts.validate()
        assert success is False
