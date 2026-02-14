# PhoneyBaloney Redesign — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild PhoneyBaloney as a modular, multi-provider vishing simulator with a web UI, replacing the single-file monolith.

**Architecture:** Plugin-based provider system with abstract base classes for LLM, TTS, and STT. FastAPI web UI with WebSocket for real-time session interaction. YAML-based scenarios with hidden secrets. Cross-platform installer.

**Tech Stack:** Python 3.10+, FastAPI, uvicorn, Jinja2, WebSocket, PyYAML, pyttsx3, openai-whisper, openai, anthropic, ollama, elevenlabs, google-cloud-texttospeech, vosk, SpeechRecognition, PyAudio

**Design Doc:** `docs/plans/2026-02-14-phoneybaloney-redesign-design.md`

---

## Phase 1: Project Scaffolding & Core Infrastructure

### Task 1: Create Project Structure

**Files:**
- Create: `phoneybaloney/__init__.py`
- Create: `phoneybaloney/providers/__init__.py`
- Create: `phoneybaloney/providers/llm/__init__.py`
- Create: `phoneybaloney/providers/tts/__init__.py`
- Create: `phoneybaloney/providers/stt/__init__.py`
- Create: `phoneybaloney/web/__init__.py`
- Create: `phoneybaloney/web/static/.gitkeep`
- Create: `phoneybaloney/web/templates/.gitkeep`
- Create: `scenarios/.gitkeep`
- Create: `transcripts/.gitkeep`
- Create: `requirements/base.txt`
- Create: `phoneybaloney/__main__.py`

**Step 1: Create all directories and init files**

```python
# phoneybaloney/__init__.py
__version__ = "2.0.0"
```

```python
# phoneybaloney/__main__.py
"""Entry point for python -m phoneybaloney."""
from phoneybaloney.app import main

if __name__ == "__main__":
    main()
```

```
# requirements/base.txt
fastapi>=0.109.0
uvicorn>=0.27.0
jinja2>=3.1.0
pyyaml>=6.0
colorama>=0.4.6
python-multipart>=0.0.6
websockets>=12.0
```

All `__init__.py` files in providers/ subdirectories are empty initially.

**Step 2: Verify structure**

Run: `python -c "import phoneybaloney; print(phoneybaloney.__version__)"`
Expected: `2.0.0`

**Step 3: Commit**

```bash
git add phoneybaloney/ scenarios/ transcripts/ requirements/
git commit -m "Scaffold project structure for modular redesign"
```

---

### Task 2: Provider Base Classes

**Files:**
- Create: `phoneybaloney/providers/base.py`
- Create: `tests/__init__.py`
- Create: `tests/test_providers_base.py`

**Step 1: Write the failing tests**

```python
# tests/test_providers_base.py
import pytest
from phoneybaloney.providers.base import BaseLLM, BaseTTS, BaseSTT, ProviderRegistry


class TestBaseLLM:
    def test_cannot_instantiate_directly(self):
        """Base classes should not be used directly without implementing methods."""
        llm = BaseLLM()
        with pytest.raises(NotImplementedError):
            llm.initialize({})

    def test_generate_response_not_implemented(self):
        llm = BaseLLM()
        with pytest.raises(NotImplementedError):
            llm.generate_response([])


class TestBaseTTS:
    def test_synthesize_not_implemented(self):
        tts = BaseTTS()
        with pytest.raises(NotImplementedError):
            tts.synthesize("hello", "female")

    def test_list_voices_not_implemented(self):
        tts = BaseTTS()
        with pytest.raises(NotImplementedError):
            tts.list_voices()

    def test_validate_not_implemented(self):
        tts = BaseTTS()
        with pytest.raises(NotImplementedError):
            tts.validate()


class TestBaseSTT:
    def test_listen_not_implemented(self):
        stt = BaseSTT()
        with pytest.raises(NotImplementedError):
            stt.listen(15)

    def test_validate_not_implemented(self):
        stt = BaseSTT()
        with pytest.raises(NotImplementedError):
            stt.validate()


class TestProviderRegistry:
    def test_register_and_get_llm(self):
        registry = ProviderRegistry()

        class FakeLLM(BaseLLM):
            def initialize(self, config):
                pass
            def generate_response(self, messages):
                return "hello"
            def validate(self):
                return True, "OK"

        registry.register_llm("fake", FakeLLM)
        provider = registry.get_llm("fake")
        assert isinstance(provider, FakeLLM)

    def test_register_and_get_tts(self):
        registry = ProviderRegistry()

        class FakeTTS(BaseTTS):
            def initialize(self, config):
                pass
            def synthesize(self, text, voice):
                return b"audio"
            def list_voices(self):
                return ["voice1"]
            def validate(self):
                return True, "OK"

        registry.register_tts("fake", FakeTTS)
        provider = registry.get_tts("fake")
        assert isinstance(provider, FakeTTS)

    def test_register_and_get_stt(self):
        registry = ProviderRegistry()

        class FakeSTT(BaseSTT):
            def initialize(self, config):
                pass
            def listen(self, timeout):
                return "hello"
            def validate(self):
                return True, "OK"

        registry.register_stt("fake", FakeSTT)
        provider = registry.get_stt("fake")
        assert isinstance(provider, FakeSTT)

    def test_get_unknown_provider_raises(self):
        registry = ProviderRegistry()
        with pytest.raises(KeyError):
            registry.get_llm("nonexistent")

    def test_list_providers(self):
        registry = ProviderRegistry()

        class FakeLLM(BaseLLM):
            def initialize(self, config): pass
            def generate_response(self, messages): return ""
            def validate(self): return True, "OK"

        registry.register_llm("fake1", FakeLLM)
        registry.register_llm("fake2", FakeLLM)
        assert set(registry.list_llm_providers()) == {"fake1", "fake2"}
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_providers_base.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'phoneybaloney.providers.base'`

