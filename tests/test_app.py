"""
tests/test_app.py

Basic FastAPI smoke tests for the Mergington High School API.
Uses AAA style and a fixture that restores the in-memory
`activities` dictionary between tests.
"""

import copy
import pytest
from fastapi.testclient import TestClient

# import the app and the mutable data structure
from src.app import app, activities as _activities


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Preserve the original activities dictionary and restore it
    after each test so tests don't bleed into one another.
    """
    original = copy.deepcopy(_activities)
    yield
    _activities.clear()
    _activities.update(copy.deepcopy(original))


@pytest.fixture
def client():
    """FastAPI TestClient for exercising the routes."""
    return TestClient(app)


def test_root_redirects_to_static(client):
    # Arrange: client fixture
    # Act
    resp = client.get("/")
    # Assert
    assert resp.status_code == 200
    assert "/static/index.html" in resp.url or "Mergington" in resp.text


def test_get_activities(client):
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "tester@example.com"
    # Act
    resp = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert
    assert resp.status_code == 200
    assert email in _activities[activity]["participants"]


def test_signup_duplicate(client):
    # Arrange
    activity = "Chess Club"
    existing = _activities[activity]["participants"][0]
    # Act
    resp = client.post(
        f"/activities/{activity}/signup", params={"email": existing}
    )
    # Assert
    assert resp.status_code == 400


def test_signup_nonexistent_activity(client):
    # Act
    resp = client.post(
        "/activities/NoSuchActivity/signup", params={"email": "x@y.com"}
    )
    # Assert
    assert resp.status_code == 404


def test_unregister_success(client):
    # Arrange
    activity = "Chess Club"
    email = _activities[activity]["participants"][0]
    # Act
    resp = client.delete(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert
    assert resp.status_code == 200
    assert email not in _activities[activity]["participants"]


def test_unregister_not_signed(client):
    # Act
    resp = client.delete(
        "/activities/Chess Club/signup", params={"email": "nobody@here"}
    )
    # Assert
    assert resp.status_code == 400


def test_unregister_nonexistent_activity(client):
    # Act
    resp = client.delete(
        "/activities/DoesntExist/signup", params={"email": "a@b.com"}
    )
    # Assert
    assert resp.status_code == 404
