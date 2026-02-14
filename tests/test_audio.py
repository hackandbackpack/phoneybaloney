import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.audio import play_audio, list_microphones, get_default_microphone


class TestPlayAudio:
    @patch("phoneybaloney.audio.PYGAME_AVAILABLE", True)
    @patch("phoneybaloney.audio.pygame")
    def test_play_audio_calls_mixer(self, mock_pygame):
        mock_pygame.mixer.get_init.return_value = True
        mock_pygame.mixer.music.get_busy.side_effect = [True, False]
        mock_pygame.time = MagicMock()

        play_audio(b"RIFF" + b"\x00" * 100)
        mock_pygame.mixer.music.load.assert_called_once()
        mock_pygame.mixer.music.play.assert_called_once()

    @patch("phoneybaloney.audio.PYGAME_AVAILABLE", True)
    @patch("phoneybaloney.audio.pygame")
    def test_play_audio_inits_mixer_if_needed(self, mock_pygame):
        mock_pygame.mixer.get_init.return_value = False
        mock_pygame.mixer.music.get_busy.return_value = False

        play_audio(b"audio_data")
        mock_pygame.mixer.init.assert_called_once()

    @patch("phoneybaloney.audio.PYGAME_AVAILABLE", False)
    def test_play_audio_raises_without_pygame(self):
        with pytest.raises(RuntimeError, match="pygame"):
            play_audio(b"data")


class TestListMicrophones:
    @patch("phoneybaloney.audio.SR_AVAILABLE", True)
    @patch("phoneybaloney.audio.sr")
    def test_list_microphones(self, mock_sr):
        mock_sr.Microphone.list_microphone_names.return_value = ["Mic 1", "Mic 2"]
        mics = list_microphones()
        assert len(mics) == 2
        assert mics[0]["name"] == "Mic 1"
        assert mics[0]["index"] == 0

    @patch("phoneybaloney.audio.SR_AVAILABLE", False)
    def test_list_microphones_no_sr(self):
        assert list_microphones() == []


class TestGetDefaultMicrophone:
    @patch("phoneybaloney.audio.SR_AVAILABLE", True)
    @patch("phoneybaloney.audio.sr")
    def test_get_default(self, mock_sr):
        mock_sr.Microphone.list_microphone_names.return_value = ["Default Mic"]
        assert get_default_microphone() == "Default Mic"

    @patch("phoneybaloney.audio.SR_AVAILABLE", False)
    def test_get_default_no_sr(self):
        assert get_default_microphone() == ""