**Step 3: Write the implementation**

```python
# phoneybaloney/providers/base.py
"""Abstract base classes for all providers."""


class BaseLLM:
    """Base class for LLM providers (conversation intelligence)."""

    def initialize(self, config: dict) -> None:
        """Set up the provider with config values (API keys, model names, etc.)."""
        raise NotImplementedError

    def generate_response(self, messages: list[dict]) -> str:
        """Generate a response given a conversation history.

        Args:
            messages: List of dicts with 'role' and 'content' keys.
                      Roles: 'system', 'user', 'assistant'

        Returns:
            The assistant's response text.
        """
        raise NotImplementedError

    def validate(self) -> tuple[bool, str]:
        """Test that the provider is properly configured and reachable.

        Returns:
            Tuple of (success: bool, message: str)
        """
        raise NotImplementedError


class BaseTTS:
    """Base class for Text-to-Speech providers (voice output)."""

    def initialize(self, config: dict) -> None:
        """Set up the provider with config values."""
        raise NotImplementedError

    def synthesize(self, text: str, voice: str) -> bytes:
        """Convert text to audio.

        Args:
            text: The text to speak.
            voice: Voice identifier (mapped from scenario gender/tone via config).

        Returns:
            Audio data as bytes (WAV format).
        """
        raise NotImplementedError

    def list_voices(self) -> list[dict]:
        """Return available voices from this provider.

        Returns:
            List of dicts with at least 'id' and 'name' keys.
            May also include 'gender', 'language', 'preview_url'.
        """
        raise NotImplementedError

    def validate(self) -> tuple[bool, str]:
        """Test that the provider is properly configured and reachable."""
        raise NotImplementedError


class BaseSTT:
    """Base class for Speech-to-Text providers (voice input)."""

    def initialize(self, config: dict) -> None:
        """Set up the provider with config values."""
        raise NotImplementedError

    def listen(self, timeout: int = 15) -> str | None:
        """Listen for speech and return transcribed text.

        Args:
            timeout: Max seconds to wait for speech.

        Returns:
            Transcribed text, or None if nothing was understood.
        """
        raise NotImplementedError

    def validate(self) -> tuple[bool, str]:
        """Test that the provider is properly configured and reachable."""
        raise NotImplementedError


class ProviderRegistry:
    """Registry that maps provider names to their classes."""

    def __init__(self):
        self._llm: dict[str, type[BaseLLM]] = {}
        self._tts: dict[str, type[BaseTTS]] = {}
        self._stt: dict[str, type[BaseSTT]] = {}

    def register_llm(self, name: str, cls: type[BaseLLM]) -> None:
        self._llm[name] = cls

    def register_tts(self, name: str, cls: type[BaseTTS]) -> None:
        self._tts[name] = cls

    def register_stt(self, name: str, cls: type[BaseSTT]) -> None:
        self._stt[name] = cls

    def get_llm(self, name: str) -> BaseLLM:
        if name not in self._llm:
            raise KeyError(f"Unknown LLM provider: '{name}'. Available: {list(self._llm.keys())}")
        return self._llm[name]()

    def get_tts(self, name: str) -> BaseTTS:
        if name not in self._tts:
            raise KeyError(f"Unknown TTS provider: '{name}'. Available: {list(self._tts.keys())}")
        return self._tts[name]()

    def get_stt(self, name: str) -> BaseSTT:
        if name not in self._stt:
            raise KeyError(f"Unknown STT provider: '{name}'. Available: {list(self._stt.keys())}")
        return self._stt[name]()

    def list_llm_providers(self) -> list[str]:
        return list(self._llm.keys())

    def list_tts_providers(self) -> list[str]:
        return list(self._tts.keys())

    def list_stt_providers(self) -> list[str]:
        return list(self._stt.keys())
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_providers_base.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add phoneybaloney/providers/base.py tests/
git commit -m "Add provider base classes and registry with tests"
```

