# services/analytics/tests/test_analytics.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analytics_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_analytics_simulated():
    response = client.get("/events/count")
    assert response.status_code in [200, 404]
