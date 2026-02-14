import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.llm.openai_llm import OpenAILLM


class TestOpenAILLM:
    def test_initialize_stores_config(self):
        llm = OpenAILLM()
        llm.initialize({"api_key": "sk-test", "model": "gpt-4o"})
        assert llm.model == "gpt-4o"

    def test_initialize_defaults(self):
        llm = OpenAILLM()
        llm.initialize({})
        assert llm.model == "gpt-4o"

    @patch("phoneybaloney.providers.llm.openai_llm.openai")
    def test_generate_response(self, mock_openai):
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from GPT!"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response

        llm = OpenAILLM()
        llm.initialize({"api_key": "sk-test", "model": "gpt-4o"})
        result = llm.generate_response([{"role": "user", "content": "Hi"}])
        assert result == "Hello from GPT!"

    @patch("phoneybaloney.providers.llm.openai_llm.openai")
    def test_validate_success(self, mock_openai):
        mock_openai.OpenAI.return_value.models.list.return_value = MagicMock()

        llm = OpenAILLM()
        llm.initialize({"api_key": "sk-test"})
        success, msg = llm.validate()
        assert success is True

    @patch("phoneybaloney.providers.llm.openai_llm.openai")
    def test_validate_bad_key(self, mock_openai):
        mock_openai.OpenAI.return_value.models.list.side_effect = Exception("Invalid API key")

        llm = OpenAILLM()
        llm.initialize({"api_key": "bad-key"})
        success, msg = llm.validate()
        assert success is False