---

### Task 3: Configuration System

**Files:**
- Create: `phoneybaloney/config.py`
- Create: `config.example.yaml`
- Create: `tests/test_config.py`

**Step 1: Write the failing tests**

```python
# tests/test_config.py
import pytest
import tempfile
import os
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
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write the implementation**

```python
# phoneybaloney/config.py
"""Configuration loading, saving, and validation."""
import os
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
```

Also create the fully-commented `config.example.yaml` (this is the human-readable reference):

```yaml
# config.example.yaml — see design doc for full commented version
# Copy this to config.yaml and fill in your provider sections.
```

The full commented config.example.yaml should match the design doc Section 3 verbatim.

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_config.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add phoneybaloney/config.py config.example.yaml tests/test_config.py
git commit -m "Add configuration system with load/save/generate and tests"
```

---

### Task 4: Scenario Loader

**Files:**
- Create: `phoneybaloney/scenarios.py`
- Create: `tests/test_scenarios.py`
- Create: `scenarios/megacorp.yaml`
- Create: `scenarios/example_template.yaml`

**Step 1: Write the failing tests**

```python
# tests/test_scenarios.py
import pytest
from pathlib import Path
from phoneybaloney.scenarios import load_scenario, list_scenarios, ScenarioMetadata


class TestListScenarios:
    def test_lists_yaml_files(self, tmp_path):
        (tmp_path / "test1.yaml").write_text("company: Test1\ndescription: Desc1\ndifficulty: Easy\nobjective: Obj1\nstarting_extension: '0'\nglobal_prompt: prompt\ncharacters: []")
        (tmp_path / "test2.yaml").write_text("company: Test2\ndescription: Desc2\ndifficulty: Hard\nobjective: Obj2\nstarting_extension: '0'\nglobal_prompt: prompt\ncharacters: []")
        (tmp_path / "notayaml.txt").write_text("ignored")
        scenarios = list_scenarios(str(tmp_path))
        assert len(scenarios) == 2
        names = [s.company for s in scenarios]
        assert "Test1" in names
        assert "Test2" in names

    def test_metadata_does_not_include_characters(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: SecretCorp
description: A test scenario
difficulty: Medium
objective: Find the secret
starting_extension: "0"
global_prompt: Be secretive
characters:
  - extension: "0"
    name: Hidden Person
    prompt: This is secret info
""")
        scenarios = list_scenarios(str(tmp_path))
        meta = scenarios[0]
        assert meta.company == "SecretCorp"
        assert meta.description == "A test scenario"
        assert not hasattr(meta, "characters")
        assert "Hidden Person" not in str(meta)


class TestLoadScenario:
    def test_load_full_scenario(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: MegaCorp
description: A software company
difficulty: Beginner
objective: Get a password reset
extensions_hint: Start at extension 0
starting_extension: "0"
global_prompt: Do not reveal you are an AI.
characters:
  - extension: "0"
    name: Susan
    title: Operator
    voice:
      gender: female
      tone: warm
    prompt: You are Susan the operator.
  - extension: "100"
    name: Rick
    title: IT Help Desk
    voice:
      gender: male
      tone: professional
    prompt: You are Rick from IT.
""")
        scenario = load_scenario(str(tmp_path / "test.yaml"))
        assert scenario["company"] == "MegaCorp"
        assert scenario["starting_extension"] == "0"
        assert len(scenario["characters"]) == 2
        assert scenario["characters"][0]["name"] == "Susan"

    def test_get_character_by_extension(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: Test
description: Test
difficulty: Easy
objective: Test
starting_extension: "0"
global_prompt: prompt
characters:
  - extension: "0"
    name: First
    voice:
      gender: female
    prompt: You are First.
  - extension: "100"
    name: Second
    voice:
      gender: male
    prompt: You are Second.
""")
        scenario = load_scenario(str(tmp_path / "test.yaml"))
        from phoneybaloney.scenarios import get_character
        char = get_character(scenario, "100")
        assert char["name"] == "Second"

    def test_get_character_invalid_extension(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: Test
description: Test
difficulty: Easy
objective: Test
starting_extension: "0"
global_prompt: prompt
characters:
  - extension: "0"
    name: Only
    voice:
      gender: female
    prompt: You are Only.
""")
        scenario = load_scenario(str(tmp_path / "test.yaml"))
        from phoneybaloney.scenarios import get_character
        assert get_character(scenario, "999") is None

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_scenario("/nonexistent.yaml")
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_scenarios.py -v`
Expected: FAIL

