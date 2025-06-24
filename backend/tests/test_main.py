"""
Basic tests for the FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_metrics_endpoint():
    """Test the metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Metrics should be in Prometheus format
    assert "http_requests_total" in response.text


def test_api_docs():
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_app_startup():
    """Test that the FastAPI app starts up correctly."""
    # This test ensures the app configuration is valid
    assert app is not None
    assert app.title == "WageLift API" 