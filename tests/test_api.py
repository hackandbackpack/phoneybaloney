import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from phoneybaloney.app import create_app


@pytest.fixture
def client():
    app = create_app(config_path=None, test_mode=True)
    return TestClient(app)


class TestAPIScenarios:
    def test_list_scenarios(self, client):
        response = client.get("/api/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find at least the megacorp scenario
        names = [s["company"] for s in data]
        assert "MegaCorp" in names

    def test_scenario_metadata_only(self, client):
        response = client.get("/api/scenarios")
        data = response.json()
        for scenario in data:
            assert "company" in scenario
            assert "difficulty" in scenario
            assert "characters" not in scenario
            assert "global_prompt" not in scenario


class TestAPIMicrophones:
    def test_microphones_endpoint(self, client):
        response = client.get("/api/microphones")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAPIConfig:
    def test_get_config(self, client):
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_save_config(self, client, tmp_path):
        with patch("phoneybaloney.app.CONFIG_PATH", str(tmp_path / "config.yaml")):
            response = client.post("/api/config", json={
                "llm_provider": "ollama",
                "tts_provider": "pyttsx3",
                "stt_provider": "whisper_local",
            })
            assert response.status_code == 200
            assert response.json()["ok"] is True


class TestAPIValidation:
    def test_validate_endpoint(self, client):
        response = client.post("/api/validate/llm")
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data
        assert "message" in data
