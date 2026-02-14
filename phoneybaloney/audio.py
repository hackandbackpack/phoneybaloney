"""Audio playback and microphone utilities."""
import io
import tempfile
from pathlib import Path

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


def play_audio(audio_bytes: bytes) -> None:
    """Play WAV/MP3 audio bytes through speakers."""
    if not PYGAME_AVAILABLE:
        raise RuntimeError("pygame not installed. Install with: pip install pygame")

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    audio_fp = io.BytesIO(audio_bytes)
    pygame.mixer.music.load(audio_fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(50)


def list_microphones() -> list[dict]:
    """Return available audio input devices."""
    if not SR_AVAILABLE:
        return []
    try:
        names = sr.Microphone.list_microphone_names()
        return [{"index": i, "name": name} for i, name in enumerate(names)]
    except Exception:
        return []


def get_default_microphone() -> str:
    """Return the default microphone name."""
    mics = list_microphones()
    if mics:
        return mics[0]["name"]
    return ""
