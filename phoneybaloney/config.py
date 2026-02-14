"""Configuration loading, saving, and validation."""
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AppConfig:
    """Application configuration."""
    llm_provider: str = "ollama"
    tts_provider: str = "pyttsx3"
    stt_provider: str = "whisper_local"
    scenario: str = "megacorp"
    log_transcripts: bool = True
    raw: dict = field(default_factory=dict)

    def get_llm_config(self) -> dict:
        return self.raw.get(self.llm_provider, {})

    def get_tts_config(self) -> dict:
        return self.raw.get(self.tts_provider, {})

    def get_stt_config(self) -> dict:
        return self.raw.get(self.stt_provider, {})

    def get_voice_map(self) -> dict:
        tts_config = self.get_tts_config()
        return tts_config.get("voice_map", {
            "female_default": "",
            "male_default": "",
        })


def load_config(path: str) -> AppConfig:
    """Load configuration from a YAML file."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    return AppConfig(
        llm_provider=raw.get("llm_provider", "ollama"),
        tts_provider=raw.get("tts_provider", "pyttsx3"),
        stt_provider=raw.get("stt_provider", "whisper_local"),
        scenario=raw.get("scenario", "megacorp"),
        log_transcripts=raw.get("log_transcripts", True),
        raw=raw,
    )


def save_config(config: AppConfig, path: str) -> None:
    """Save configuration to a YAML file."""
    data = dict(config.raw)
    data["llm_provider"] = config.llm_provider
    data["tts_provider"] = config.tts_provider
    data["stt_provider"] = config.stt_provider
    data["scenario"] = config.scenario
    data["log_transcripts"] = config.log_transcripts

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def generate_default_config(path: str) -> None:
    """Generate a default config.yaml with all options documented."""
    default = AppConfig(
        raw={
            "ollama": {"model": "llama3", "url": "http://localhost:11434"},
            "openai": {"api_key": "", "model": "gpt-4o"},
            "claude": {"api_key": "", "model": "claude-sonnet-4-5-20250929"},
            "pyttsx3": {"rate": 175, "voice_map": {"female_default": "", "male_default": ""}},
            "coqui": {"model": "tts_models/en/ljspeech/tacotron2-DDC"},
            "google_tts": {"api_key": "", "voice_map": {"female_default": "", "male_default": ""}},
            "elevenlabs": {"api_key": "", "voice_map": {"female_default": "", "male_default": ""}},
            "whisper_local": {"model": "base"},
            "vosk": {"model_path": ""},
            "google_stt": {},
            "whisper_api": {},
        }
    )
    save_config(default, path)
