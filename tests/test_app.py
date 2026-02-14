import pytest
from fastapi.testclient import TestClient
from phoneybaloney.app import create_app


@pytest.fixture
def client():
    app = create_app(config_path=None, test_mode=True)
    return TestClient(app)


def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_settings_page_returns_200(client):
    response = client.get("/settings")
    assert response.status_code == 200


def test_help_page_returns_200(client):
    response = client.get("/help")
    assert response.status_code == 200


def test_session_page_returns_200(client):
    response = client.get("/session")
    assert response.status_code == 200


def test_wizard_page_returns_200(client):
    response = client.get("/wizard")
    assert response.status_code == 200
