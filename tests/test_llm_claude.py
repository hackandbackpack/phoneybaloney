import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.llm.claude_llm import ClaudeLLM


class TestClaudeLLM:
    def test_initialize_stores_config(self):
        llm = ClaudeLLM()
        llm.initialize({"api_key": "sk-ant-test", "model": "claude-sonnet-4-5-20250929"})
        assert llm.model == "claude-sonnet-4-5-20250929"

    @patch("phoneybaloney.providers.llm.claude_llm.anthropic")
    def test_generate_response(self, mock_anthropic):
        mock_block = MagicMock()
        mock_block.text = "Hello from Claude!"
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_response

        llm = ClaudeLLM()
        llm.initialize({"api_key": "sk-ant-test", "model": "claude-sonnet-4-5-20250929"})
        result = llm.generate_response([
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ])
        assert result == "Hello from Claude!"

    @patch("phoneybaloney.providers.llm.claude_llm.anthropic")
    def test_generate_response_extracts_system(self, mock_anthropic):
        """Claude API separates system prompt from messages."""
        mock_block = MagicMock()
        mock_block.text = "Response"
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        client_mock = mock_anthropic.Anthropic.return_value
        client_mock.messages.create.return_value = mock_response

        llm = ClaudeLLM()
        llm.initialize({"api_key": "sk-ant-test", "model": "claude-sonnet-4-5-20250929"})
        llm.generate_response([
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "Bye"},
        ])

        call_kwargs = client_mock.messages.create.call_args
        assert call_kwargs.kwargs["system"] == "System prompt"
        # Messages should not include the system message
        msgs = call_kwargs.kwargs["messages"]
        assert all(m["role"] != "system" for m in msgs)

    @patch("phoneybaloney.providers.llm.claude_llm.anthropic")
    def test_validate_success(self, mock_anthropic):
        mock_block = MagicMock()
        mock_block.text = "OK"
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_response

        llm = ClaudeLLM()
        llm.initialize({"api_key": "sk-ant-test"})
        success, msg = llm.validate()
        assert success is True

    @patch("phoneybaloney.providers.llm.claude_llm.anthropic")
    def test_validate_failure(self, mock_anthropic):
        mock_anthropic.Anthropic.return_value.messages.create.side_effect = Exception("Bad key")

        llm = ClaudeLLM()
        llm.initialize({"api_key": "bad"})
        success, msg = llm.validate()
        assert success is False
