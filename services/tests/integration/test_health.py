# tests/integration/test_health.py
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def test_all_services_are_up():
    """
    Teste que tous les services répondent /health
    → Attend jusqu'à 30 secondes que tout soit prêt (normal en CI)
    """
    session = requests.Session()
    retry = Retry(total=30, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retry))

    services = {
        "gateway": "http://localhost:8080/health",
        "auth": "http://localhost:8001/health",
        "project": "http://localhost:8002/health",
        "billing": "http://localhost:8003/health",
        "notification": "http://localhost:8004/health",
        "analytics": "http://localhost:8005/health",
    }

    for name, url in services.items():
        print(f"Vérification {name} → {url}")
        try:
            r = session.get(url, timeout=30)
            assert r.status_code == 200, f"{name} n'est pas prêt (code {r.status_code})"
            print(f"{name} est UP")
        except Exception as e:
            print(f"{name} a échoué : {e}")
            raise

    print("TOUS LES SERVICES SONT UP ET PRÊTS !")