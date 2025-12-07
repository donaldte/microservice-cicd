# services/analytics/app/main.py
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import os

# ============================================================
# Analytics Service – SANS KAFKA (compatible CI + prod sans Kafka)
# ============================================================

app = FastAPI(title="Analytics Service")

Instrumentator().instrument(app).expose(app)  

# Métriques simulées (elles restent même sans Kafka)
fake_metrics = {
    "active_users": 12,
    "projects_created": 34,
    "billing_events": 0
}

# Optionnel : tu pourras réactiver Kafka plus tard avec une variable d’environnement
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"


# ============================================================
# Consumer Kafka → désactivé proprement si Kafka n’est pas actif
# ============================================================
if KAFKA_ENABLED:
    from aiokafka import AIOKafkaConsumer
    import json
    import asyncio

    async def consume_billing_events():
        consumer = AIOKafkaConsumer(
            "billing.events",
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            group_id="analytics-group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        await consumer.start()
        try:
            async for msg in consumer:
                fake_metrics["billing_events"] += 1
                print("ANALYTICS UPDATED → ", fake_metrics)
        finally:
            await consumer.stop()

    @app.on_event("startup")
    async def start_kafka_consumer():
        asyncio.create_task(consume_billing_events())
else:
    print("Kafka désactivé (KAFKA_ENABLED=false ou absent) → mode mock activé")




# ============================================================
# Endpoints publics
# ============================================================
@app.get("/metrics/app")
def app_metrics():
    return fake_metrics


@app.get("/health")
def health():
    return {"status": "ok", "service": "analytics"}


@app.get("/events/count")
def count_events():
    return {"count": fake_metrics["billing_events"]}


# Bonus : endpoint pour simuler un événement (utile en dev/test)
@app.post("/simulate/billing-event")
def simulate_event():
    fake_metrics["billing_events"] += 1
    return {"status": "event_simulated", "new_count": fake_metrics["billing_events"]}