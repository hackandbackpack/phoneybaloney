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
