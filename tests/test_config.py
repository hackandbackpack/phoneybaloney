import pytest
from pathlib import Path
from phoneybaloney.config import AppConfig, load_config, save_config, generate_default_config


class TestLoadConfig:
    def test_load_valid_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
llm_provider: ollama
tts_provider: pyttsx3
stt_provider: whisper_local

ollama:
  model: llama3
  url: http://localhost:11434

pyttsx3:
  rate: 175
  voice_map:
    female_default: ""
    male_default: ""

whisper_local:
  model: base

scenario: megacorp
log_transcripts: true
""")
        config = load_config(str(config_file))
        assert config.llm_provider == "ollama"
        assert config.tts_provider == "pyttsx3"
        assert config.stt_provider == "whisper_local"
        assert config.log_transcripts is True

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_get_provider_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
llm_provider: openai
tts_provider: pyttsx3
stt_provider: whisper_local

openai:
  api_key: "test-key-123"
  model: gpt-4o

pyttsx3:
  rate: 175

whisper_local:
  model: base
""")
        config = load_config(str(config_file))
        openai_config = config.get_llm_config()
        assert openai_config["api_key"] == "test-key-123"
        assert openai_config["model"] == "gpt-4o"

    def test_get_provider_config_returns_empty_for_unconfigured(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
llm_provider: ollama
tts_provider: pyttsx3
stt_provider: whisper_local
""")
        config = load_config(str(config_file))
        assert config.get_llm_config() == {}


class TestSaveConfig:
    def test_save_and_reload(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config = AppConfig(
            llm_provider="claude",
            tts_provider="elevenlabs",
            stt_provider="whisper_local",
            log_transcripts=True,
            scenario="megacorp",
            raw={"claude": {"api_key": "sk-test"}, "elevenlabs": {"api_key": "el-test"},
                 "whisper_local": {"model": "base"}}
        )
        save_config(config, str(config_file))
        reloaded = load_config(str(config_file))
        assert reloaded.llm_provider == "claude"
        assert reloaded.get_llm_config()["api_key"] == "sk-test"


class TestGenerateDefaultConfig:
    def test_generates_file(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        generate_default_config(str(config_file))
        assert config_file.exists()
        config = load_config(str(config_file))
        assert config.llm_provider == "ollama"
        assert config.tts_provider == "pyttsx3"
        assert config.stt_provider == "whisper_local"
