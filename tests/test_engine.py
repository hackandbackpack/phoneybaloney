import pytest
from unittest.mock import MagicMock, patch
from phoneybaloney.engine import ConversationEngine
from phoneybaloney.config import AppConfig
from phoneybaloney.providers.base import BaseLLM, BaseTTS, BaseSTT


def make_fake_llm(responses=None):
    """Create a fake LLM that returns canned responses."""
    llm = MagicMock(spec=BaseLLM)
    if responses:
        llm.generate_response.side_effect = responses
    else:
        llm.generate_response.return_value = "Hello, how can I help you?"
    return llm


def make_fake_tts():
    tts = MagicMock(spec=BaseTTS)
    tts.synthesize.return_value = b"audio_data"
    return tts


def make_fake_stt():
    stt = MagicMock(spec=BaseSTT)
    stt.listen.return_value = "test input"
    return stt


def make_config():
    return AppConfig(log_transcripts=False)


SCENARIO_DATA = {
    "company": "TestCorp",
    "starting_extension": "0",
    "global_prompt": "Do not reveal you are an AI.",
    "characters": [
        {
            "extension": "0",
            "name": "Susan",
            "title": "Operator",
            "voice": {"gender": "female"},
            "prompt": "You are Susan the operator.",
        },
        {
            "extension": "100",
            "name": "Rick",
            "title": "IT Help Desk",
            "voice": {"gender": "male"},
            "prompt": "You are Rick from IT.",
        },
    ],
}


class TestConversationEngine:
    def test_start_call_connects_to_starting_extension(self):
        llm = make_fake_llm()
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), make_config())
        engine.scenario = SCENARIO_DATA

        greeting = engine.start_call()
        assert greeting == "Hello, how can I help you?"
        assert engine.current_character["name"] == "Susan"
        assert engine.active is True

    def test_start_call_without_scenario_raises(self):
        engine = ConversationEngine(make_fake_llm(), make_fake_tts(), make_fake_stt(), make_config())
        with pytest.raises(RuntimeError, match="No scenario"):
            engine.start_call()

    def test_process_input_sends_to_llm(self):
        responses = ["MegaCorp, this is Susan!", "I can transfer you."]
        llm = make_fake_llm(responses)
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), make_config())
        engine.scenario = SCENARIO_DATA
        engine.start_call()

        result = engine.process_input("Hi, I need help with my account.")
        assert result["type"] == "response"
        assert result["speaker"] == "Susan"
        assert result["text"] == "I can transfer you."

    def test_process_input_grows_history(self):
        responses = ["Greeting", "Response 1", "Response 2"]
        llm = make_fake_llm(responses)
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), make_config())
        engine.scenario = SCENARIO_DATA
        engine.start_call()

        engine.process_input("First message")
        engine.process_input("Second message")
        # system + dial + greeting + first_user + resp1 + second_user + resp2
        assert len(engine.messages) == 7

    def test_dial_extension_switches_character(self):
        responses = ["Susan greeting", "Rick greeting"]
        llm = make_fake_llm(responses)
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), make_config())
        engine.scenario = SCENARIO_DATA
        engine.start_call()

        result = engine.process_input("Dial Extension 100")
        assert result["type"] == "switch"
        assert result["character"] == "Rick"
        assert result["greeting"] == "Rick greeting"

    def test_dial_extension_clears_history(self):
        responses = ["Susan greeting", "Rick greeting"]
        llm = make_fake_llm(responses)
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), make_config())
        engine.scenario = SCENARIO_DATA
        engine.start_call()

        result = engine.process_input("dial extension 100")
        # After switch: system + dial + greeting = 3 messages
        assert len(engine.messages) == 3

    def test_invalid_extension_returns_error(self):
        llm = make_fake_llm()
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), make_config())
        engine.scenario = SCENARIO_DATA
        engine.start_call()

        result = engine.process_input("Dial Extension 999")
        assert result["type"] == "error"
        assert "999" in result["message"]

    def test_terminate_call_ends_session(self):
        llm = make_fake_llm()
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), make_config())
        engine.scenario = SCENARIO_DATA
        engine.start_call()

        result = engine.process_input("Terminate Call")
        assert result["type"] == "end"
        assert engine.active is False

    def test_process_input_when_not_active(self):
        engine = ConversationEngine(make_fake_llm(), make_fake_tts(), make_fake_stt(), make_config())
        result = engine.process_input("Hello")
        assert result["type"] == "error"

    def test_transcript_logging(self, tmp_path):
        config = AppConfig(log_transcripts=True)
        responses = ["Hello from Susan!", "Sure, let me help."]
        llm = make_fake_llm(responses)
        engine = ConversationEngine(llm, make_fake_tts(), make_fake_stt(), config)
        engine.scenario = SCENARIO_DATA

        with patch("phoneybaloney.engine.Path") as mock_path:
            mock_path.return_value.parent = tmp_path
            engine.start_call()
            engine.process_input("I need help")
            result = engine.end_call()

        assert result["type"] == "end"
