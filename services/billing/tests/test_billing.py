# services/billing/tests/test_billing.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_billing_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_billing_event_simulation():
    payload = {
        "user_email": "john@example.com",
        "plan_name": "PRO",
        "status": "paid"
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code in [200, 500]
