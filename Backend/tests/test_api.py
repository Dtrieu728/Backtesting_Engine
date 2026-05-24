import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

def test_get_strategies():
    response = client.get("/api/strategies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(s["id"] == "long_only" for s in data)

def test_get_symbols():
    response = client.get("/api/symbols")
    assert response.status_code == 200
    assert "symbols" in response.json()

def test_get_history():
    response = client.get("/api/backtest/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_run_backtest_missing_symbols():
    response = client.post("/api/backtest", json={
        "symbols": [],
        "strategy": "long_only",
        "short_period": 20,
        "long_period": 50,
    })
    assert response.status_code == 422  # validation error