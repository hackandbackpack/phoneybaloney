import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.stt.vosk_stt import VoskSTT


class TestVoskSTT:
    def test_initialize_stores_config(self):
        stt = VoskSTT()
        stt.initialize({"model_path": "/path/to/model"})
        assert stt.model_path == "/path/to/model"

    @patch("phoneybaloney.providers.stt.vosk_stt.VOSK_AVAILABLE", False)
    def test_validate_not_installed(self):
        stt = VoskSTT()
        stt.initialize({})
        success, msg = stt.validate()
        assert success is False
        assert "not installed" in msg.lower()

    @patch("phoneybaloney.providers.stt.vosk_stt.VOSK_AVAILABLE", True)
    @patch("phoneybaloney.providers.stt.vosk_stt.Path")
    def test_validate_no_model_path(self, mock_path):
        mock_path.return_value.exists.return_value = False
        stt = VoskSTT()
        stt.initialize({"model_path": ""})
        success, msg = stt.validate()
        assert success is False

    @patch("phoneybaloney.providers.stt.vosk_stt.VOSK_AVAILABLE", True)
    @patch("phoneybaloney.providers.stt.vosk_stt.Path")
    def test_validate_success(self, mock_path):
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.is_dir.return_value = True
        stt = VoskSTT()
        stt.initialize({"model_path": "/valid/path"})
        success, msg = stt.validate()
        assert success is True
