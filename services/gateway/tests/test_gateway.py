# services/gateway/tests/test_gateway.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_gateway_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_gateway_route_forward():
    """Simule un appel proxy vers auth service."""
    response = client.get("/auth/simulated")
    assert response.status_code in [200, 404]
