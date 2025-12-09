# gateway/app/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource


def setup_tracing(service_name: str):
    # Nom du service visible dans Jaeger
    resource = Resource(attributes={"service.name": service_name})

    # Provider global
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Exporter Thrift → compatible 100% avec jaegertracing/all-in-one
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",   # ← nom du service dans Docker/Swarm
        agent_port=6831,            # ← port Thrift (UDP) par défaut
    )

    processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(processor)

    return trace.get_tracer(service_name)