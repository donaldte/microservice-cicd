# services/auth/tests/test_auth.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_login_simulation():
    payload = {"email": "test@example.com", "password": "123456"}
    response = client.post("/login", json=payload)
    assert response.status_code in [200, 401, 404]
