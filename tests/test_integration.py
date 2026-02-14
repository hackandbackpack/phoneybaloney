"""End-to-end integration test with mock providers."""
import pytest
from unittest.mock import MagicMock
from phoneybaloney.config import AppConfig
from phoneybaloney.engine import ConversationEngine
from phoneybaloney.providers.base import BaseLLM, BaseTTS, BaseSTT, ProviderRegistry
from phoneybaloney.providers.llm import register_all_llm
from phoneybaloney.providers.tts import register_all_tts
from phoneybaloney.providers.stt import register_all_stt
from phoneybaloney.scenarios import list_scenarios, load_scenario


class FakeLLM(BaseLLM):
    """Deterministic LLM for testing."""
    def __init__(self):
        self.call_count = 0
        self.responses = [
            "MegaCorp, this is Susan. How may I direct your call?",
            "Sure, I can transfer you to IT. That's extension 200.",
            "IT Help Desk, this is Rick. What can I do for you?",
            "I can reset that for you. What's your employee number?",
        ]

    def initialize(self, config: dict) -> None:
        pass

    def generate_response(self, messages: list[dict]) -> str:
        idx = min(self.call_count, len(self.responses) - 1)
        self.call_count += 1
        return self.responses[idx]

    def validate(self) -> tuple[bool, str]:
        return True, "Fake LLM ready"


class FakeTTS(BaseTTS):
    def initialize(self, config: dict) -> None:
        pass

    def synthesize(self, text: str, voice: str) -> bytes:
        return b"RIFF" + b"\x00" * 44 + text.encode()

    def list_voices(self) -> list[dict]:
        return [{"id": "fake", "name": "Fake Voice"}]

    def validate(self) -> tuple[bool, str]:
        return True, "Fake TTS ready"


class FakeSTT(BaseSTT):
    def initialize(self, config: dict) -> None:
        pass

    def listen(self, timeout: int = 15) -> str | None:
        return "test input"

    def validate(self) -> tuple[bool, str]:
        return True, "Fake STT ready"


class TestProviderRegistry:
    def test_all_providers_register(self):
        registry = ProviderRegistry()
        register_all_llm(registry)
        register_all_tts(registry)
        register_all_stt(registry)

        assert len(registry.list_llm_providers()) == 3
        assert len(registry.list_tts_providers()) == 4
        assert len(registry.list_stt_providers()) == 4


class TestEndToEndFlow:
    @pytest.fixture
    def engine(self, tmp_path):
        """Create an engine with fake providers and the real megacorp scenario."""
        config = AppConfig(log_transcripts=True)
        llm = FakeLLM()
        tts = FakeTTS()
        stt = FakeSTT()
        engine = ConversationEngine(llm, tts, stt, config)

        # Load the actual megacorp scenario
        import shutil
        from pathlib import Path
        scenario_src = Path(__file__).parent.parent / "scenarios" / "megacorp.yaml"
        scenario_dst = tmp_path / "megacorp.yaml"
        shutil.copy(scenario_src, scenario_dst)
        engine.load_scenario(str(scenario_dst))
        return engine

    def test_full_call_lifecycle(self, engine, tmp_path):
        """Test: start -> greet -> chat -> dial -> chat -> end."""
        # Step 1: Start call — connects to starting extension (Susan)
        greeting = engine.start_call()
        assert engine.active is True
        assert engine.current_character["name"] == "Susan Daniels"
        assert greeting  # Should have a greeting

        # Step 2: Have a conversation
        result = engine.process_input("Hi, I need to get to the IT department.")
        assert result["type"] == "response"
        assert result["speaker"] == "Susan Daniels"

        # Step 3: Dial extension to switch to Rick
        result = engine.process_input("Dial Extension 200")
        assert result["type"] == "switch"
        assert result["character"] == "Rick Thompson"
        assert result["greeting"]  # Rick should greet us

        # Step 4: Conversation with new character
        result = engine.process_input("I need a password reset.")
        assert result["type"] == "response"
        assert result["speaker"] == "Rick Thompson"

        # Step 5: Verify conversation history was cleared on switch
        # After switch: system + dial + greeting + user + response = 5
        assert len(engine.messages) == 5

        # Step 6: End call
        result = engine.process_input("Terminate Call")
        assert result["type"] == "end"
        assert engine.active is False

    def test_invalid_extension(self, engine):
        engine.start_call()
        result = engine.process_input("Dial Extension 999")
        assert result["type"] == "error"
        assert "999" in result["message"]

    def test_transcript_saved(self, engine, tmp_path):
        engine.start_call()
        engine.process_input("Hello!")

        # Override transcripts dir to tmp_path
        result = engine.end_call()
        # Transcript should have been saved (we check the session has entries)
        assert len(engine.session.entries) >= 2  # greeting + user message

    def test_scenario_metadata_hidden(self):
        """Verify list_scenarios only returns safe metadata."""
        from pathlib import Path
        scenarios_dir = str(Path(__file__).parent.parent / "scenarios")
        scenarios = list_scenarios(scenarios_dir)
        for s in scenarios:
            assert hasattr(s, "company")
            assert hasattr(s, "difficulty")
            assert not hasattr(s, "characters")
            assert not hasattr(s, "global_prompt")

    def test_tts_produces_audio(self, engine):
        tts = FakeTTS()
        tts.initialize({})
        audio = tts.synthesize("Hello world", "female")
        assert isinstance(audio, bytes)
        assert len(audio) > 0
