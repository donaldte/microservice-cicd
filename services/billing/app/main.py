# services/billing/app/main.py
import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

# Imports conditionnels (ne plantent pas si Kafka est désactivé)
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

if KAFKA_ENABLED:
    from aiokafka import AIOKafkaProducer
    from opentelemetry.instrumentation.aiokafka import AIOKafkaInstrumentor

# Imports toujours nécessaires
try:
    from .tracing import setup_tracing
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:
    # En cas de mock ou de module manquant (CI), on passe
    def setup_tracing(*args, **kwargs):
        return None
    FastAPIInstrumentor = None


app = FastAPI(title="Billing Service")
Instrumentator().instrument(app).expose(app)

tracer = setup_tracing("billing-service")
if FastAPIInstrumentor:
    FastAPIInstrumentor.instrument_app(app)


# ============================================================
# Producteur Kafka – activé seulement si KAFKA_ENABLED=true
# ============================================================
producer = None

if KAFKA_ENABLED:
    AIOKafkaInstrumentor().instrument()

    @app.on_event("startup")
    async def start_kafka_producer():
        global producer
        bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await producer.start()
        print(f"Kafka producer démarré → {bootstrap}")

    @app.on_event("shutdown")
    async def stop_kafka_producer():
        global producer
        if producer:
            await producer.stop()
            print("Kafka producer arrêté")
else:
    print("Kafka désactivé (KAFKA_ENABLED=false) → mode mock activé")


# ============================================================
# Modèle et endpoint
# ============================================================
class BillingEvent(BaseModel):
    user_email: str
    plan_name: str
    status: str


@app.post("/webhook")
async def webhook(event: BillingEvent):
    payload = {
        "email": event.user_email,
        "plan": event.plan_name,
        "status": event.status
    }

    if KAFKA_ENABLED and producer:
        with tracer.start_as_current_span("produce-billing-event"):
            await producer.send_and_wait("billing.events", payload)
        return {"message": "billing event produced to Kafka"}
    else:
        # Mode mock → on simule juste l’envoi
        print("MOCK KAFKA → billing event:", payload)
        return {"message": "billing event simulated (Kafka disabled)"}


# ============================================================
# Health check
# ============================================================
@app.get("/health")
def health():
    return {"status": "ok", "service": "billing"}


# Bonus : endpoint pour tester manuellement
@app.post("/simulate")
def simulate():
    return {"message": "simulation mode – Kafka is disabled"}