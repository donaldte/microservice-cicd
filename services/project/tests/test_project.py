# services/project/tests/test_project.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_project_health():
    response = client.get("/health")
    assert response.status_code == 200


