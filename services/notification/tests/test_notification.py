# services/notification/tests/test_notification.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_notification_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_send_email_simulation():
    payload = {"email": "john@example.com", "subject": "Test", "message": "Hello!"}
    response = client.post("/send", json=payload)
    assert response.status_code in [200, 400, 404]
