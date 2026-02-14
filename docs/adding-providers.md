# Adding Custom Providers

PhoneyBaloney uses a plugin-based provider system. You can add your own LLM, TTS, or STT providers by implementing a simple interface.

## Overview

Each provider type has an abstract base class in `phoneybaloney/providers/base.py`:

- **BaseLLM** — Conversation intelligence
- **BaseTTS** — Voice output (text-to-speech)
- **BaseSTT** — Voice input (speech-to-text)

## Step-by-Step: Adding a New TTS Provider

This walkthrough creates a fictional "AcmeTTS" provider. The same pattern applies to LLM and STT providers.

### 1. Create the provider file

Create `phoneybaloney/providers/tts/acme_tts.py`:

```python
"""Acme TTS provider — example custom provider."""
from phoneybaloney.providers.base import BaseTTS


class AcmeTTS(BaseTTS):
    """TTS provider using Acme's API."""

    def initialize(self, config: dict) -> None:
        """Called once with the provider's config section from config.yaml."""
        self.api_key = config.get("api_key", "")
        self.voice_map = config.get("voice_map", {})

    def synthesize(self, text: str, voice: str) -> bytes:
        """Convert text to audio bytes (WAV format).

        Args:
            text: The text to speak.
            voice: Voice identifier from the voice_map config.

        Returns:
            Audio data as bytes.
        """
        voice_id = self.voice_map.get(voice, voice)
        # Call your API here and return audio bytes
        # Example:
        # response = requests.post("https://api.acme.com/tts", ...)
        # return response.content
        raise NotImplementedError("Replace with your API call")

    def list_voices(self) -> list[dict]:
        """Return available voices.

        Each voice should be a dict with at least 'id' and 'name'.
        Optional: 'gender', 'language', 'preview_url'.
        """
        # Example:
        # response = requests.get("https://api.acme.com/voices", ...)
        # return [{"id": v["id"], "name": v["name"]} for v in response.json()]
        return []

    def validate(self) -> tuple[bool, str]:
        """Test that the provider works.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Make a lightweight API call to verify the key works
            voices = self.list_voices()
            if voices:
                return True, f"Acme TTS connected, {len(voices)} voices"
            return False, "Acme TTS: no voices found"
        except Exception as e:
            return False, f"Acme TTS error: {e}"
```

### 2. Register the provider

Edit `phoneybaloney/providers/tts/__init__.py` and add your import and registration:

```python
from phoneybaloney.providers.tts.acme_tts import AcmeTTS

def register_all_tts(registry: ProviderRegistry) -> None:
    # ... existing registrations ...
    registry.register_tts("acme", AcmeTTS)
```

### 3. Add config section

Add your provider's config to `config.example.yaml`:

```yaml
# Acme TTS — Custom provider
acme:
  api_key: ""
  voice_map:
    female_default: ""
    male_default: ""
```

Users select it by setting `tts_provider: acme` in their `config.yaml`.

### 4. Write tests

Create `tests/test_tts_acme.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.tts.acme_tts import AcmeTTS


class TestAcmeTTS:
    def test_initialize(self):
        tts = AcmeTTS()
        tts.initialize({"api_key": "test-key"})
        assert tts.api_key == "test-key"

    def test_validate_success(self):
        tts = AcmeTTS()
        tts.initialize({"api_key": "test-key"})
        # Mock your API calls
        with patch.object(tts, 'list_voices', return_value=[{"id": "v1", "name": "Voice 1"}]):
            success, msg = tts.validate()
            assert success is True
```

Run tests: `python -m pytest tests/test_tts_acme.py -v`

## LLM Provider Interface

```python
class BaseLLM:
    def initialize(self, config: dict) -> None: ...
    def generate_response(self, messages: list[dict]) -> str: ...
    def validate(self) -> tuple[bool, str]: ...
```

The `messages` parameter follows the OpenAI format:
```python
[
    {"role": "system", "content": "System prompt"},
    {"role": "user", "content": "User message"},
    {"role": "assistant", "content": "Previous response"},
]
```

## STT Provider Interface

```python
class BaseSTT:
    def initialize(self, config: dict) -> None: ...
    def listen(self, timeout: int = 15) -> str | None: ...
    def validate(self) -> tuple[bool, str]: ...
```

The `listen` method should:
1. Record audio from the microphone
2. Transcribe it to text
3. Return the text, or `None` if nothing was understood

## Tips

- Use `unittest.mock.patch` in tests to avoid real API calls
- Handle import errors gracefully for optional dependencies
- Return descriptive validation messages — they're shown in the UI
- Voice mapping (gender -> voice ID) should go in config.yaml, not hardcoded