**Step 3: Write the implementation**

```python
# phoneybaloney/scenarios.py
"""Scenario loading and management."""
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ScenarioMetadata:
    """Safe metadata about a scenario — no secrets, no character details."""
    filename: str
    company: str
    description: str
    difficulty: str
    objective: str
    extensions_hint: str
    starting_extension: str


def list_scenarios(scenarios_dir: str) -> list[ScenarioMetadata]:
    """List all scenarios in a directory, returning only safe metadata."""
    scenarios_path = Path(scenarios_dir)
    results = []

    for yaml_file in sorted(scenarios_path.glob("*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        results.append(ScenarioMetadata(
            filename=yaml_file.name,
            company=data.get("company", "Unknown"),
            description=data.get("description", ""),
            difficulty=data.get("difficulty", "Unknown"),
            objective=data.get("objective", ""),
            extensions_hint=data.get("extensions_hint", ""),
            starting_extension=data.get("starting_extension", "0"),
        ))

    return results


def load_scenario(path: str) -> dict:
    """Load a full scenario from a YAML file (for engine use only)."""
    scenario_path = Path(path)
    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with open(scenario_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_character(scenario: dict, extension: str) -> dict | None:
    """Find a character by extension number. Returns None if not found."""
    for character in scenario.get("characters", []):
        if character.get("extension") == extension:
            return character
    return None
```

**Step 4: Write the MegaCorp scenario file**

Create `scenarios/megacorp.yaml` with the full MegaCorp scenario from the design doc (all characters: Susan, Anne, Rick, Jennifer).

**Step 5: Write the example template**

Create `scenarios/example_template.yaml` with placeholder fields and comments explaining each field.

**Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/test_scenarios.py -v`
Expected: ALL PASS

**Step 7: Commit**

```bash
git add phoneybaloney/scenarios.py tests/test_scenarios.py scenarios/
git commit -m "Add scenario loader with metadata safety and YAML scenarios"
```

---

## Phase 2: Provider Implementations

### Task 5: Ollama LLM Provider

**Files:**
- Create: `phoneybaloney/providers/llm/ollama.py`
- Create: `tests/test_llm_ollama.py`

**Step 1: Write the failing tests**

Tests should cover:
- `initialize()` stores model name and URL
- `generate_response()` sends correct message format (mock HTTP call)
- `validate()` returns (False, message) when Ollama is not reachable (mock)
- `validate()` returns (True, message) when Ollama is reachable (mock)

Use `unittest.mock.patch` to mock the `requests` or `ollama` library calls.

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_llm_ollama.py -v`

**Step 3: Implement**

Use the `ollama` Python package. Key methods:
- `initialize()`: store model name and URL
- `generate_response()`: call `ollama.chat()` with messages
- `validate()`: call `ollama.list()` and check model exists

**Step 4: Run tests, verify pass**

**Step 5: Commit**

```bash
git commit -m "Add Ollama LLM provider"
```

---

### Task 6: OpenAI LLM Provider

**Files:**
- Create: `phoneybaloney/providers/llm/openai_llm.py`
- Create: `tests/test_llm_openai.py`

Same pattern as Task 5. Use the `openai` Python package (modern API, v1+).
- `initialize()`: set API key and model
- `generate_response()`: call `client.chat.completions.create()`
- `validate()`: make a lightweight `models.list()` call

**Commit:** `"Add OpenAI LLM provider"`

---

### Task 7: Claude LLM Provider

**Files:**
- Create: `phoneybaloney/providers/llm/claude_llm.py`
- Create: `tests/test_llm_claude.py`

Use the `anthropic` Python package.
- `initialize()`: set API key and model
- `generate_response()`: call `client.messages.create()` — note Claude uses a different message format (system prompt is separate from messages), so this provider handles the translation
- `validate()`: lightweight API call

**Commit:** `"Add Claude LLM provider"`

---

### Task 8: LLM Provider Registration

**Files:**
- Modify: `phoneybaloney/providers/llm/__init__.py`
- Create: `tests/test_llm_registry.py`

**Step 1: Write test**

```python
# tests/test_llm_registry.py
from phoneybaloney.providers.llm import register_all_llm
from phoneybaloney.providers.base import ProviderRegistry

def test_all_llm_providers_registered():
    registry = ProviderRegistry()
    register_all_llm(registry)
    providers = registry.list_llm_providers()
    assert "ollama" in providers
    assert "openai" in providers
    assert "claude" in providers
```

**Step 2: Implement**

