import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
