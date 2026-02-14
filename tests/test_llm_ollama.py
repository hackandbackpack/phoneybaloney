import pytest
from unittest.mock import patch, MagicMock
from phoneybaloney.providers.llm.ollama import OllamaLLM


class TestOllamaLLM:
    def test_initialize_stores_config(self):
        llm = OllamaLLM()
        llm.initialize({"model": "llama3", "url": "http://localhost:11434"})
        assert llm.model == "llama3"
        assert llm.url == "http://localhost:11434"

    def test_initialize_defaults(self):
        llm = OllamaLLM()
        llm.initialize({})
        assert llm.model == "llama3"
        assert llm.url == "http://localhost:11434"

    @patch("phoneybaloney.providers.llm.ollama.requests")
    def test_generate_response(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"role": "assistant", "content": "Hello there!"}
        }
        mock_requests.post.return_value = mock_response

        llm = OllamaLLM()
        llm.initialize({"model": "llama3", "url": "http://localhost:11434"})
        result = llm.generate_response([
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ])
        assert result == "Hello there!"
        mock_requests.post.assert_called_once()

    @patch("phoneybaloney.providers.llm.ollama.requests")
    def test_validate_success(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama3:latest"}]}
        mock_requests.get.return_value = mock_response

        llm = OllamaLLM()
        llm.initialize({"model": "llama3"})
        success, msg = llm.validate()
        assert success is True

    @patch("phoneybaloney.providers.llm.ollama.requests")
    def test_validate_not_reachable(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError("refused")

        llm = OllamaLLM()
        llm.initialize({"model": "llama3"})
        success, msg = llm.validate()
        assert success is False
        assert "not reachable" in msg.lower() or "refused" in msg.lower()