```python
# phoneybaloney/providers/llm/__init__.py
from phoneybaloney.providers.base import ProviderRegistry
from phoneybaloney.providers.llm.ollama import OllamaLLM
from phoneybaloney.providers.llm.openai_llm import OpenAILLM
from phoneybaloney.providers.llm.claude_llm import ClaudeLLM

def register_all_llm(registry: ProviderRegistry) -> None:
    registry.register_llm("ollama", OllamaLLM)
    registry.register_llm("openai", OpenAILLM)
    registry.register_llm("claude", ClaudeLLM)
```

**Commit:** `"Register all LLM providers"`

---

### Task 9: pyttsx3 TTS Provider (Free/Offline)

**Files:**
- Create: `phoneybaloney/providers/tts/pyttsx3_tts.py`
- Create: `tests/test_tts_pyttsx3.py`

Key methods:
- `initialize()`: create pyttsx3 engine, set rate
- `synthesize()`: use engine to generate WAV bytes (save to BytesIO)
- `list_voices()`: query system voices, return list with id/name/gender
- `validate()`: check that at least one system voice exists
- Voice mapping: receives `"female"` or `"male"`, maps via config voice_map or auto-selects

**Commit:** `"Add pyttsx3 TTS provider"`

---

### Task 10: Coqui TTS Provider (Free/Neural)

**Files:**
- Create: `phoneybaloney/providers/tts/coqui_tts.py`
- Create: `tests/test_tts_coqui.py`

Uses the `TTS` package from Coqui.
- `initialize()`: load model
- `synthesize()`: generate audio from text
- `list_voices()`: list available/downloaded models
- `validate()`: check model is downloaded

**Commit:** `"Add Coqui TTS provider"`

---

### Task 11: Google Cloud TTS Provider

**Files:**
- Create: `phoneybaloney/providers/tts/google_tts.py`
- Create: `tests/test_tts_google.py`

Uses Google Cloud TTS REST API (same as original code but cleaned up).
- `initialize()`: store API key
- `synthesize()`: POST to texttospeech API, return audio bytes
- `list_voices()`: GET voices.list endpoint, return available voices
- `validate()`: test API key against voices.list

**Commit:** `"Add Google Cloud TTS provider"`

---

### Task 12: ElevenLabs TTS Provider

**Files:**
- Create: `phoneybaloney/providers/tts/elevenlabs_tts.py`
- Create: `tests/test_tts_elevenlabs.py`

Uses the `elevenlabs` Python package.
- `initialize()`: store API key
- `synthesize()`: generate audio via API
- `list_voices()`: fetch available voices including custom/cloned
- `validate()`: test API key

**Commit:** `"Add ElevenLabs TTS provider"`

---

### Task 13: TTS Provider Registration

**Files:**
- Modify: `phoneybaloney/providers/tts/__init__.py`
- Create: `tests/test_tts_registry.py`

Same pattern as Task 8. Register: pyttsx3, coqui, google_tts, elevenlabs.

**Commit:** `"Register all TTS providers"`

---

### Task 14: Whisper Local STT Provider

**Files:**
- Create: `phoneybaloney/providers/stt/whisper_stt.py`
- Create: `tests/test_stt_whisper.py`

Uses `openai-whisper` package (local inference).
- `initialize()`: load whisper model (tiny/base/small/medium/large)
- `listen()`: record from microphone, transcribe with whisper
- `validate()`: check model is loadable

**Commit:** `"Add Whisper local STT provider"`

---

### Task 15: Vosk STT Provider

**Files:**
- Create: `phoneybaloney/providers/stt/vosk_stt.py`
- Create: `tests/test_stt_vosk.py`

Uses `vosk` package.
- `initialize()`: load model from path
- `listen()`: record and transcribe
- `validate()`: check model path exists and is valid

**Commit:** `"Add Vosk STT provider"`

---

### Task 16: Google Web Speech STT Provider

**Files:**
- Create: `phoneybaloney/providers/stt/google_stt.py`
- Create: `tests/test_stt_google.py`

Uses `speech_recognition` package (same as original but cleaned up).
- `initialize()`: create recognizer
- `listen()`: record from mic, call `recognize_google()`
- `validate()`: check microphone available

**Commit:** `"Add Google Web Speech STT provider"`

---

### Task 17: OpenAI Whisper API STT Provider

**Files:**
- Create: `phoneybaloney/providers/stt/openai_stt.py`
- Create: `tests/test_stt_openai.py`

Uses `openai` package's audio transcription API.
- `initialize()`: store API key
- `listen()`: record from mic, send to Whisper API
- `validate()`: test API key

**Commit:** `"Add OpenAI Whisper API STT provider"`

---

### Task 18: STT Provider Registration

