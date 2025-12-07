# services/notification/app/main.py (ou analytics – même fichier)
import os
import json
import asyncio
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# ============================================================
# Configuration globale
# ============================================================
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

# Imports conditionnels – ne plantent jamais même si Kafka est désactivé
if KAFKA_ENABLED:
    from aiokafka import AIOKafkaConsumer
    from opentelemetry.instrumentation.aiokafka import AIOKafkaInstrumentor

# Imports avec fallback (au cas où tracing n'existe pas)
try:
    from .tracing import setup_tracing
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:
    def setup_tracing(*args, **kwargs):
        return None
    FastAPIInstrumentor = None


app = FastAPI(title="Notification Service")  # ou "Analytics Service"
Instrumentator().instrument(app).expose(app)  

# ============================================================
# Initialisation du tracing et observabilité
# ============================================================
tracer = setup_tracing("notification-service")  # ou "analytics-service"

if FastAPIInstrumentor:
    FastAPIInstrumentor.instrument_app(app)




# ============================================================
# Consumer Kafka – activé seulement si KAFKA_ENABLED=true
# ============================================================
fake_metrics = {
    "active_users": 12,
    "projects_created": 34,
    "billing_events": 0
}

if KAFKA_ENABLED:
    # Instrumentation OpenTelemetry pour Kafka
    AIOKafkaInstrumentor().instrument()

    async def consume_billing_events():
        bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        consumer = AIOKafkaConsumer(
            "billing.events",
            bootstrap_servers=bootstrap,
            group_id="notification-group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        await consumer.start()
        print(f"Kafka consumer démarré → {bootstrap}")
        try:
            async for msg in consumer:
                with tracer.start_as_current_span("process-billing-event"):
                    fake_metrics["billing_events"] += 1
                    print("NOTIFICATION / ANALYTICS → événement reçu :", msg.value)
                    print("Métriques mises à jour →", fake_metrics)
        finally:
            await consumer.stop()
            print("Kafka consumer arrêté")

    @app.on_event("startup")
    async def start_kafka_consumer():
        asyncio.create_task(consume_billing_events())
else:
    print("Kafka désactivé → mode simulation activé (métriques statiques)")


# ============================================================
# Endpoints publics
# ============================================================
@app.get("/metrics/app")
def app_metrics():
    return fake_metrics


@app.get("/health")
def health():
    return {"status": "ok", "service": "notification"}  # ou "analytics"


@app.get("/events/count")
def count_events():
    return {"count": fake_metrics["billing_events"]}


# Bonus : endpoint pour simuler un événement (très utile en dev/test)
@app.post("/simulate/event")
def simulate_billing_event():
    fake_metrics["billing_events"] += 1
    print("SIMULATION → événement billing reçu (Kafka désactivé)")
    return {
        "message": "event simulated",
        "new_count": fake_metrics["billing_events"]
    }