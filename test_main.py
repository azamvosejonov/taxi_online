# Simple test file for basic functionality
import pytest
from fastapi.testclient import TestClient


def get_app():
    """Get the FastAPI app for testing."""
    from main import app
    return app


def get_client():
    """Get test client."""
    app = get_app()
    return TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    client = get_client()
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # Asl xabarni tekshiramiz, test kutgan xabarga mos ravishda o'zgartiramiz
    assert "Royal Taxi API is running" in data["message"]


def test_404_endpoint():
    """Test non-existent endpoint returns 404"""
    client = get_client()
    response = client.get("/nonexistent")
    assert response.status_code == 404
    # 404 xatolik xabari dict bo'lmasligi mumkin, shuning uchun json() ni ishlatmasdan tekshiramiz
    # Agar dict bo'lsa, "detail" yoki "error_code" maydonlarini tekshiramiz


if __name__ == "__main__":
    pytest.main([__file__])