**Files:**
- Modify: `phoneybaloney/providers/stt/__init__.py`
- Create: `tests/test_stt_registry.py`

Register: whisper_local, vosk, google_stt, whisper_api.

**Commit:** `"Register all STT providers"`

---

## Phase 3: Core Engine

### Task 19: Session & Transcript Manager

**Files:**
- Create: `phoneybaloney/session.py`
- Create: `tests/test_session.py`

**Step 1: Write tests**

Test that:
- Session creates with scenario name and timestamp
- `add_entry()` records speaker, text, and timestamp
- `save_transcript()` writes a markdown file to the transcripts directory
- Transcript filename format: `{scenario}_{date}_{time}.md`
- Transcript content includes all entries in order

**Step 2: Implement**

```python
# phoneybaloney/session.py
"""Session management and transcript logging."""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class TranscriptEntry:
    timestamp: str
    speaker: str
    text: str


@dataclass
class Session:
    scenario_name: str
    started_at: datetime = field(default_factory=datetime.now)
    entries: list[TranscriptEntry] = field(default_factory=list)

    def add_entry(self, speaker: str, text: str) -> None:
        entry = TranscriptEntry(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            speaker=speaker,
            text=text,
        )
        self.entries.append(entry)

    def save_transcript(self, transcripts_dir: str) -> str:
        path = Path(transcripts_dir)
        path.mkdir(parents=True, exist_ok=True)
        filename = f"{self.scenario_name}_{self.started_at.strftime('%Y-%m-%d_%H%M%S')}.md"
        filepath = path / filename

        lines = [f"# {self.scenario_name} — Session Transcript", ""]
        lines.append(f"**Date:** {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        for entry in self.entries:
            lines.append(f"**[{entry.timestamp}] {entry.speaker}:** {entry.text}")
            lines.append("")

        filepath.write_text("\n".join(lines), encoding="utf-8")
        return str(filepath)
```

**Commit:** `"Add session manager with transcript logging"`

---

### Task 20: Conversation Engine

**Files:**
- Create: `phoneybaloney/engine.py`
- Create: `tests/test_engine.py`

This is the core brain. Tests should use mock providers (from Task 2 test patterns).

**Key responsibilities:**
- Load config, instantiate selected providers via registry
- Load scenario YAML
- `start_call()`: connect to starting_extension character, generate greeting
- `process_input()`: receive transcribed text, check for commands (dial extension / terminate), otherwise send to LLM
- `switch_character()`: change to new extension, clear conversation history, generate new greeting
- `end_call()`: save transcript, clean up
- Conversation history is per-call (fresh on every character switch)

**LLM message construction:**
```python
messages = [
    {"role": "system", "content": f"{scenario['global_prompt']} {character['prompt']}"},
    {"role": "user", "content": "*dials number*"},
]
# ... then append user/assistant messages as conversation progresses
```

**Command detection:**
- Regex for "dial extension XXX" (case insensitive)
- Regex for "terminate call" (case insensitive)

**Tests should cover:**
- Starting a call connects to starting_extension
- User input is sent to LLM and response returned
- "Dial Extension 100" switches character and clears history
- "Terminate Call" ends session
- Invalid extension returns error message
- Conversation history grows with each exchange
- History is cleared on character switch

**Commit:** `"Add conversation engine with command handling"`

---

### Task 21: Audio Playback Utility

**Files:**
- Create: `phoneybaloney/audio.py`
- Create: `tests/test_audio.py`

Shared utility for playing audio bytes through speakers. Used by the engine to play TTS output.

- `play_audio(audio_bytes: bytes) -> None` — plays WAV/MP3 audio bytes using pygame mixer
- `list_microphones() -> list[dict]` — returns available input devices
- `get_default_microphone() -> str` — returns default mic name

**Commit:** `"Add audio playback and microphone utilities"`

---

## Phase 4: Web UI

### Task 22: FastAPI Application Shell

**Files:**
- Create: `phoneybaloney/app.py`
- Create: `tests/test_app.py`

**Step 1: Write tests**

```python
# tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from phoneybaloney.app import create_app

def test_homepage_returns_200():
    app = create_app(config_path=None, test_mode=True)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200

def test_settings_page_returns_200():
    app = create_app(config_path=None, test_mode=True)
    client = TestClient(app)
    response = client.get("/settings")
    assert response.status_code == 200

def test_help_page_returns_200():
    app = create_app(config_path=None, test_mode=True)
    client = TestClient(app)
    response = client.get("/help")
    assert response.status_code == 200
```

**Step 2: Implement**

