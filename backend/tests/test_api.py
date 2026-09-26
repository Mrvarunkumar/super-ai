"""
Basic smoke tests. Run with: pytest tests/test_api.py
Note: /chat requires a valid ANTHROPIC_API_KEY in the environment.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200


def test_status():
    resp = client.get("/status")
    assert resp.status_code == 200
    body = resp.json()
    assert "cpu_percent" in body


def test_create_and_list_task():
    resp = client.post("/tasks", json={"title": "Test task", "steps": ["step one", "step two"]})
    assert resp.status_code == 200
    task = resp.json()
    assert task["title"] == "Test task"

    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert any(t["id"] == task["id"] for t in resp.json())


def test_command_requires_confirmation_for_sensitive_action():
    resp = client.post("/command", json={"tool": "shutdown_computer", "arguments": {}, "confirm": False})
    assert resp.status_code == 200
    body = resp.json()
    assert body["requires_confirmation"] is True


def test_memory_roundtrip():
    resp = client.post("/memory", json={"key": "test_key", "value": "test_value"})
    assert resp.status_code == 200
    resp = client.get("/memory")
    assert resp.json().get("test_key") == "test_value"
