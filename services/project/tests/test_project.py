# services/project/tests/test_project.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_project_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_create_project_simulation():
    payload = {"name": "Test Project"}
    response = client.post("/projects", json=payload)
    assert response.status_code in [200, 201, 400]