```python
# phoneybaloney/app.py
"""FastAPI web application."""
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

WEB_DIR = Path(__file__).parent / "web"
TEMPLATES = Jinja2Templates(directory=str(WEB_DIR / "templates"))


def create_app(config_path: str | None = None, test_mode: bool = False) -> FastAPI:
    app = FastAPI(title="PhoneyBaloney")
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")

    @app.get("/")
    async def home(request: Request):
        return TEMPLATES.TemplateResponse("home.html", {"request": request})

    @app.get("/settings")
    async def settings(request: Request):
        return TEMPLATES.TemplateResponse("settings.html", {"request": request})

    @app.get("/help")
    async def help_page(request: Request):
        return TEMPLATES.TemplateResponse("help.html", {"request": request})

    return app


def main():
    port = 8080
    print(f"\nPhoneyBaloney is running!")
    print(f"Open your browser to: http://localhost:{port}\n")
    webbrowser.open(f"http://localhost:{port}")
    uvicorn.run(create_app(), host="127.0.0.1", port=port)
```

Create minimal placeholder HTML templates for home, settings, help.

**Commit:** `"Add FastAPI application shell with routes"`

---

### Task 23: API Endpoints

**Files:**
- Modify: `phoneybaloney/app.py`
- Create: `tests/test_api.py`

REST API endpoints for the web UI to call:

```
GET  /api/status          — provider validation status (all green/red checks)
GET  /api/scenarios        — list available scenarios (metadata only)
GET  /api/config           — get current config
POST /api/config           — update config (saves to config.yaml)
GET  /api/voices           — list voices from active TTS provider
POST /api/validate/{type}  — validate a specific provider (llm/tts/stt)
GET  /api/microphones      — list available microphones
```

Each endpoint tested with FastAPI TestClient.

**Commit:** `"Add REST API endpoints for config, scenarios, and validation"`

---

### Task 24: WebSocket Session Endpoint

**Files:**
- Modify: `phoneybaloney/app.py`
- Create: `tests/test_websocket.py`

WebSocket endpoint for real-time session communication:

```
WS /ws/session?scenario={filename}
```

Messages from server to client:
- `{"type": "status", "status": "listening"}`
- `{"type": "status", "status": "thinking", "character": "Susan"}`
- `{"type": "status", "status": "speaking", "character": "Susan"}`
- `{"type": "transcript", "speaker": "Susan Daniels", "text": "MegaCorp, this is Susan..."}`
- `{"type": "transcript", "speaker": "You", "text": "Hi, I'm calling about..."}`
- `{"type": "audio", "data": "<base64 audio>"}`
- `{"type": "error", "message": "Extension not found"}`
- `{"type": "call_ended"}`

Messages from client to server:
- `{"type": "dial", "extension": "3100"}`
- `{"type": "end_call"}`
- `{"type": "mute", "muted": true}`

**Commit:** `"Add WebSocket endpoint for real-time session communication"`

---

### Task 25: HTML Templates — Home/Dashboard

**Files:**
- Create: `phoneybaloney/web/templates/base.html`
- Create: `phoneybaloney/web/templates/home.html`
- Create: `phoneybaloney/web/static/css/style.css`
- Create: `phoneybaloney/web/static/js/app.js`

Base template with nav bar (Home, Settings, Help). Dark theme, clean layout.

Home page:
- Provider status dashboard (green/red indicators)
- Scenario cards with metadata (company, description, difficulty, objective)
- "Start Call" button per scenario (disabled if providers not validated)

**Commit:** `"Add dashboard HTML template with provider status and scenario cards"`

---

### Task 26: HTML Templates — Settings Page

**Files:**
- Create: `phoneybaloney/web/templates/settings.html`
- Create: `phoneybaloney/web/static/js/settings.js`

Settings page:
- LLM provider dropdown + config fields + "Test Connection" button
- TTS provider dropdown + config fields + "Test Connection" button
- Voice browser with "Load Voices" → dropdown → "Play Sample"
- Voice mapping (male_default, female_default)
- STT provider dropdown + config fields + "Test Connection" button
- Microphone dropdown
- Save button (POSTs to /api/config)
- All fields show/hide based on selected provider
- Info (?) icons with explanations

**Commit:** `"Add settings page with provider configuration and voice browser"`

---

### Task 27: HTML Templates — Session Page

**Files:**
- Create: `phoneybaloney/web/templates/session.html`
- Create: `phoneybaloney/web/static/js/session.js`

Session page:
- Scenario metadata header
- Scrolling transcript area (chat-style)
- Status bar: "Listening...", "[Name] is thinking...", "[Name] is speaking..."
- Controls: mute/unmute, dial extension input + dial button, end call, volume slider
- WebSocket connection for real-time updates
- First-use overlay: "How This Works" (dismissible, "Don't show again" via localStorage)

**Commit:** `"Add session page with live transcript and WebSocket"`

---

### Task 28: HTML Templates — Help Page

