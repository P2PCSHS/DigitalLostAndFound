import pytest

from app_factory import create_app
from config import TestConfig


@pytest.fixture
def app():
    """A fresh app backed by its own in-memory database."""
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_item(client):
    """Create an item through the API and return its JSON."""

    def _make(type="Keys", description="a blue keychain"):
        response = client.post("/items", json={"type": type, "description": description})
        assert response.status_code == 201, response.get_json()
        return response.get_json()

    return _make