**Files:**
- Create: `phoneybaloney/web/templates/help.html`

Static help content:
- What is vishing?
- How to use PhoneyBaloney
- Tips for beginners
- How to create your own scenarios
- How to add custom providers
- Troubleshooting common issues (mic not detected, Ollama not running, etc.)

**Commit:** `"Add help page with beginner documentation"`

---

### Task 29: First-Run Setup Wizard

**Files:**
- Create: `phoneybaloney/web/templates/wizard.html`
- Create: `phoneybaloney/web/static/js/wizard.js`
- Modify: `phoneybaloney/app.py` — add route and first-run detection

The wizard triggers when `config.yaml` does not exist or a `first_run: true` flag is set.

Steps:
1. Welcome + explain what PhoneyBaloney is
2. LLM setup (recommend Ollama, link to install, test connection)
3. TTS setup (pick tier, test voice)
4. STT + microphone setup (pick provider, test recording + playback)
5. Summary + "Start Your First Call"

After completion, sets `first_run: false` in config.

**Commit:** `"Add first-run setup wizard"`

---

## Phase 5: Installation & Packaging

### Task 30: Setup Script

**Files:**
- Create: `setup.py`

Cross-platform installer:
1. Detect OS
2. Check Python 3.10+
3. Create venv
4. Install base + LLM requirements
5. Platform-specific audio deps (PyAudio)
6. Interactive optional deps (Whisper, Coqui, Vosk)
7. Generate config.yaml from template
8. Create directories (scenarios, transcripts)
9. Run validation
10. Print OS-specific launch instructions

**Commit:** `"Add cross-platform setup script"`

---

### Task 31: Launcher Scripts

**Files:**
- Create: `start.bat`
- Create: `start.sh`

```bat
@echo off
call venv\Scripts\activate
python -m phoneybaloney
```

```bash
#!/bin/bash
source venv/bin/activate
python -m phoneybaloney
```

**Commit:** `"Add launcher scripts for Windows and Mac/Linux"`

---

### Task 32: Requirements Files

**Files:**
- Create: `requirements/base.txt`
- Create: `requirements/llm.txt`
- Create: `requirements/tts_free.txt`
- Create: `requirements/tts_coqui.txt`
- Create: `requirements/tts_cloud.txt`
- Create: `requirements/stt_whisper.txt`
- Create: `requirements/stt_vosk.txt`
- Create: `requirements/stt_cloud.txt`

Each file has pinned versions for reproducibility.

**Commit:** `"Add tiered requirements files"`

---

## Phase 6: Documentation

### Task 33: README

**Files:**
- Rewrite: `README.md`

Sections:
- What is PhoneyBaloney
- Quick Start (4 commands: clone, cd, setup, start)
- Platform-specific instructions (Windows, Mac, Linux) with clear headers
- Provider options overview (table: name, cost, quality, requirements)
- Screenshot/description of the web UI
- Creating your own scenarios
- Troubleshooting
- Contributing

**Commit:** `"Rewrite README with comprehensive documentation"`

---

### Task 34: Provider Development Guide

**Files:**
- Create: `docs/adding-providers.md`

Walkthrough:
1. Base class interface explanation
2. Step-by-step: create a new TTS provider
3. Registration
4. Testing
5. Template files reference

**Commit:** `"Add provider development guide"`

---

### Task 35: Config Reference

**Files:**
- Update: `config.example.yaml` — full comments matching design doc Section 3

Every option explained in plain English with links to get API keys.

**Commit:** `"Add fully documented config.example.yaml"`

---

## Phase 7: Integration & Polish

### Task 36: End-to-End Integration Test

**Files:**
- Create: `tests/test_integration.py`

Test the full flow with mock providers:
1. Load config → instantiate providers → load scenario
2. Start call → get greeting
3. Send user input → get LLM response
4. Dial extension → character switches, history clears
5. Terminate call → transcript saved

**Commit:** `"Add end-to-end integration test"`

---

### Task 37: Clean Up Old Code

**Files:**
- Delete or archive: `phoneybaloney.py` (original monolith)
- Update: `.gitignore` — add venv/, config.yaml, transcripts/*.md, __pycache__/

**Commit:** `"Remove original monolith, add .gitignore"`

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1-4 | Scaffolding, base classes, config, scenarios |
| 2 | 5-18 | All provider implementations (LLM, TTS, STT) |
| 3 | 19-21 | Session management, conversation engine, audio |
| 4 | 22-29 | Web UI (FastAPI, templates, WebSocket, wizard) |
| 5 | 30-32 | Setup script, launchers, requirements |
| 6 | 33-35 | README, docs, config reference |
| 7 | 36-37 | Integration testing, cleanup |
